from langgraph.graph.state import CompiledStateGraph
from openai.types.chat import ChatCompletionUserMessageParam
from starlette.responses import StreamingResponse
import asyncio
import json
from app.engine.runflow import create_graph, convert_edges_to_nodes
from app.models.models import Response, State, GraphData


async def use_run_flow(data:GraphData):
    user_flow = data.data
    nodes = await convert_edges_to_nodes(user_flow)
    print("----")
    print('-->', nodes)
    print("----")
    # return tools

    # return nodes
    graph = await create_graph(nodes)
    user_prompt = ChatCompletionUserMessageParam(role="user", content=data.input)
    messages = [user_prompt]
    response: Response = {
        "messages": messages,
        "type": None,
        "meta": []
    }
    _state: State = {
        "response": response,
        "node_data": None
    }

    stream = stream_graph(graph,_state)
    return StreamingResponse(stream, media_type="text/event-stream")


async def stream_graph(graph:CompiledStateGraph,state:State):
    result = graph.astream(state, stream_mode="updates")
    async for chunk in result:
        print('==>',chunk)
        await asyncio.sleep(0.1)
        yield f"data: {json.dumps({'chunk': "working"})}\n\n"