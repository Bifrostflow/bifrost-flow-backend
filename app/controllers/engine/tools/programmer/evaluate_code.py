import json

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
)
from app.models.meta import EvaluateCodeModel
from app.models.models import Response, State
from app.controllers.engine.tools.tools_helpers.manage_messages import (
    ChatHistory,
    manage_flow_chat_history,
)
from app.utils.constants import OPEN_AI_KEY

EVALUATE_CODE = "evaluate_code"


def evaluate_code(state: State):
    print("🤖 --- doing evaluate_code", state.get("node_data"))

    user_openai_key = state.get("api_keys").get(OPEN_AI_KEY)
    client = OpenAI(api_key=user_openai_key)

    #  Define prompts
    system_prompt = """
            You are a Coding Expert Agent and your job is to 
            1. Check if provided value is code
            2. If not code send is_code as false else true and remark as 'no code provided by user'
            3. If provided prompt is code, evaluate the code thoroughly rate it out out of 1-10 
                    where 1 is lowest quality and 10 is highest quality
                    add a remark for betterment or appreciation (30 words limit.)
    """
    tool_prompt = "evaluate provided code"
    generated_code = state.get("response").get("messages")[-1].get("content")
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
        response_format=EvaluateCodeModel,
        messages=[*system_prompt_chat, *messages],
    )
    # manage parsed response
    parsedResponse = query_res.choices[0].message.parsed
    parsedResponse.type = EVALUATE_CODE
    parsedResponse.node_id = state.get("node_data").get("node_graph_id")
    parsedResponse.code = generated_code

    meta = parsedResponse.model_dump()

    # manage parsed response remark
    message = ""
    if parsedResponse.remark:
        message = parsedResponse.remark

    response_chat_data = ChatCompletionAssistantMessageParam(
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
