from gotrue.helpers import model_dump
from jose import jwt
from pydantic import BaseModel
from supabase import SupabaseException

from app.controllers.supabase_auth.create_user import check_user_exist
from app.db.supa_base import super_supabase
from app.models.projects import Project, EdgeDB, NodeDB, CollaboratorDB, CollaboratorInfo, CollaboratorUsersInfo, \
    EditProject
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
                response_edges=super_supabase.table("edges").insert(edge.model_dump()).execute()
            except SupabaseException as e:
                print("in edges")
                print(e)
                print(e.message)
                res=APIResponse(isSuccess=False,message="Project creation failed.",data=None,error=None)
                return res
            try:
                node=NodeDB(flow_id=flow_id,data="")
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
         res = APIResponse(isSuccess=False, message=f"User not exist", data=None, error=None)
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
                response_flows=super_supabase.table("flows").update(project.model_dump()).eq("user_id",user_id).eq("id",project.id).execute()
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
         res = APIResponse(isSuccess=False, message=f"User not exist", data=None, error=None)
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
                response_flows=super_supabase.table("flows").delete().eq("user_id",user_id).eq("id",flow_id).execute()
                res = APIResponse(isSuccess=True, message="Project deleted Successfully.", data=None, error=None)
                return res
            except SupabaseException as e:
                print("in flows")
                print(e)
                print(e.message)
                res=APIResponse(isSuccess=False,message="Project deletion failed.",data=None,error=None)
                return res


        else:
         res = APIResponse(isSuccess=False, message=f"User not exist", data=None, error=None)
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
        # data = super_supabase.rpc("get_flow_status_by_user", {"uid": user_id}).execute()
        data = super_supabase.table("flows").select("*").eq("id",flow_id).execute()
        res = APIResponse(isSuccess=True, message="", data=data.data, error=None)
        return res
    except SupabaseException as e:
         res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
         return res

