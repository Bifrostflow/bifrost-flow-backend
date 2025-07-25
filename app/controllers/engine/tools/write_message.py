from app.controllers.engine.helpers import load_model_with_key
from app.models.models import MessageResponse, State, Response
from app.controllers.engine.tools.tools_helpers.manage_messages import (
    ChatHistory,
    manage_flow_chat_history,
)
from app.utils.constants import OPEN_AI_KEY
from langchain_core.messages import HumanMessage,SystemMessage

def write_message(state: State):
    print("🤖 --- doing write_message", state.get("node_data"))
    user_openai_key = state.get("api_keys").get(OPEN_AI_KEY)
    client = load_model_with_key(user_openai_key,"gpt-4.1-mini")

    #  Define prompts
    system_prompt = """
                You are an agent which generates messages/text based on user prompt.
                You will not generate code or any data which is not general text or simple user prompt.
                you can help the summarize things like blogs, codes, documentation, news, articles, etc.
                Refuse to generate without enough context 
                """
    tool_prompt = "write message based on provided response"

    # Add Chat item
    tool_chat = HumanMessage(tool_prompt)
    system_prompt_chat = SystemMessage(system_prompt)

    # Create chat data
    chat_data = ChatHistory(state=state, tool_prompt=tool_chat)
    messages = manage_flow_chat_history(data=chat_data)
    
    query_res = client.invoke([system_prompt_chat, *messages])
    message = ""
    if query_res.content:
        message = query_res.content

    response_chat_data = MessageResponse(content=message,role="assistant")
    messages.append(response_chat_data)
    response: Response = {
        "messages": messages,
        "type": state.get("response").get("type"),
        "meta": state.get("response").get("meta"),
        "links_to_open":state.get("response").get("links_to_open"),
    }
    state["response"] = response
    return state