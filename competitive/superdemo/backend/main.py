#!/usr/bin/env python3
"""
FastAPI Backend for Memory Systems Demo
Provides REST endpoints for Mem0 and Zep memory integrations
"""

import os
import uuid
import time
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import asyncio

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

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
    performance_metrics: Optional[Dict[str, float]] = None

# Global clients - initialize once
llm = None
mem0_client = None
zep_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize clients on startup"""
    global llm, mem0_client, zep_client
    
    print(f"Loading environment from: {env_path}")
    
    # Check environment variables
    openai_key = os.environ.get("OPENAI_API_KEY")
    mem0_key = os.environ.get("MEM0_API_KEY")
    zep_key = os.environ.get("ZEP_API_KEY")
    
    if not openai_key:
        print("WARNING: OPENAI_API_KEY not set")
        openai_key = "sk-mock-key-for-demo"
    else:
        print("✓ OPENAI_API_KEY loaded")
        
    if not mem0_key:
        print("WARNING: MEM0_API_KEY not set")
        mem0_key = "mock-mem0-key"
    else:
        print("✓ MEM0_API_KEY loaded")
        
    if not zep_key:
        print("WARNING: ZEP_API_KEY not set")
        zep_key = "mock-zep-key"
    else:
        print("✓ ZEP_API_KEY loaded")
    
    # Initialize clients (will fail on actual API calls if keys are invalid)
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=openai_key
        )
    except Exception as e:
        print(f"WARNING: Failed to initialize OpenAI client: {e}")
        llm = None
    
    try:
        mem0_client = MemoryClient(
            api_key=mem0_key
        )
    except Exception as e:
        print(f"WARNING: Failed to initialize Mem0 client: {e}")
        mem0_client = None
    
    try:
        zep_client = AsyncZep(
            api_key=zep_key
        )
    except Exception as e:
        print(f"WARNING: Failed to initialize Zep client: {e}")
        zep_client = None

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
    if not mem0_client or not llm:
        # Return mock response if clients not initialized
        return QueryResponse(
            response="Mock response: Memory system not connected. Please configure API keys.",
            memory_saved=False,
            context_found=False,
            retrieved_memory=None,
            performance_metrics={
                "search_time_ms": 10.5,
                "chain_invoke_time_ms": 250.3,
                "add_time_ms": 15.2,
                "total_time_ms": 276.0
            }
        )
    
    try:
        # Initialize performance metrics
        perf_metrics = {}
        
        # Retrieve context from Mem0
        context_messages = []
        context_found = False
        retrieved_memory_parts = []
        
        # Performance counter for mem0_client.search
        search_start = time.time()
        memories = mem0_client.search(query=request.query, user_id=request.user_id, limit=5)
        search_end = time.time()
        perf_metrics['search_time_ms'] = (search_end - search_start) * 1000
        
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
        
        # Performance counter for chain.invoke
        invoke_start = time.time()
        response = chain.invoke({
            "context": context_messages,
            "messages": [HumanMessage(content=request.query)]
        })
        invoke_end = time.time()
        perf_metrics['chain_invoke_time_ms'] = (invoke_end - invoke_start) * 1000
        
        # Save interaction to Mem0
        messages = [
            {"role": "user", "content": request.query},
            {"role": "assistant", "content": response.content}
        ]
        
        # Performance counter for mem0_client.add
        add_start = time.time()
        mem0_client.add(messages, user_id=request.user_id)
        add_end = time.time()
        perf_metrics['add_time_ms'] = (add_end - add_start) * 1000
        
        # Calculate total time
        perf_metrics['total_time_ms'] = perf_metrics['search_time_ms'] + perf_metrics['chain_invoke_time_ms'] + perf_metrics['add_time_ms']
        
        return QueryResponse(
            response=response.content,
            memory_saved=True,
            context_found=context_found,
            retrieved_memory=retrieved_memory_parts if retrieved_memory_parts else None,
            performance_metrics=perf_metrics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Mem0 query: {str(e)}")

@app.post("/zep/query", response_model=QueryResponse)
async def zep_query(request: QueryRequest):
    """
    Process query using Zep for memory management
    """
    if not zep_client or not llm:
        # Return mock response if clients not initialized
        return QueryResponse(
            response="Mock response: Memory system not connected. Please configure API keys.",
            memory_saved=False,
            context_found=False,
            retrieved_memory=None,
            performance_metrics={
                "user_setup_time_ms": 5.2,
                "thread_create_time_ms": 8.7,
                "search_time_ms": 12.3,
                "chain_invoke_time_ms": 245.7,
                "add_time_ms": 18.9,
                "total_time_ms": 290.8
            }
        )
    
    try:
        # Initialize performance metrics
        perf_metrics = {}
        
        # Performance counter for user setup
        user_setup_start = time.time()
        # Ensure user exists in Zep
        try:
            await ensure_zep_user(request.user_id)
        except Exception as e:
            # If user creation fails (e.g., due to auth), return mock response
            if "unauthorized" in str(e).lower() or "401" in str(e):
                return QueryResponse(
                    response="Mock response: Zep authentication failed. Please configure valid API keys.",
                    memory_saved=False,
                    context_found=False,
                    retrieved_memory=None,
                    performance_metrics={
                        "user_setup_time_ms": 0,
                        "search_time_ms": 0,
                        "chain_invoke_time_ms": 0,
                        "add_time_ms": 0,
                        "total_time_ms": 0
                    }
                )
        user_setup_end = time.time()
        perf_metrics['user_setup_time_ms'] = (user_setup_end - user_setup_start) * 1000
        
        # Performance counter for thread creation
        thread_create_start = time.time()
        # Create a new thread for this session
        thread_id = f"{request.user_id}_thread_{uuid.uuid4().hex[:8]}"
        try:
            await zep_client.thread.create(
                thread_id=thread_id,
                user_id=request.user_id
            )
        except Exception as e:
            # If thread creation fails due to auth, return mock response
            if "unauthorized" in str(e).lower() or "401" in str(e):
                return QueryResponse(
                    response="Mock response: Zep authentication failed. Please configure valid API keys.",
                    memory_saved=False,
                    context_found=False,
                    retrieved_memory=None,
                    performance_metrics={
                        "user_setup_time_ms": perf_metrics.get('user_setup_time_ms', 0),
                        "thread_create_time_ms": 0,
                        "search_time_ms": 0,
                        "chain_invoke_time_ms": 0,
                        "add_time_ms": 0,
                        "total_time_ms": perf_metrics.get('user_setup_time_ms', 0)
                    }
                )
        thread_create_end = time.time()
        perf_metrics['thread_create_time_ms'] = (thread_create_end - thread_create_start) * 1000
        
        # Retrieve context from Zep graph
        context_messages = []
        context_found = False
        retrieved_memory_parts = []
        
        # Performance counter for search
        search_start = time.time()
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
        search_end = time.time()
        perf_metrics['search_time_ms'] = (search_end - search_start) * 1000
        
        # Generate response
        chain = prompt | llm
        
        # Performance counter for chain.invoke
        invoke_start = time.time()
        response = chain.invoke({
            "context": context_messages,
            "messages": [HumanMessage(content=request.query)]
        })
        invoke_end = time.time()
        perf_metrics['chain_invoke_time_ms'] = (invoke_end - invoke_start) * 1000
        
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
        
        # Performance counter for message saving
        add_start = time.time()
        await zep_client.thread.add_messages(
            thread_id=thread_id,
            messages=messages
        )
        add_end = time.time()
        perf_metrics['add_time_ms'] = (add_end - add_start) * 1000
        
        # Calculate total time
        perf_metrics['total_time_ms'] = (
            perf_metrics.get('user_setup_time_ms', 0) +
            perf_metrics.get('thread_create_time_ms', 0) +
            perf_metrics.get('search_time_ms', 0) +
            perf_metrics.get('chain_invoke_time_ms', 0) +
            perf_metrics.get('add_time_ms', 0)
        )
        
        return QueryResponse(
            response=response.content,
            memory_saved=True,
            context_found=context_found,
            retrieved_memory=retrieved_memory_parts if retrieved_memory_parts else None,
            performance_metrics=perf_metrics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Zep query: {str(e)}")

async def ensure_zep_user(user_id: str):
    """Ensure user exists in Zep, create if not"""
    if not zep_client:
        return
    
    try:
        await zep_client.user.get(user_id)
    except Exception as e:
        error_str = str(e).lower()
        if "unauthorized" in error_str or "401" in error_str:
            # API key is invalid, skip user creation
            return
        if "not found" in error_str:
            try:
                await zep_client.user.add(
                    user_id=user_id,
                    email=f"{user_id}@example.com",
                    first_name="Demo",
                    last_name="User"
                )
            except Exception:
                # Ignore errors in user creation
                pass

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