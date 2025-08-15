#!/usr/bin/env python3
"""
FastAPI Backend for Memory Systems Demo
Provides REST endpoints for Mem0 and Zep memory integrations
"""

import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Memory system imports
from mem0 import MemoryClient
from zep_cloud import AsyncZep
from zep_cloud.types import Message

app = FastAPI(title="Memory Systems Demo API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    user_id: str
    query: str

class QueryResponse(BaseModel):
    response: str
    memory_saved: bool
    context_found: bool = False
    retrieved_memory: Optional[list[str]] = None

# Global clients - initialize once
llm = None
mem0_client = None
zep_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize clients on startup"""
    global llm, mem0_client, zep_client
    
    # Check environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    if not os.environ.get("MEM0_API_KEY"):
        raise RuntimeError("MEM0_API_KEY environment variable not set")
    if not os.environ.get("ZEP_API_KEY"):
        raise RuntimeError("ZEP_API_KEY environment variable not set")
    
    # Initialize clients
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    mem0_client = MemoryClient(
        api_key=os.environ.get("MEM0_API_KEY")
    )
    
    zep_client = AsyncZep(
        api_key=os.environ.get("ZEP_API_KEY")
    )

# Common prompt template
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""You are a helpful assistant with access to conversation history.
    Use the provided context from previous interactions to give personalized responses.
    If context is relevant, reference it naturally in your response."""),
    MessagesPlaceholder(variable_name="context"),
    MessagesPlaceholder(variable_name="messages")
])

@app.post("/mem0/query", response_model=QueryResponse)
async def mem0_query(request: QueryRequest):
    """
    Process query using Mem0 for memory management
    """
    try:
        # Retrieve context from Mem0
        context_messages = []
        context_found = False
        retrieved_memory_parts = []
        
        memories = mem0_client.search(query=request.query, user_id=request.user_id, limit=5)
        
        if memories:
            context_found = True
            for memory in memories:
                memory_content = memory.get('memory', '')
                retrieved_memory_parts.append(memory_content)
                context_messages.append(
                    SystemMessage(content=f"Previous context: {memory_content}")
                )
        
        # Generate response
        chain = prompt | llm
        response = chain.invoke({
            "context": context_messages,
            "messages": [HumanMessage(content=request.query)]
        })
        
        # Save interaction to Mem0
        messages = [
            {"role": "user", "content": request.query},
            {"role": "assistant", "content": response.content}
        ]
        mem0_client.add(messages, user_id=request.user_id)
        
        return QueryResponse(
            response=response.content,
            memory_saved=True,
            context_found=context_found,
            retrieved_memory=retrieved_memory_parts if retrieved_memory_parts else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Mem0 query: {str(e)}")

@app.post("/zep/query", response_model=QueryResponse)
async def zep_query(request: QueryRequest):
    """
    Process query using Zep for memory management
    """
    try:
        # Ensure user exists in Zep
        await ensure_zep_user(request.user_id)
        
        # Create a new thread for this session
        thread_id = f"{request.user_id}_thread_{uuid.uuid4().hex[:8]}"
        await zep_client.thread.create(
            thread_id=thread_id,
            user_id=request.user_id
        )
        
        # Retrieve context from Zep graph
        context_messages = []
        context_found = False
        retrieved_memory_parts = []
        
        try:
            search_results = await zep_client.graph.search(
                user_id=request.user_id,
                query=request.query,
                limit=5,
                scope="edges"
            )
            
            if search_results and search_results.edges:
                context_found = True
                context_parts = []
                for edge in search_results.edges:
                    fact = edge.fact if hasattr(edge, 'fact') else str(edge)
                    context_parts.append(fact)
                    retrieved_memory_parts.append(fact)
                
                if context_parts:
                    combined_context = "\n".join(context_parts)
                    context_messages.append(
                        SystemMessage(content=f"Previous context from knowledge graph:\n{combined_context}")
                    )
        except Exception as search_error:
            # Continue without context if search fails
            pass
        
        # Generate response
        chain = prompt | llm
        response = chain.invoke({
            "context": context_messages,
            "messages": [HumanMessage(content=request.query)]
        })
        
        # Save interaction to Zep
        messages = [
            Message(
                name=request.user_id,
                role="user",
                content=request.query
            ),
            Message(
                name="Assistant",
                role="assistant",
                content=response.content
            )
        ]
        
        await zep_client.thread.add_messages(
            thread_id=thread_id,
            messages=messages
        )
        
        return QueryResponse(
            response=response.content,
            memory_saved=True,
            context_found=context_found,
            retrieved_memory=retrieved_memory_parts if retrieved_memory_parts else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Zep query: {str(e)}")

async def ensure_zep_user(user_id: str):
    """Ensure user exists in Zep, create if not"""
    try:
        await zep_client.user.get(user_id)
    except Exception as e:
        if "not found" in str(e).lower():
            await zep_client.user.add(
                user_id=user_id,
                email=f"{user_id}@example.com",
                first_name="Demo",
                last_name="User"
            )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "memory-systems-demo"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Memory Systems Demo API",
        "version": "1.0.0",
        "endpoints": {
            "/mem0/query": "Query using Mem0 memory system",
            "/zep/query": "Query using Zep memory system",
            "/health": "Health check"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)