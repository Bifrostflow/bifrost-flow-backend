import json
from typing import List
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
)
from tavily import TavilyClient
from app.models.models import State, Response


def tavily_search(state: State):
    print("🤖 --- doing write_message", state.get("node_data"))
    messages = state.get("response").get("messages")
    # requires node input
    node_input = ""
    # start finding node input
    meta_strings = state.get("response").get("meta")
    node_input_found = False
    if not node_input_found:
        if len(meta_strings) > 0:
            for meta_string in meta_strings[::-1]:
                meta_json = json.loads(meta_string)
                if meta_json.get("type") == "google_trends":
                    google_trends_data = meta_json
                    node_input = f"search this {google_trends_data.get("title")}"
                    node_input_found = True
    if not node_input_found:
        if state.get("node_data").get("node_input"):
            node_input = state.get("node_data").get(
                "node_input"
            )  # input provided by user to node via UI
            node_input_found = True
        else:
            node_input = messages[0].get("content")  # prompt
            node_input_found = True
    if not node_input_found:
        if len(state.get("response").get("messages")) > 0:
            node_input = state.get("response").get("messages")[-1].get("content")
            node_input_found = True
    # end finding node input

    user_tavily_api_key = state.get("api_keys").get("tavily")
    tavily_client = TavilyClient(api_key=user_tavily_api_key)
    search_response = tavily_client.search(node_input)

    results = search_response.get("results")[0:3]
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
    return state
