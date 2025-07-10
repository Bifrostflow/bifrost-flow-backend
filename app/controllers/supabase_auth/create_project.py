from datetime import datetime, timezone
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
        print(exist.isExist)
        if exist.isExist:
            project.user_id = user_id
            try:
                collaborator_data = CollaboratorInfo(
                    role="owner", uid=user_id
                ).model_dump()
                users = CollaboratorUsersInfo(data=[collaborator_data])

                project.users = users.model_dump_json()
                project.nodes = ""
                project.edges = ""
                project.api_keys = ""

                response_flows = (
                    super_supabase.table("flows").insert(project.model_dump()).execute()
                )
                flow_id = response_flows.data[0].get("id")

                print(flow_id)
                res = APIResponse(
                    isSuccess=True,
                    message="Project created Successfully.",
                    data=response_flows.data,
                    error=None,
                )
                return res
            except SupabaseException as e:
                print("in flow create")
                print(e)
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
                print("in flows")
                print(e)
                print(e.message)
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
        print(exist.isExist)
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
                print("in flows")
                print(e)
                print(e.message)
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
            .eq("user_id", user_id)
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
            print(new_item)
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
                bucket_path=f"{flow_graph.flow_id}.png"
                base64=flow_graph.snap.split("base64,")[1]
                buffer=Base64Encoder.decode(base64)
                flow_data_bucket=super_supabase.storage.from_("flow-snaps").upload(path=bucket_path,file=buffer,file_options={"cache-control": "3600", "upsert": "true","content-type":"image/png"})
                print(flow_data_bucket)
                now = datetime.now(timezone.utc)
                response = (
                    super_supabase.table("flows")
                    .update({"edges": flow_graph.edges, "nodes": flow_graph.nodes,"updated_at":now.isoformat(sep=' ', timespec='microseconds'),"snap_path":flow_data_bucket.path})
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
                print(e)
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
            print(response_nodes_for_user_id, user_id)
            if not response_nodes_for_user_id.data[0].get("user_id") == user_id:
                raise HTTPException(status_code=403, detail="Unauthorized")
            response_nodes = (
                super_supabase.table("flows")
                .select("edges", "nodes", "api_keys")
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
                print("ALL GOOD")
                print(response_nodes.data[0])
                res = APIResponse(
                    isSuccess=True,
                    message="",
                    data=response_nodes.data[0],
                    error=None,
                )
                return res
        except SupabaseException as e:
            print(e)
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
            print(e)
            res = APIResponse(
                isSuccess=False, message="Failed to update.", data=None, error=None
            )
            return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res
