from langgraph.graph.state import CompiledStateGraph
from openai.types.chat import ChatCompletionUserMessageParam
import json
import asyncio
from fastapi.responses import StreamingResponse, FileResponse

from app.engine.runflow import create_graph, convert_edges_to_nodes
from app.models.models import Response, State, GraphData


async def use_run_flow(data:GraphData):
    user_flow = data.data
    nodes = await convert_edges_to_nodes(user_flow)

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

    # result = graph.astream(_state,stream_mode="messages")
    # async for chunk in result:
    #     yield f"data: {json.dumps({'chunk': {chunk}})}\n\n"
    #     print(chunk)
    stream = stream_graph(graph,_state)
    return StreamingResponse(stream, media_type="text/event-stream")
    # result_messages = result.get("response").get("messages")


    # response_messages = []
    # for item in result_messages:
    #     if item.get("role") == "assistant" and item.get("content"):
    #         response_messages.append(item.get("content"))
    #
    # response_data: Response = {
    #     "meta": result.get("response").get("meta"),
    #     "type": result.get("response").get("type"),
    #     "messages": response_messages
    # }
    # return response_data

async def stream_graph(graph:CompiledStateGraph,state:State):
    result = graph.astream(state, stream_mode="updates")
    async for chunk in result:
        print('==>',chunk)
        await asyncio.sleep(0.1)
        yield f"data: {json.dumps({'chunk': "working"})}\n\n"