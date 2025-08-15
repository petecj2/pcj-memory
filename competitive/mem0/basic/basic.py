import os
from mem0 import MemoryClient
import json

# Read API key from environment variable
api_key = os.getenv("MEM0_API_KEY")

if not api_key:
    raise ValueError("API key not found. Please set the MY_API_KEY environment variable.")

print("API key loaded successfully!")

client = MemoryClient(api_key)

messages = [
    { "role": "user", "content": "Hi, I'm Alex. I'm a vegetarian and I'm allergic to nuts." },
    { "role": "assistant", "content": "Hello Alex! I see that you're a vegetarian with a nut allergy." }
]

client.add(messages, user_id="alex")

query = "What can I cook for dinner tonight?"

print(json.dumps(client.search(query, user_id="alex"), indent=4))