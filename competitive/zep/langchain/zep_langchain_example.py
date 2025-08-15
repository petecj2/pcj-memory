#!/usr/bin/env python3
"""
Simple Zep + LangChain Integration Example
Demonstrates context-aware conversations with memory persistence
"""

import os
import asyncio
import uuid
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from zep_cloud import AsyncZep
from zep_cloud.types import Message


async def main():
    # Initialize clients using environment variables
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    zep_client = AsyncZep(
        api_key=os.environ.get("ZEP_API_KEY")
    )
    
    # User identifier for memory association
    user_id = "demo_user_123"
    
    # Check if user exists, create if not
    print(f"Checking for user '{user_id}'...")
    try:
        user = await zep_client.user.get(user_id)
        print(f"User '{user_id}' found")
    except Exception as e:
        if "not found" in str(e).lower():
            print(f"User '{user_id}' not found, creating...")
            try:
                await zep_client.user.add(
                    user_id=user_id,
                    email="demo@example.com",
                    first_name="Demo",
                    last_name="User"
                )
                print(f"User '{user_id}' created successfully")
            except Exception as create_error:
                print(f"Error creating user: {create_error}")
                return
        else:
            print(f"Error checking user: {e}")
            return
    
    # Create a new thread for this session
    thread_id = f"{user_id}_thread_{uuid.uuid4().hex[:8]}"
    print(f"Creating new thread '{thread_id}'...")
    try:
        await zep_client.thread.create(
            thread_id=thread_id,
            user_id=user_id
        )
        print(f"Thread '{thread_id}' created successfully")
    except Exception as e:
        print(f"Error creating thread: {e}")
        return
    
    # Create prompt template with memory context
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a helpful assistant with access to conversation history.
        Use the provided context from previous interactions to give personalized responses.
        If context is relevant, reference it naturally in your response."""),
        MessagesPlaceholder(variable_name="context"),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    async def retrieve_context(query, user_id):
        """Retrieve relevant memories for the user using graph search"""
        print(f"Searching graph - Query: '{query}', User ID: '{user_id}'")
        
        context_messages = []
        try:
            # Search the user's knowledge graph
            search_results = await zep_client.graph.search(
                user_id=user_id,
                query=query,
                limit=5,
                scope="edges"  # Search edges for relationships and facts
            )
            
            if search_results and search_results.edges:
                print(f"  Found {len(search_results.edges)} relevant memories")
                # Combine relevant memories into context
                context_parts = []
                for edge in search_results.edges:
                    # Extract fact from the edge
                    fact = edge.fact if hasattr(edge, 'fact') else str(edge)
                    context_parts.append(fact)
                    print(f"    - {fact[:100]}...")  # Print first 100 chars of each fact
                
                if context_parts:
                    combined_context = "\n".join(context_parts)
                    context_messages.append(
                        SystemMessage(content=f"Previous context from knowledge graph:\n{combined_context}")
                    )
            else:
                print("  No relevant memories found in graph")
                
        except Exception as e:
            print(f"  Error searching graph: {e}")
        
        return context_messages
    
    async def generate_response(query, user_id):
        """Generate context-aware response using LangChain and Zep"""
        # Retrieve relevant context
        context = await retrieve_context(query, user_id)
        
        # Format messages for the prompt
        chain = prompt | llm
        
        response = chain.invoke({
            "context": context,
            "messages": [HumanMessage(content=query)]
        })
        
        return response.content
    
    async def save_interaction(query, response, thread_id, user_id):
        """Save the interaction to Zep for future reference"""
        messages = [
            Message(
                name=user_id,
                role="user",
                content=query
            ),
            Message(
                name="Assistant",
                role="assistant",
                content=response
            )
        ]
        
        print(f"\nSaving memory for thread '{thread_id}'...")
        try:
            result = await zep_client.thread.add_messages(
                thread_id=thread_id,
                messages=messages
            )
            print(f"Memory saved successfully")
            return result
        except Exception as e:
            print(f"Error saving memory: {e}")
            return None
    
    # Example conversation loop
    print("\nZep + LangChain Integration Demo")
    print("=" * 40)
    print(f"Session Thread ID: {thread_id}")
    print("Type 'quit' to exit\n")
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            # Generate response with context
            response = await generate_response(user_input, user_id)
            print(f"\nAssistant: {response}\n")
            
            # Save the interaction for future context
            await save_interaction(user_input, response, thread_id, user_id)
            
        except Exception as e:
            print(f"Error: {e}")
            print("Make sure your API keys are set in environment variables:")
            print("  - OPENAI_API_KEY")
            print("  - ZEP_API_KEY")
            break


if __name__ == "__main__":
    # Check for required environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    if not os.environ.get("ZEP_API_KEY"):
        print("Error: ZEP_API_KEY environment variable not set")
        exit(1)
    
    # Run the async main function
    asyncio.run(main())