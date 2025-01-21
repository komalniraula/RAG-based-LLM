from dotenv import load_dotenv
import chainlit as cl
import auth
from typing import Optional
import update_counter  # Import the new module
import llm_model

# Load environment variables from .env file
load_dotenv()

# Define the password authentication function
@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    if auth.validate_user(username, password):
        return cl.User(identifier=username, metadata={"role": "user", "provider": "credentials"})
    return None

@cl.on_chat_start
async def on_chat_start():
    app_user = cl.user_session.get("user")
    if app_user:
        # Split the identifier and capitalize the first name
        first_name = app_user.identifier.split('.')[0].capitalize()
        await cl.Message(content=f"Hello {first_name}, ask anything about Jyoti Bikash Bank internal policies. Currently, I am only aware of operation Manual 2080.").send()
    else:
        await cl.Message(content="You need to log in first.").send()

@cl.on_message
async def main(message: cl.Message):
    app_user = cl.user_session.get("user")

    if not app_user:
        await cl.Message(content="You need to log in first.").send()
        return

    user_id = app_user.identifier

    users = auth.read_users()
    if users[user_id]['counter'] > users[user_id]['limit']:
        await cl.Message(content='Limit reached for today').send()
        return

    embedded_result = llm_model.search_index(message.content)
    context = "\n".join(embedded_result)
    formatted_string = f"Question: {message.content}\n\nContext: {context}"
    output = llm_model.get_response(formatted_string)
    print("------")

    users[user_id]['counter'] += 1  # Update the in-memory counter
    update_counter.update_counter(user_id)  # Persist the counter update

    await cl.Message(content=f"Received: {output}").send()

if __name__ == "__main__":
    cl.run(port=8000)