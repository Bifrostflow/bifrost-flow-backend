
from langchain_core.messages import HumanMessage,SystemMessage
import json
from app.controllers.engine.helpers import load_model_with_key
from app.models.meta import CodeDocumentation
from app.models.models import MessageResponse, State, Response
from app.controllers.engine.prompts.programmer.code_documentation import (
    code_documentation_system_prompt,
    code_documentation_tool_prompt,
)
from app.controllers.engine.tools.tools_helpers.manage_messages import (
    ChatHistory,
    manage_flow_chat_history,
)
from app.utils.constants import OPEN_AI_KEY

CODE_DOCUMENTATION = "code_documentation"


def code_documentation(state: State):
    print("🤖 --- doing code_documentation", state.get("node_data"))

    user_openai_key = state.get("api_keys").get(OPEN_AI_KEY)
    client = load_model_with_key(user_openai_key,"gpt-4.1-nano")

    # Define prompts
    system_prompt = code_documentation_system_prompt
    tool_prompt = code_documentation_tool_prompt

    # Add Chat item
    tool_chat = HumanMessage(role="user", content=tool_prompt)
    system_prompt_chat = (
        SystemMessage(role="system", content=system_prompt),
    )

    # Create chat data
    chat_data = ChatHistory(state=state, tool_prompt=tool_chat)
    messages = manage_flow_chat_history(data=chat_data)

    # run prompt
    structured_client = client.with_structured_output(CodeDocumentation)
    query_res=structured_client.invoke([*system_prompt_chat, *messages])

    # manage parsed response
    parsed_response = query_res.model_dump()
    parsed_response["type"] = CODE_DOCUMENTATION
    parsed_response["node_id"] = state.get("node_data").get("node_graph_id")

    if not parsed_response:
        return state
    meta = parsed_response

    # manage parsed response remark
    message = ""
    if parsed_response["content"]:
        message = parsed_response.get("response_message")

    response_chat_data = MessageResponse(
        role="assistant", content=message
    )
    messages.append(response_chat_data)

    response: Response = {
        "type": state.get("response").get("type"),
        "messages": messages,
        "meta": [*state.get("response").get("meta"), json.dumps(meta)],
        "links_to_open":state.get("response").get("links_to_open"),
    }
    state["response"] = response
    return state
