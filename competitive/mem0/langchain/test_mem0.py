#!/usr/bin/env python3
"""Test script to verify Mem0 functionality"""

import os
from mem0 import MemoryClient

# Initialize client
mem0 = MemoryClient(api_key=os.environ.get("MEM0_API_KEY"))
user_id = "test_user_123"

print("Testing Mem0 functionality...")
print("=" * 40)

# Test 1: Add a memory
print("\n1. Adding a test memory...")
messages = [
    {"role": "user", "content": "I've been to Paris, Tokyo, and New York recently."},
    {"role": "assistant", "content": "That's wonderful! You've visited some amazing cities."}
]
add_result = mem0.add(messages, user_id=user_id)
print(f"Add result: {add_result}")

# Test 2: Search for the memory
print("\n2. Searching for 'Paris'...")
search_result = mem0.search(query="Paris", user_id=user_id, limit=5)
print(f"Search result: {search_result}")

# Test 3: Search for travel-related memories
print("\n3. Searching for 'travel' or 'been to'...")
search_result2 = mem0.search(query="travel been to cities", user_id=user_id, limit=5)
print(f"Search result: {search_result2}")

# Test 4: Get all memories for user
print("\n4. Getting all memories for user...")
all_memories = mem0.get_all(user_id=user_id)
print(f"All memories: {all_memories}")