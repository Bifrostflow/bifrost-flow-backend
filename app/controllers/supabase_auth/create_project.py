from jose import jwt
from supabase import SupabaseException

from app.controllers.supabase_auth.create_user import check_user_exist
from app.db.supa_base import super_supabase
from app.models.projects import Project, EdgeDB, NodeDB, CollaboratorDB, CollaboratorInfo, CollaboratorUsersInfo, \
    EditProject, UpdateFlowGraph
from app.models.response import APIResponse

def create_supabase_project(jwks:any,token:str,project:Project)->APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(isSuccess=False, message="Authorization failed.", data=None, error=None)
            return res
        exist = check_user_exist(jwks,token)
        print(exist.isExist)
        if exist.isExist:
            project.user_id=user_id
            try:
                response_flows=super_supabase.table("flows").insert(project.model_dump()).execute()
                flow_id=response_flows.data[0].get("id")
                print(flow_id)
            except SupabaseException as e:
                print("in flows")
                print(e)
                print(e.message)
                res=APIResponse(isSuccess=False,message="Project creation failed.",data=None,error=None)
                return res

            try:
                edge=EdgeDB(api_keys="",flow_id=flow_id,data="")
                edge.user_id=user_id
                response_edges=super_supabase.table("edges").insert(edge.model_dump()).execute()
            except SupabaseException as e:
                print("in edges")
                print(e)
                print(e.message)
                res=APIResponse(isSuccess=False,message="Project creation failed.",data=None,error=None)
                return res
            try:
                node=NodeDB(flow_id=flow_id,data="")
                node.user_id = user_id
                response_nodes=super_supabase.table("nodes").insert(node.model_dump()).execute()
            except SupabaseException as e:
                print("in nodes")
                print(e)
                print(e.message)
                res=APIResponse(isSuccess=False,message="Project creation failed.",data=None,error=None)
                return res
            try:
                collaborator_data=CollaboratorInfo(role="owner",uid=user_id).model_dump()
                users=CollaboratorUsersInfo(data=[collaborator_data])
                collaborator=CollaboratorDB(flow_id=flow_id,users=f"{users.model_dump()}")
                collaborator.user_id = user_id
                response_collaborators=super_supabase.table("collaborators").insert(collaborator.model_dump()).execute()
            except SupabaseException as e:
                print("in collaborator")
                print(e)
                print(e.message)
                res=APIResponse(isSuccess=False,message="Project creation failed.",data=None,error=None)
                return res

            res=APIResponse(isSuccess=True,message="Project created Successfully.",data=response_flows.data,error=None)
            return res
        else:
         res = APIResponse(isSuccess=False, message="User not exist", data=None, error=None)
         return res
    except SupabaseException as e:
         res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
         return res

def edit_supabase_project(jwks:any,token:str,project:EditProject)->APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(isSuccess=False, message="Authorization failed.", data=None, error=None)
            return res
        exist = check_user_exist(jwks,token)
        if exist.isExist:
            try:
                response_flows=super_supabase.table("flows").update(project.model_dump()).eq("id",project.id).eq("user_id",user_id).execute()
                res = APIResponse(isSuccess=True, message="Project updated Successfully.", data=response_flows.data,
                                  error=None)
                return res
            except SupabaseException as e:
                print("in flows")
                print(e)
                print(e.message)
                res=APIResponse(isSuccess=False,message="Failed to update.",data=None,error=None)
                return res
        else:
         res = APIResponse(isSuccess=False, message="User not exist", data=None, error=None)
         return res
    except SupabaseException as e:
         res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
         return res

def delete_supabase_project(jwks:any,token:str,flow_id:str)->APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(isSuccess=False, message="Authorization failed.", data=None, error=None)
            return res
        exist = check_user_exist(jwks,token)
        print(exist.isExist)
        if exist.isExist:

            try:
                super_supabase.table("flows").delete().eq("id",flow_id).eq("user_id",user_id).execute()
                res = APIResponse(isSuccess=True, message="Project deleted Successfully.", data=None, error=None)
                return res
            except SupabaseException as e:
                print("in flows")
                print(e)
                print(e.message)
                res=APIResponse(isSuccess=False,message="Project deletion failed.",data=None,error=None)
                return res


        else:
         res = APIResponse(isSuccess=False, message="User not exist", data=None, error=None)
         return res
    except SupabaseException as e:
         res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
         return res

def get_supabase_projects(jwks:any,token:str)->APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(isSuccess=False, message="Authorization failed.", data=None, error=None)
            return res
        data = super_supabase.rpc("get_flow_status_by_user", {"uid": user_id}).execute()
        # data = super_supabase.table("flows").select("*").eq("user_id",user_id).execute()
        res = APIResponse(isSuccess=True, message="", data=data.data, error=None)
        return res
    except SupabaseException as e:
         res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
         return res

def get_supabase_project(jwks:any,token:str,flow_id:str)->APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(isSuccess=False, message="Authorization failed.", data=None, error=None)
            return res
        data = super_supabase.table("flows").select("*").eq("id",flow_id).eq("user_id",user_id).execute()
        res = APIResponse(isSuccess=True, message="", data=data.data, error=None)
        return res
    except SupabaseException as e:
         res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
         return res

def update_supabase_nodes(jwks:any,token:str,flow_graph:UpdateFlowGraph)->APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(isSuccess=False, message="Authorization failed.", data=None, error=None)
            return res
        exist = check_user_exist(jwks, token)
        if exist.isExist:
            try:
                response_nodes = super_supabase.table("nodes").update({"data":flow_graph.nodes}).eq("flow_id",flow_graph.flow_id).eq("user_id",user_id).execute()
                response_edges = super_supabase.table("edges").update({"data":flow_graph.edges}).eq("flow_id",flow_graph.flow_id).eq("user_id",user_id).execute()
                if len(response_nodes.data)==0 and len(response_edges.data)==0:
                    res = APIResponse(isSuccess=False, message="Failed to update.", data=[],
                                      error=None)
                    return res
                else:
                    res = APIResponse(isSuccess=True, message="Graph data updated Successfully.", data=None,
                                      error=None)
                    return res
            except SupabaseException as e:
                print(e)
                res = APIResponse(isSuccess=False, message="Failed to update.", data=None, error=None)
                return res
        else:
            res = APIResponse(isSuccess=False, message="User not exist", data=None, error=None)
            return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res

def load_supabase_nodes(jwks:any,token:str,flow_id:str)->APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(isSuccess=False, message="Authorization failed.", data=None, error=None)
            return res
        exist = check_user_exist(jwks, token)
        if exist.isExist:
            try:
                response_nodes = super_supabase.rpc("get_graph_for_flow",{ "u_id": user_id,"f_id":flow_id }).execute()
                print("response_nodes: ",response_nodes.data[0])
                if len(response_nodes.data)==0:
                    res = APIResponse(isSuccess=False, message="Failed to load.", data=[],
                                      error=None)
                    return res
                else:
                    res = APIResponse(isSuccess=True, message="", data=response_nodes.data[0],
                                      error=None)
                    return res
            except SupabaseException as e:
                print(e)
                res = APIResponse(isSuccess=False, message="Failed to load.", data=None, error=None)
                return res
        else:
            res = APIResponse(isSuccess=False, message="User not exist", data=None, error=None)
            return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res