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
        await asyncio.sleep(0.1)
        chunk_data_response:Response={
            "messages":[],
            "meta":state.get("response").get("meta"),
            "type":state.get("response").get("type"),
        }
        response_data = [*chunk.values()][0].get("response")
        chunk_data_response["messages"]=response_data.get("messages")[-1]
        chunk_data:State={
            "node_data":state.get("node_data"),
            "response":chunk_data_response
        }
        print("chunk_data::: ",chunk_data)
        yield f"data: {json.dumps(chunk_data)}\n\n"