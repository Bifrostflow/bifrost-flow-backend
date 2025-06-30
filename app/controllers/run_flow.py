import ast
from langgraph.graph.state import CompiledStateGraph
from openai.types.chat import ChatCompletionUserMessageParam
from starlette.responses import StreamingResponse
import asyncio
import json

from supabase import SupabaseException
from app.controllers.engine.runflow import create_graph, convert_edges_to_nodes
from app.controllers.supabase_auth.create_user import check_user_exist
from app.models.models import Response, State, GraphData
from jose import jwt
from app.db.supa_base import super_supabase

from app.models.response import APIResponse

async def use_run_flow(jwks:any,token:str,data:GraphData):
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(isSuccess=False, message="Authorization failed.", data=None, error=None)
            return res
        exist = check_user_exist(jwks,token)
        if exist.isExist:
            collaborators_data=super_supabase.table("collaborators").select("users").eq("flow_id",data.flow_id).execute()
            c_users=ast.literal_eval(collaborators_data.data[0].get("users"))
            users=c_users.get("data")
            has_access = any(user.get("uid") == user_id for user in users)
            
            if has_access:
                user_flow = data.data
                nodes = await convert_edges_to_nodes(user_flow)

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
                    "node_data": None,
                    "ui_response":"Started Graph"
                }

                stream = stream_graph(graph,_state)
                return StreamingResponse(stream, media_type="text/event-stream")
            else:
                res = APIResponse(isSuccess=False, message="Access denied.", data=None, error=None)
            return res    
        else:
            res = APIResponse(isSuccess=False, message="User not exist", data=None, error=None)
            return res
    except SupabaseException as e:
         res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
         return res


async def stream_graph(graph:CompiledStateGraph,state:State):
    result = graph.astream(state, stream_mode="updates")
    async for chunk in result:
        await asyncio.sleep(0.1)
        chunked_state=[*chunk.values()][0]
        response_data = chunked_state.get("response")
        response_data_ui_message = chunked_state.get("ui_response")
        meta_for_me={}
        for meta in chunked_state.get("response").get("meta"):
            meta_json=json.loads(meta)
            if meta_json.get("node_id")==chunked_state.get("node_data").get("node_graph_id"):
                meta_for_me=meta_json
                break
        
        chunk_data_response:Response={
            "messages":[],
            "meta":meta_for_me,
            "type":chunked_state.get("response").get("type"),
        }
        chunk_data_response["messages"]=response_data.get("messages")[-1]
        chunk_data:State={
            "node_data":chunked_state.get("node_data"),
            "response":chunk_data_response,
            "ui_response":response_data_ui_message
        }
        yield f"data: {json.dumps(chunk_data)}\n\n"