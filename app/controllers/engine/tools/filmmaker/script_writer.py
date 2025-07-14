import json
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
)

from app.models.meta import ScriptWriterMeta
from app.models.models import State, Response
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
    client = OpenAI(api_key=user_openai_key)

    #  Define prompts
    system_prompt = script_writer_system_prompt
    tool_prompt = script_writer_tool_prompt

    # Add Chat item
    tool_chat = ChatCompletionUserMessageParam(role="user", content=tool_prompt)
    system_prompt_chat = (
        ChatCompletionSystemMessageParam(role="system", content=system_prompt),
    )

    # Create chat data
    chat_data = ChatHistory(state=state, tool_prompt=tool_chat)
    messages = manage_flow_chat_history(data=chat_data)

    query_res = client.beta.chat.completions.parse(
        model="gpt-4.1-mini",
        response_format=ScriptWriterMeta,
        messages=[*system_prompt_chat, *messages],
    )
    parsed_response=query_res.choices[0].message.parsed
    parsed_response.node_id=state.get("node_data").get("node_graph_id")
    parsed_response.type=SCRIPT_WRITER
    meta=parsed_response.model_dump()
    message = parsed_response.response_message
    

    response_chat_data = ChatCompletionAssistantMessageParam(
        role="assistant", content=message
    )
    messages.append(response_chat_data)

    response: Response = {
        "messages": messages,
        "type": state.get("response").get("type"),
        "meta": [*state.get("response").get("meta"),json.dumps(meta)],
    }
    state["response"] = response
    return state
