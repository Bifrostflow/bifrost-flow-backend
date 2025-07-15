from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
)
from typing import List
from app.controllers.get_system_node_by_id import get_node_ui_loading_message
from app.models.models import State, Response, ResponseModel
from app.db.jsonDB import tools_db

# CLASSIFY_MESSAGE = "classify_message"
CLASSIFY_MESSAGE = "684a054b6c981a601e166627"


async def classify_message(state: State):
    print("🤖 --- doing classification", state.get("node_data"))
    load_dotenv()
    client = OpenAI()

    next_nodes = state.get("node_data").get("next_nodes")
    print("next_nodes: ", next_nodes)
    next_node_steps_check = ""
    type_map = dict()
    for p_node in next_nodes:
        node_id = p_node.split("-")[1]
        node_id_prefix = p_node.split("-")[0]
        node = tools_db.get_by_id(node_id)
        prefixed_type = f"{node_id_prefix}-{node.type}"
        print("prefixed_type: ",prefixed_type)
        type_map[prefixed_type] = p_node

        # TODO FIX THIS PROMPT SO AI CAN DIFFERENTIATE BETWEEN TWO SAME types
        next_node_steps_check += (
            f"\nprefixed_type: `{prefixed_type}` as `type`: {node.what_i_do} and this node_id_prefix: `{node_id_prefix}` as `prefix`"
        )

    system_prompt = """
   You are a data classifier.

Your task:
- Receive a prompt and a response from the user.
- Identify the correct `type` (also called `prefixed_type`) based on the data pattern.
- Each type has a `description`. Use that to choose the most appropriate one.
- Your job is to return only one valid `prefixed_type` from the defined list.

Behavior rules:
1. If a specific tool or node matches the pattern, select its `prefixed_type` and generate a message accordingly.
2. If no tool matches the input, return the **first node's `prefixed_type`** and generate the message:"No suitable node found. Using default: <prefixed_type>"
3. ❌ Never return a type that is not part of the defined list. This will cause an error.
✅ Instead, safely select any existing `prefixed_type` from the available tools/nodes.

Output:
- Return only the selected `prefixed_type`.
- Along with a short message justifying the selection.

Be strict, precise, and deterministic.

    """

    prompt = state.get("response").get("messages")[0].get("content")
    user_message = f"""
        PROMPT-START:
        Prompt: {prompt}
        PROMPT-END:
        
        -- Check for this tools
        {next_node_steps_check}

        
        """

    messages: List[
        ChatCompletionSystemMessageParam
        | ChatCompletionUserMessageParam
        | ChatCompletionAssistantMessageParam
    ] = [
        ChatCompletionSystemMessageParam(role="system", content=system_prompt),
        ChatCompletionUserMessageParam(role="user", content=user_message),
    ]

    query_res = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=ResponseModel,
        messages=messages,
    )
    parsed_response=query_res.choices[0].message.parsed
    prompt_type = parsed_response.type
    sanitized_prompt_type=prompt_type.split("-")[-1]
    response_message=ChatCompletionAssistantMessageParam(role="assistant",content=parsed_response.message)
    prompt_prefix = parsed_response.prefix
    
    route_id = f"{prompt_prefix}-{sanitized_prompt_type}"
    print(route_id)
    ui_response=get_node_ui_loading_message(type_map[route_id])
    print(ui_response)
    response: Response = {
        "type": type_map[route_id],
        "messages": [*state.get("response").get("messages"),response_message],
        "meta": state.get("response").get("meta"),
        "links_to_open":state.get("response").get("links_to_open"),
    }
    state["response"] = response
    state["ui_response"]=ui_response
    return state
