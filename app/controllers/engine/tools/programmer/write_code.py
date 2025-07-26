from langchain_core.messages import HumanMessage,SystemMessage
from app.controllers.engine.helpers import load_model_with_key
from app.controllers.get_system_node_by_id import get_node_ui_loading_failed_message
from app.models.models import MessageResponse, State, Response
from app.controllers.engine.tools.tools_helpers.manage_messages import (
    ChatHistory,
    manage_flow_chat_history,
)
from app.utils.constants import OPEN_AI_KEY


def write_code(state: State):
    print("🤖 --- doing write_code", state.get("node_data"))

    user_openai_key = state.get("api_keys").get(OPEN_AI_KEY)
    client = load_model_with_key(user_openai_key,"gpt-4.1")

    #  Define prompts
    system_prompt = f"""
            You are a Coding Expert Agent
            Your job is to write code only 
            if provided prompt is not for code generation just skip by saying `{get_node_ui_loading_failed_message(state.get("node_data").get("node_graph_id"))}` 
            no need to add any extra text or message for user like how to use and other docs you can add code comments only 
        """
    tool_prompt = "write code based on provided response"

    # Add Chat item
    tool_chat = HumanMessage(tool_prompt)
    system_prompt_chat = (
        SystemMessage(system_prompt),
    )

    # Create chat data
    chat_data = ChatHistory(state=state, tool_prompt=tool_chat)
    messages = manage_flow_chat_history(data=chat_data)

    query_res = client.invoke([*system_prompt_chat, *messages])

    message = ""
    if query_res.content:
        message = query_res.content

    response_chat_data = MessageResponse(
        role="assistant", content=message
    )
    messages.append(response_chat_data)

    response: Response = {
        "messages": messages,
        "type": state.get("response").get("type"),
        "meta": state.get("response").get("meta"),
        "links_to_open":state.get("response").get("links_to_open"),
    }
    state["response"] = response
    return state
