import json


from langchain_core.messages import HumanMessage,SystemMessage

from app.controllers.engine.helpers import load_model_with_key
from app.db.template_data import generate_receipt_id
from app.models.meta import ScriptWriterMeta
from app.models.models import MessageResponse, State, Response
from app.controllers.engine.prompts.filmmaker.script_writer import (
    script_writer_system_prompt,
    script_writer_tool_prompt,
)
from app.controllers.engine.tools.tools_helpers.manage_messages import (
    ChatHistory,
    manage_flow_chat_history,
)
from app.utils.constants import OPEN_AI_KEY

SCRIPT_WRITER = "script_writer"

def script_writer(state: State):
    print("🤖 --- doing script_writer", state.get("node_data"))

    user_openai_key = state.get("api_keys").get(OPEN_AI_KEY)
    client = load_model_with_key(user_openai_key,"gpt-4.1-mini")

    #  Define prompts
    system_prompt = script_writer_system_prompt
    tool_prompt = script_writer_tool_prompt

    # Add Chat item
    tool_chat = HumanMessage(role="user", content=tool_prompt)
    system_prompt_chat = (
        SystemMessage(role="system", content=system_prompt),
    )

    # Create chat data
    chat_data = ChatHistory(state=state, tool_prompt=tool_chat)
    messages = manage_flow_chat_history(data=chat_data)

    structured_client = client.with_structured_output(ScriptWriterMeta)
    query_res=structured_client.invoke([*system_prompt_chat, *messages])

    query_res = client.invoke([*system_prompt_chat, *messages])

    parsed_response=query_res.model_dump()
    parsed_response["node_id"]=state.get("node_data").get("node_graph_id")
    parsed_response["type"]=SCRIPT_WRITER
    parsed_response["slug_name"]=f"{parsed_response.get("slug_name") or generate_receipt_id()}_{generate_receipt_id()}"
    meta=parsed_response
    message = parsed_response.get("response_message")
    

    response_chat_data = MessageResponse(
        role="assistant", content=message or "Script generated."
    )
    messages.append(response_chat_data)

    response: Response = {
        "messages": messages,
        "meta": [*state.get("response").get("meta"),json.dumps(meta)],
        "type": state.get("response").get("type"),
        "links_to_open":[*state.get("response").get("links_to_open")],
    }
    state["response"] = response
    return state
