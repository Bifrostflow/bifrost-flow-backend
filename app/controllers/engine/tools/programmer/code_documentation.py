from openai import OpenAI
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
)
import json
from app.models.models import State, Response, CodeDocumentation
from app.controllers.engine.prompts.programmer.code_documentation import (
    code_documentation_system_prompt,
    code_documentation_tool_prompt,
)
from app.controllers.engine.tools.tools_helpers.manage_messages import (
    ChatHistory,
    manage_flow_chat_history,
)

CODE_DOCUMENTATION = "code_documentation"


def code_documentation(state: State):
    print("🤖 --- doing code_documentation", state.get("node_data"))

    user_openai_key = state.get("api_keys").get("openai")
    client = OpenAI(api_key=user_openai_key)

    # Define prompts
    system_prompt = code_documentation_system_prompt
    tool_prompt = code_documentation_tool_prompt

    # Add Chat item
    tool_chat = ChatCompletionUserMessageParam(role="user", content=tool_prompt)
    system_prompt_chat = (
        ChatCompletionSystemMessageParam(role="system", content=system_prompt),
    )

    # Create chat data
    chat_data = ChatHistory(state=state, tool_prompt=tool_chat)
    messages = manage_flow_chat_history(data=chat_data)

    # run prompt
    query_res = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=CodeDocumentation,
        messages=[*system_prompt_chat, *messages],
    )
    # manage parsed response
    parsed_response = query_res.choices[0].message.parsed
    parsed_response.type = CODE_DOCUMENTATION
    parsed_response.node_id = state.get("node_data").get("node_graph_id")

    state["ui_response"] = "Finished code documentation."
    if not parsed_response:
        return state
    meta = parsed_response.model_dump()

    # manage parsed response remark
    message = ""
    if parsed_response.content:
        message = parsed_response.response_message

    response_chat_data = ChatCompletionAssistantMessageParam(
        role="assistant", content=message
    )
    messages.append(response_chat_data)

    response: Response = {
        "type": state.get("response").get("type"),
        "messages": messages,
        "meta": [*state.get("response").get("meta"), json.dumps(meta)],
    }
    state["response"] = response
    return state
