from datetime import datetime, timezone
import webbrowser
from fastapi import HTTPException
from jose import jwt
from pydantic import Base64Encoder
from supabase import SupabaseException

from app.controllers.supabase_auth.create_user import check_user_exist
from app.db.supa_base import super_supabase
from app.models.projects import (
    Project,
    CollaboratorInfo,
    CollaboratorUsersInfo,
    EditProject,
    UpdateFlowGraph,
    UpdateFlowKeys,
)
from app.models.response import APIResponse
from app.utils import fallback_snap
from app.utils.projct_name_genrator import generate_norse_project_name

def subscription_plan_limit(plan: str) -> int:
    """
    Returns the project limit based on the user's subscription plan.
    """
    plan_limits = {
        "mortal": 5,
        "demigod": 20,
        "deity": 50
    }
    return plan_limits.get(plan, 0)  # Default to 0 if plan is not recognized

def create_supabase_project(jwks: any, token: str, project: Project) -> APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(
                isSuccess=False, message="Authorization failed.", data=None, error=None
            )
            return res
        exist = check_user_exist(jwks, token)
        # print(exist.isExist)
        if exist.isExist:
            # Check if the user has reached their project limit
            user_data = (
                super_supabase.table("users")
                .select("user_plan")
                .eq("clerk_id", user_id)
                .execute()
            )
            plan = user_data.data[0].get("user_plan")
            project_limit = subscription_plan_limit(plan)
            current_project_count = len((
                super_supabase.table("flows")
                .select("id")
                .eq("user_id", user_id)
                .execute()
            ).data)
            # print("Current project count:", current_project_count)
            if current_project_count >= project_limit:
                res = APIResponse(
                    isSuccess=False,
                    message=f"Project limit reached. You can only have {project_limit} projects.",
                    data=None,
                    error=None,
                )
                return res
            
            project.user_id = user_id
            try:
                collaborator_data = CollaboratorInfo(
                    role="owner", uid=user_id
                ).model_dump()
                users = CollaboratorUsersInfo(data=[collaborator_data])
                # upload flow snap
                # Initialize nodes, edges, and api_keys as empty strings
                project.users = users.model_dump_json()
                project.nodes = ""
                project.edges = ""
                project.api_keys = ""
                project.name=generate_norse_project_name()
                project.description=""
                response_flows = (
                    super_supabase.table("flows").insert(project.model_dump()).execute()
                )
                flow_id = response_flows.data[0].get("id")
                # If the flow snap is provided, upload it
                snap_path = upload_flow_snap(flow_id, fallback_snap.fallback)
                if snap_path:
                    # Update the flow with the snap path
                    super_supabase.table("flows").update({"snap_path": snap_path}).eq("id", flow_id).execute()
                res = APIResponse(
                    isSuccess=True,
                    message="Project created Successfully.",
                    data=response_flows.data,
                    error=None,
                )
                return res
            except SupabaseException as e:
                # print("in flow create")
                # print(e)
                res = APIResponse(
                    isSuccess=False,
                    message="Project creation failed.",
                    data=None,
                    error=None,
                )
                return res
        else:
            res = APIResponse(
                isSuccess=False, message="Access Denied.", data=None, error=None
            )
            return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res


def edit_supabase_project(jwks: any, token: str, project: EditProject) -> APIResponse:
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
            try:
                response_flows = (
                    super_supabase.table("flows")
                    .update({"name": project.name, "description": project.description})
                    .eq("id", project.id)
                    .eq("user_id", user_id)
                    .execute()
                )
                res = APIResponse(
                    isSuccess=True,
                    message="Project updated Successfully.",
                    data=response_flows.data,
                    error=None,
                )
                return res
            except SupabaseException as e:
                # print("in flows")
                # print(e)
                # print(e.message)
                res = APIResponse(
                    isSuccess=False, message="Failed to update.", data=None, error=None
                )
                return res
        else:
            res = APIResponse(
                isSuccess=False, message="Access Denied.", data=None, error=None
            )
            return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res


