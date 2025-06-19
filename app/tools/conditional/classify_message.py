from bson import ObjectId
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam, \
    ChatCompletionSystemMessageParam
from typing import List
from app.db.mongo import node_collection
from app.models.models import State, Response, ResponseModel

CLASSIFY_MESSAGE="classify_message"
async def classify_message(state:State):
    print("🤖 --- doing classification", state.get("node_data"))
    load_dotenv()
    client = OpenAI()

    next_nodes=state.get("node_data").get("next_nodes")
    print("next_nodes: ",next_nodes)
    next_node_steps_check =""
    type_map=dict()
    for p_node in next_nodes:
        node_id=p_node.split("-")[1]
        node_id_prefix=p_node.split("-")[0]
        node = await node_collection.find_one({"_id": ObjectId(node_id)}, {"_id": 0,"type":1, "what_i_do": 1})
        prefixed_type=f"{node_id_prefix}-{node.get("type")}"
        type_map[prefixed_type]=p_node

        # TODO FIX THIS PROMPT SO AI CAN DIFFERENTIATE BETWEEN TWO SAME types
        next_node_steps_check += f"\n{prefixed_type}: {node.get("what_i_do")} and this `{node_id_prefix}` as prefix"

    system_prompt="""
    You are a data classifier and your job isto get prompt and response data pattern `type` from user with `description` about that type
    and return appropriate type.
    """

    prompt=state.get("response").get("messages")[0].get("content")
    user_message=f"""
        PROMPT-START:
        Prompt: {prompt}
        PROMPT-END:
        
        -- Check for this
        {next_node_steps_check}
        """

    messages: List[ChatCompletionSystemMessageParam|ChatCompletionUserMessageParam|ChatCompletionAssistantMessageParam]=[
        ChatCompletionSystemMessageParam(role="system",content=system_prompt),
        ChatCompletionUserMessageParam(role="user",content=user_message),
        ]

    query_res = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=ResponseModel,
        messages=messages,
    )
    prompt_type=query_res.choices[0].message.parsed.type
    prompt_prefix=query_res.choices[0].message.parsed.prefix
    route_id=f"{prompt_prefix}-{prompt_type}"

    response: Response = {
        "type":type_map[route_id],
        "messages": state.get("response").get('messages'),
        "meta": state.get("response").get("meta")
    }
    state["response"] = response
    return state
