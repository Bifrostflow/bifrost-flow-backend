from dotenv import load_dotenv
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
)
from tavily import TavilyClient
from app.models.models import State, Response


def tavily_search(state: State):
    print("🤖 --- doing write_message", state.get("node_data"))
    load_dotenv()
    messages = state.get("response").get("messages")

    # requires node input
    node_input = ""
    if state.get("node_data").get("node_input"):
        node_input = state.get("node_data").get(
            "node_input"
        )  # input provided by user to node via UI
    else:
        node_input = messages[0].get("content")  # prompt
    user_tavily_api_key = state.get("api_keys").get("tavily")
    tavily_client = TavilyClient(api_key=user_tavily_api_key)
    search_response = tavily_client.search(node_input)
    print(search_response)
    results = search_response.get("results")[0:2]
    result_text = ""
    for result in results:
        result_text += f"result title:{result.get("title")}, content:{result.get("content")} \n\n\n"

    message = result_text

    user_request = ChatCompletionUserMessageParam(role="user", content=f"{node_input}")
    messages.append(user_request)
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
    print(state)
    state["ui_response"] = "Search finished."
    return state