def delete_supabase_project(jwks: any, token: str, flow_id: str) -> APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(
                isSuccess=False, message="Authorization failed.", data=None, error=None
            )
            return res
        exist = check_user_exist(jwks, token)
        # print(exist.isExist)
        if exist.isExist:
            try:
                super_supabase.table("flows").delete().eq("id", flow_id).eq(
                    "user_id", user_id
                ).execute()
                res = APIResponse(
                    isSuccess=True,
                    message="Project deleted Successfully.",
                    data=None,
                    error=None,
                )
                return res
            except SupabaseException as e:
                # print("in flows")
                # print(e)
                # print(e.message)
                res = APIResponse(
                    isSuccess=False,
                    message="Project deletion failed.",
                    data=None,
                    error=None,
                )
                return res
        else:
            res = APIResponse(
                isSuccess=False, message="Access Denied.", data=None, error=None
            )
            return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res


def get_supabase_projects(jwks: any, token: str) -> APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(
                isSuccess=False, message="Authorization failed.", data=None, error=None
            )
            return res
        user_data = (
            super_supabase.table("users").select("user_plan").eq("clerk_id", user_id).execute()
        )
        plan=user_data.data[0].get("user_plan")
        project_limit=0
        if plan=="mortal":
            project_limit=5
        elif plan=="demigod":
            project_limit=20
        elif plan=="deity":
            project_limit=50
        
        data = (
            super_supabase.table("flows")
            .select("name", "description", "updated_at", "id","snap_path")
            .eq("user_id", user_id).order("updated_at", desc=True)  
            .execute()
        )
        new_data=[]
        for item in data.data:
            new_item=item
            if new_item.get("snap_path"):
                new_item_image_url=super_supabase.storage.from_("flow-snaps").get_public_url(new_item.get("snap_path"))
                new_item["snap_path"]=new_item_image_url
            else:
                new_item["snap_path"]=""
            # print(new_item)
            new_data.append(new_item)
        response_data={
            "projects": new_data,
            "project_limit": project_limit,
            "current_project_count": len(new_data)
        }
        res = APIResponse(isSuccess=True, message="", data=response_data, error=None)
        return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res


def get_supabase_project(jwks: any, token: str, flow_id: str) -> APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(
                isSuccess=False, message="Authorization failed.", data=None, error=None
            )
            return res
        data = (
            super_supabase.table("flows")
            .select("*")
            .eq("id", flow_id)
            .eq("user_id", user_id)
            .execute()
        )
        res = APIResponse(isSuccess=True, message="", data=data.data, error=None)
        return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res

def upload_flow_snap(flow_id:str,snap_string:str):
    try:
        bucket_path=f"{flow_id}.png"
        base64=snap_string.split("base64,")[1]
        buffer=Base64Encoder.decode(base64)
        flow_data_bucket=super_supabase.storage.from_("flow-snaps").upload(path=bucket_path,file=buffer,file_options={"cache-control": "3600", "upsert": "true","content-type":"image/png"})
        # print(flow_data_bucket)
        return flow_data_bucket.path
    except SupabaseException as e:
        # print(e)
        return None
    


def update_supabase_nodes(
    jwks: any, token: str, flow_graph: UpdateFlowGraph
) -> APIResponse:
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
            try:
                flow_data_bucket_path=upload_flow_snap(flow_graph.flow_id,flow_graph.snap)
                now = datetime.now(timezone.utc)
                response = (
                    super_supabase.table("flows")
                    .update({"edges": flow_graph.edges, "nodes": flow_graph.nodes,"updated_at":now.isoformat(sep=' ', timespec='microseconds'),"snap_path":flow_data_bucket_path})
                    .eq("id", flow_graph.flow_id)
                    .eq("user_id", user_id)
                    .execute()
                )
                if len(response.data) == 0:
                    res = APIResponse(
                        isSuccess=False,
                        message="Failed to update.",
                        data=[],
                        error=None,
                    )
                    return res
                else:
                    res = APIResponse(
                        isSuccess=True,
                        message="Graph data updated Successfully.",
                        data=None,
                        error=None,
                    )
                    return res
            except SupabaseException as e:
                # print(e)
                res = APIResponse(
                    isSuccess=False, message="Failed to update.", data=None, error=None
                )
                return res
        else:
            res = APIResponse(
                isSuccess=False, message="Access Denied.", data=None, error=None
            )
            return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res


