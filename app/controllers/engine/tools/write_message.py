from openai import OpenAI
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
)

from app.models.models import State, Response
from app.controllers.engine.tools.tools_helpers.manage_messages import (
    ChatHistory,
    manage_flow_chat_history,
)


def write_message(state: State):
    print("🤖 --- doing write_message", state.get("node_data"))
    user_openai_key = state.get("api_keys").get("openai")
    client = OpenAI(api_key=user_openai_key)

    #  Define prompts
    system_prompt = """
                   You are an agent which generates messages/text based on user prompt.
                   You will not generate code or any data which is not general text or simple user prompt.
                   you can help the summarize things like blogs, codes, documentation, news, articles, etc.
                   Refuse to generate without enough context 
                   """
    tool_prompt = "write message based on provided response"

    # Add Chat item
    tool_chat = ChatCompletionUserMessageParam(role="user", content=tool_prompt)
    system_prompt_chat = (
        ChatCompletionSystemMessageParam(role="system", content=system_prompt),
    )

    # Create chat data
    chat_data = ChatHistory(state=state, tool_prompt=tool_chat)
    messages = manage_flow_chat_history(data=chat_data)
    query_res = client.chat.completions.create(
        model="gpt-4.1-mini", messages=[*system_prompt_chat, *messages]
    )

    message = ""
    if query_res.choices[0].message.content:
        message = query_res.choices[0].message.content

    response_chat_data = ChatCompletionAssistantMessageParam(
        role="assistant", content=message
    )
    messages.append(response_chat_data)

    response: Response = {
        "messages": messages,
        "type": state.get("response").get("type"),
        "meta": state.get("response").get("meta"),
    }
    state["response"] = response
    state["ui_response"] = "Finished Writing message."
    return state
