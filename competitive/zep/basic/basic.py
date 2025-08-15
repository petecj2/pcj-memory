import os
from zep_cloud.client import Zep
from zep_cloud.types import Message
import json
import uuid

# Read API key from environment variable
API_KEY = os.getenv("ZEP_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Please set the ZEP_API_KEY environment variable.")

print("API key loaded successfully!")
client = Zep(api_key=API_KEY,)

user_id = "user123"
new_user = client.user.add(
    user_id=user_id,
    email="user@example.com",
    first_name="Jane",
    last_name="Smith",
)


# Generate a unique thread ID
thread_id = uuid.uuid4().hex
# Create a new thread for the user
client.thread.create(
    thread_id=thread_id,
    user_id=user_id,
)

messages = [
    Message(
        name="Jane",
        content="Hi, my name is Jane Smith and I work at Acme Corp.",
        role="user",
    ),
    Message(
        name="AI Assistant",
        content="Hello Jane! Nice to meet you. How can I help you with Acme Corp today?",
        role="assistant",
    )
]
# Add messages to the thread
client.thread.add_messages(thread_id, messages=messages)

json_data = {
    "employee": {
        "name": "Jane Smith",
        "position": "Senior Software Engineer",
        "department": "Engineering",
        "projects": ["Project Alpha", "Project Beta"]
    }
}
client.graph.add(
    user_id=user_id,
    type="json",
    data=json.dumps(json_data)
)
# Add text data to a user's graph
client.graph.add(
    user_id=user_id,
    type="text",
    data="Jane Smith is working on Project Alpha and Project Beta."
)

# Get memory for the thread
memory = client.thread.get_user_context(thread_id=thread_id)

# Access the context block (for use in prompts)
context_block = memory.context
print(context_block)