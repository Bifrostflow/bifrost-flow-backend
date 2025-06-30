from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam, \
    ChatCompletionAssistantMessageParam

from app.models.models import State, Response
from app.controllers.tools.tools_helpers.manage_messages import ChatHistory, manage_flow_chat_history

def write_code(state:State):
    print("🤖 --- doing write_code",state.get("node_data"))
    load_dotenv()
    client = OpenAI()

    #  Define prompts
    system_prompt = """
            You are a Coding Expert Agent
            Your job is to write code only 
            if provided prompt is not for code generation just skip by saying not able to generate code 
            no need to add any extra text or message for user like how to use and other docs you can add code comments only 
        """
    tool_prompt = "write code based on provided response"

    # Add Chat item
    tool_chat = ChatCompletionUserMessageParam(role="user", content=tool_prompt)
    system_prompt_chat = ChatCompletionSystemMessageParam(role="system", content=system_prompt),

    # Create chat data
    chat_data = ChatHistory(state=state, tool_prompt=tool_chat)
    messages = manage_flow_chat_history(data=chat_data)

    query_res = client.chat.completions.create(
        model="gpt-4.1",
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
        "meta": state.get("response").get("meta")
    }
    state["response"] = response
    state["ui_response"] = "Finished writing code."
    return state
