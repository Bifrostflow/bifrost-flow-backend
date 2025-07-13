import ast
from langgraph.constants import START
from langgraph.graph.state import CompiledStateGraph
from openai.types.chat import ChatCompletionUserMessageParam
from starlette.responses import StreamingResponse
import asyncio
import json

from supabase import SupabaseException
from app.controllers.engine.runflow import create_graph, convert_edges_to_nodes
from app.controllers.get_system_node_by_id import get_node_ui_loading_message
from app.controllers.supabase_auth.create_user import check_user_exist
from app.models.models import Response, State, GraphData
from jose import jwt
from app.db.supa_base import super_supabase

from app.models.response import APIResponse


async def use_run_flow(jwks: any, token: str, data: GraphData):
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(
                isSuccess=False, message="Authorization failed.", data=None, error=None
            )
            return res
        exist = check_user_exist(jwks, token)
        if exist.isExist:

            collaborators_data = (
                super_supabase.table("flows")
                .select("users")
                .eq("id", data.flow_id)
                .eq("user_id", user_id)
                .execute()
            )
            c_users = ast.literal_eval(collaborators_data.data[0].get("users"))
            users = c_users.get("data")
            has_access = any(user.get("uid") == user_id for user in users)

            if has_access:
                user_flow = data.data
                nodes = await convert_edges_to_nodes(user_flow)

                # return nodes
                graph = await create_graph(nodes)
                user_prompt = ChatCompletionUserMessageParam(
                    role="user", content=data.input
                )
                messages = [user_prompt]
                response: Response = {"messages": messages, "type": None, "meta": []}
                # fetch key from user
                key_response = (
                    super_supabase.table("flows")
                    .select("api_keys")
                    .eq("id", data.flow_id)
                    .eq("user_id", user_id)
                    .execute()
                )
                keys_data = {}
                if key_response.data[0].get("api_keys"):
                    keys_data: dict[str, str] = json.loads(
                        key_response.data[0].get("api_keys")
                    )
                key_id=""
                source_id=""

                for edge in graph.get_graph().edges:
                    if edge.source==START:
                        key_id=edge.target
                        for d in data.data:
                            if d.get("target")==key_id:
                                source_id=d.get("source")
                _state: State = {
                    "response": response,
                    "node_data": {"node_graph_id":source_id,"next_nodes":[key_id],"node_input":""},
                    "ui_response":"Preparing Graph",
                    "flow_id": data.flow_id,
                    "user_id": user_id,
                    "api_keys": keys_data,
                }
                stream = stream_graph(graph, _state, flow_id=data.flow_id)
                return StreamingResponse(stream, media_type="text/event-stream")
            else:
                res = APIResponse(
                    isSuccess=False, message="Access denied.", data=None, error=None
                )
            return res
        else:
            res = APIResponse(
                isSuccess=False, message="User not exist", data=None, error=None
            )
            return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res


async def stream_graph(graph: CompiledStateGraph, state: State, flow_id: str):
    try:
        print("STATE:: ",state)
        chunk_data: State = {
                "node_data": state.get("node_data"),
                "response": {
                            "messages": {"role":"assistant","content":"Query received."},
                            "meta": {},
                            "type": "",
                        },
                "ui_response": get_node_ui_loading_message(state.get("node_data").get("next_nodes")[0]),
                "flow_id": flow_id,
                "user_id": state.get("user_id"),
            }
        print("chunk_data: ",chunk_data)
        yield f"data: {json.dumps(chunk_data)}\n\n"

        result = graph.astream(state, stream_mode="updates")
        async for chunk in result:
            await asyncio.sleep(0.1)
            chunked_state = [*chunk.values()][0]
            response_data = chunked_state.get("response")
            response_data_ui_message = chunked_state.get("ui_response")
            meta_for_me = {}
            for meta in chunked_state.get("response").get("meta"):
                meta_json = json.loads(meta)
                if meta_json.get("node_id") == chunked_state.get("node_data").get(
                    "node_graph_id"
                ):
                    meta_for_me = meta_json
                    break

            chunk_data_response: Response = {
                "messages": [],
                "meta": meta_for_me,
                "type": chunked_state.get("response").get("type"),
            }
            chunk_data_response["messages"] = response_data.get("messages")[-1]
            chunk_data: State = {
                "node_data": chunked_state.get("node_data"),
                "response": chunk_data_response,
                "ui_response": response_data_ui_message,
                "flow_id": flow_id,
                "user_id": state.get("user_id"),
            }
            yield f"data: {json.dumps(chunk_data)}\n\n"
    except Exception as e:
        error_message = "Something went wrong"
        if e:
            error_message = f"{e}"
        print(e)
        chunk_data: State = {
            "ui_response": error_message,
            "flow_id": flow_id,
            "user_id": state.get("user_id"),
            "error": error_message,
        }
        yield f"data: {json.dumps(chunk_data)}\n\n"
