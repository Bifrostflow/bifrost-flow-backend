from jose import jwt
from supabase import SupabaseException

from app.controllers.supabase_auth.create_user import check_user_exist
from app.db.supa_base import super_supabase
from app.models.projects import Project, CollaboratorInfo, CollaboratorUsersInfo, \
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
                collaborator_data=CollaboratorInfo(role="owner",uid=user_id).model_dump()
                users=CollaboratorUsersInfo(data=[collaborator_data])
                
                project.users=users.model_dump_json()
                project.nodes=""
                project.edges=""
                project.api_keys=""
                
                response_flows=super_supabase.table("flows").insert(project.model_dump()).execute()
                flow_id=response_flows.data[0].get("id")
                
                print(flow_id)
                res=APIResponse(isSuccess=True,message="Project created Successfully.",data=response_flows.data,error=None)
                return res
            except SupabaseException as e:
                print("in flow create")
                print(e)
                res=APIResponse(isSuccess=False,message="Project creation failed.",data=None,error=None)
                return res
        else:
            res = APIResponse(isSuccess=False, message="Access Denied.", data=None, error=None)
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
                response_flows=super_supabase.table("flows").update({"name":project.name,"description":project.description}).eq("id",project.id).eq("user_id",user_id).execute()
                res = APIResponse(isSuccess=True, message="Project updated Successfully.", data=response_flows.data,error=None)
                return res
            except SupabaseException as e:
                print("in flows")
                print(e)
                print(e.message)
                res=APIResponse(isSuccess=False,message="Failed to update.",data=None,error=None)
                return res
        else:
            res = APIResponse(isSuccess=False, message="Access Denied.", data=None, error=None)
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
            res = APIResponse(isSuccess=False, message="Access Denied.", data=None, error=None)
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
        data = super_supabase.table("flows").select("name","description","created_at","id").eq("user_id",user_id).execute()
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
                response=super_supabase.table("flows").update({"edges":flow_graph.edges,"nodes":flow_graph.nodes}).eq("id",flow_graph.flow_id).eq("user_id",user_id).execute()
                if len(response.data)==0:
                    res = APIResponse(isSuccess=False, message="Failed to update.", data=[],error=None)
                    return res
                else:
                    res = APIResponse(isSuccess=True, message="Graph data updated Successfully.", data=None,error=None)
                    return res
            except SupabaseException as e:
                print(e)
                res = APIResponse(isSuccess=False, message="Failed to update.", data=None, error=None)
                return res
        else:
            res = APIResponse(isSuccess=False, message="Access Denied.", data=None, error=None)
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
                response_nodes = super_supabase.table("flows").select("edges","nodes","api_keys").execute()
                print("response_nodes: ",response_nodes.data[0])
                if len(response_nodes.data)==0:
                    res = APIResponse(isSuccess=False, message="Failed to load.", data=[],error=None)
                    return res
                else:
                    res = APIResponse(isSuccess=True, message="", data=response_nodes.data[0],error=None)
                    return res
            except SupabaseException as e:
                print(e)
                res = APIResponse(isSuccess=False, message="Failed to load.", data=None, error=None)
                return res
        else:
            res = APIResponse(isSuccess=False, message="Access Denied.", data=None, error=None)
            return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res