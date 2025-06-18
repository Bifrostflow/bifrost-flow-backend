from openai.types.chat import ChatCompletionUserMessageParam

from app.engine.runflow import create_graph, convert_edges_to_nodes
from app.models.models import Response, State, GraphData


async def use_run_flow(data:GraphData):
    user_flow = data.data
    nodes = await convert_edges_to_nodes(user_flow)
    print("----")
    print('-->', nodes)
    print("----")
    # return nodes
    graph = await create_graph(nodes)
    user_prompt = ChatCompletionUserMessageParam(role="user", content=data.input)
    messages = [user_prompt]
    response: Response = {
        "messages": messages,
        "type": None,
        "meta": ""
    }
    _state: State = {
        "response": response,
        "node_data": None
    }

    result = await graph.ainvoke(_state)

    print(result.get("response"))

    result_messages = result.get("response").get("messages")

    response_messages = []
    for item in result_messages:
        if item.get("role") == "assistant" and item.get("content"):
            response_messages.append(item.get("content"))

    response_data: Response = {
        "meta": result.get("response").get("meta"),
        "type": result.get("response").get("type"),
        "messages": response_messages
    }
    return response_data