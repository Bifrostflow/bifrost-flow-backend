from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
)
from typing import List
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
            f"\n{prefixed_type}: {node.what_i_do} and this `{node_id_prefix}` as prefix"
        )

    system_prompt = """
    You are a data classifier and your job is to get prompt, and response data pattern `type` from user with `description` about that type
    and return appropriate type.
    """

    prompt = state.get("response").get("messages")[0].get("content")
    user_message = f"""
        PROMPT-START:
        Prompt: {prompt}
        PROMPT-END:
        
        -- Check for this
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
    prompt_type = query_res.choices[0].message.parsed.type
    sanitized_prompt_type=prompt_type.split("-")[-1]
    response_message=ChatCompletionAssistantMessageParam(role="assistant",content=f"Redirecting to {sanitized_prompt_type.replace("_"," ")}")
    prompt_prefix = query_res.choices[0].message.parsed.prefix
    
    route_id = f"{prompt_prefix}-{sanitized_prompt_type}"
    
    response: Response = {
        "type": type_map[route_id],
        "messages": [*state.get("response").get("messages"),response_message],
        "meta": state.get("response").get("meta"),
        "links_to_open":state.get("response").get("links_to_open"),
    }
    state["response"] = response
    return state