def load_supabase_nodes(jwks: any, token: str, flow_id: str) -> APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(
                isSuccess=False, message="Authorization failed.", data=None, error=None
            )
            return res
        try:
            response_nodes_for_user_id = (
                super_supabase.table("flows")
                .select("user_id")
                .eq("id", flow_id)
                .execute()
            )
            # print(response_nodes_for_user_id, user_id)
            if not response_nodes_for_user_id.data[0].get("user_id") == user_id:
                raise HTTPException(status_code=403, detail="Unauthorized")
            response_nodes = (
                super_supabase.table("flows")
                .select("edges", "nodes", "api_keys","name")
                .eq("id", flow_id)
                .eq("user_id", user_id)
                .execute()
            )
            if len(response_nodes.data) == 0:
                res = APIResponse(
                    isSuccess=False, message="Failed to load.", data=[], error=None
                )
                return res
            else:
                # print("ALL GOOD")
                # print(response_nodes.data[0])
                res = APIResponse(
                    isSuccess=True,
                    message="",
                    data=response_nodes.data[0],
                    error=None,
                )
                return res
        except SupabaseException as e:
            # print(e)
            res = APIResponse(
                isSuccess=False, message="Failed to load.", data=None, error=None
            )
            return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res


def update_supabase_flow_keys(
    jwks: any, token: str, flow_keys: UpdateFlowKeys
) -> APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(
                isSuccess=False, message="Authorization failed.", data=None, error=None
            )
            return res
        try:
            response = (
                super_supabase.table("flows")
                .update({"api_keys": flow_keys.apiKeys})
                .eq("id", flow_keys.flow_id)
                .eq("user_id", user_id)
                .execute()
            )
            if len(response.data) == 0:
                res = APIResponse(
                    isSuccess=False, message="Failed to update.", data=[], error=None
                )
                return res
            else:
                res = APIResponse(
                    isSuccess=True,
                    message="Graph keys updated Successfully.",
                    data=None,
                    error=None,
                )
                return res
        except SupabaseException as e:
            # print(e)
            res = APIResponse(
                isSuccess=False, message="Failed to update.", data=None, error=None
            )
            return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res

def get_supabase_flow_docs(
    jwks: any, token: str, flow_id: str
) -> APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(
                isSuccess=False, message="Authorization failed.", data=None, error=None
            )
            return res
        try:
            # get flow path
            data = (super_supabase.storage.from_("flow-data").list(flow_id,{"limit":5,"offset":0,"sortBy":{"column": "created_at", "order": "desc"}}))
            # get all docs for that path
            res = APIResponse(
                    isSuccess=True,
                    message="",
                    data=data,
                    error=None,
                )
            return res
        except SupabaseException as e:
            # print(e)
            res = APIResponse(
                isSuccess=False, message="Failed to get data.", data=None, error=None
            )
            return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res

def open_supabase_flow_doc(
    jwks: any, token: str, flow_id: str,name: str
) -> APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(
                isSuccess=False, message="Authorization failed.", data=None, error=None
            )
            return res
        try:
            # get flow path
            data = (super_supabase.storage.from_("flow-data").create_signed_url(f"{flow_id}/{name}",expires_in=60000))
            webbrowser.open(data.get("signedUrl"))
            # get all docs for that path
            res = APIResponse(
                    isSuccess=True,
                    message="",
                    data=None,
                    error=None,
                )
            return res
        except SupabaseException as e:
            # print(e)
            res = APIResponse(
                isSuccess=False, message="Failed to get data.", data=None, error=None
            )
            return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res
