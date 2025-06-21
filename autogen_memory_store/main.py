import asyncio
import uuid

from autogen_memory_store.server import serve

thread_id = str(uuid.uuid4())

# test fixture to simulate a chat session
# calling the serve function with a unique thread_id


while True:
    input_message = input("Enter your message (type 'exit' to quit): ")
    if input_message.lower() == "exit":
        print("Exiting...")
        break
    response = asyncio.run(serve(thread_id, input_message))
    print(f"Response: {response}")
