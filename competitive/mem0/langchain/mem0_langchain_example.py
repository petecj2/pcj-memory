#!/usr/bin/env python3
"""
Simple Mem0 + LangChain Integration Example
Demonstrates context-aware conversations with memory persistence
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from mem0 import MemoryClient


def main():
    # Initialize clients using environment variables
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    mem0 = MemoryClient(
        api_key=os.environ.get("MEM0_API_KEY")
    )
    
    # User identifier for memory association
    user_id = "demo_user_123"
    
    # Create prompt template with memory context
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a helpful assistant with access to conversation history.
        Use the provided context from previous interactions to give personalized responses.
        If context is relevant, reference it naturally in your response."""),
        MessagesPlaceholder(variable_name="context"),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    def retrieve_context(query, user_id):
        """Retrieve relevant memories for the user"""
        print(f"Searching memories - Query: '{query}', User ID: '{user_id}'")
        memories = mem0.search(query=query, user_id=user_id, limit=5)
        
        context_messages = []
        if memories:
            # mem0.search returns a list directly, not a dict with "results"
            for memory in memories:
                memory_content = memory.get('memory', '')
                print(f"  Found memory: {memory_content}")
                context_messages.append(
                    SystemMessage(content=f"Previous context: {memory_content}")
                )
        
        return context_messages
    
    def generate_response(query, user_id):
        """Generate context-aware response using LangChain and Mem0"""
        # Retrieve relevant context
        context = retrieve_context(query, user_id)

        #print('Context:', [msg.content for msg in context] if context else "No context found")
        
        # Format messages for the prompt
        chain = prompt | llm
        
        response = chain.invoke({
            "context": context,
            "messages": [HumanMessage(content=query)]
        })
        
        return response.content
    
    def save_interaction(query, response, user_id):
        """Save the interaction to Mem0 for future reference"""
        messages = [
            {"role": "user", "content": query},
            {"role": "assistant", "content": response}
        ]
        print(f"\nSaving memory for user '{user_id}'...")
        result = mem0.add(messages, user_id=user_id)
        print(f"Memory save result: {result}")
        return result
    
    # Example conversation loop
    print("Mem0 + LangChain Integration Demo")
    print("=" * 40)
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
            response = generate_response(user_input, user_id)
            print(f"\nAssistant: {response}\n")
            
            # Save the interaction for future context
            save_interaction(user_input, response, user_id)
            
        except Exception as e:
            print(f"Error: {e}")
            print("Make sure your API keys are set in environment variables:")
            print("  - OPENAI_API_KEY")
            print("  - MEM0_API_KEY")
            break


if __name__ == "__main__":
    # Check for required environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    if not os.environ.get("MEM0_API_KEY"):
        print("Error: MEM0_API_KEY environment variable not set")
        exit(1)
    
    main()