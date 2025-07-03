from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam, \
    ChatCompletionSystemMessageParam

from app.models.models import State, Response
from app.controllers.engine.prompts.filmmaker.script_writer import script_writer_system_prompt, script_writer_tool_prompt
from app.controllers.engine.tools.tools_helpers.manage_messages import ChatHistory, manage_flow_chat_history

def script_writer(state:State):
    print("🤖 --- doing write_message", state.get("node_data"))
    load_dotenv()
    client = OpenAI()

    #  Define prompts
    system_prompt=script_writer_system_prompt
    tool_prompt=script_writer_tool_prompt

    # Add Chat item
    tool_chat=ChatCompletionUserMessageParam(role="user", content=tool_prompt)
    system_prompt_chat=ChatCompletionSystemMessageParam(role="system",content=system_prompt),

    # Create chat data
    chat_data = ChatHistory(state=state, tool_prompt=tool_chat)
    messages = manage_flow_chat_history(data=chat_data)

    query_res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            *system_prompt_chat,
            *messages]
    )

    message=""
    if query_res.choices[0].message.content:
        message=query_res.choices[0].message.content

    response_chat_data=ChatCompletionAssistantMessageParam(role="assistant",content=message)
    messages.append(response_chat_data)

    response: Response = {
        "messages": messages,
        "type": state.get("response").get("type"),
        "meta":state.get("response").get("meta")
    }
    state["response"] = response
    state["ui_response"] = "Finished writing script."
    return state
