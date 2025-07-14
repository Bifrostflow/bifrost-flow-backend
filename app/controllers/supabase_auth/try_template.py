from fastapi import HTTPException
from jose import jwt
from supabase import SupabaseException

from app.controllers.supabase_auth.create_user import check_user_exist
from app.db import template_data
from app.db.supa_base import super_supabase
from app.models.projects import (
    Project,
    CollaboratorInfo,
    CollaboratorUsersInfo,
)
from app.models.response import APIResponse
from app.db.template_data import template_db
from app.controllers.supabase_auth.create_project import subscription_plan_limit, upload_flow_snap
from app.utils import fallback_snap


def use_try_template(jwks: any, token: str, template_id: str) -> APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id:str = token_data["sub"]
        if not user_id:
            res = APIResponse(
                isSuccess=False, message="Authorization failed.", data=None, error=None
            )
            return res
        
        exist = check_user_exist(jwks, token)

        print(exist.isExist)
        if exist.isExist:
            # check if user has bought this template
            template_data=template_db.get_by_id(template_id)
            if template_data.price>0:
                receipt=f"{template_data.product_id}_{user_id.split("_")[1]}"
                receipt_data=super_supabase.table("payments").select("status").eq("receipt",receipt).execute()
                print(receipt_data,receipt)
                if(len(receipt_data.data)>0):
                    if receipt_data.data[0].get("status") !="captured":
                        res = APIResponse(
                            isSuccess=False, message="Incomplete payment.", data={"status":"re-initiate-template-payment","receipt":receipt}, error=None
                        )
                        return res
                else:
                    res = APIResponse(
                    isSuccess=False, message="Template is not purchased.", data={"status":"show-template-pay"}, error=None
                    )
                    return res 
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
            print("Current project count:", current_project_count)
            if current_project_count >= project_limit:
                res = APIResponse(
                    isSuccess=False,
                    message=f"Project limit reached. You can only have {project_limit} projects.",
                    data=None,
                    error=None,
                )
                return res
            template=template_db.get_by_id(template_id)
            print("description:: ",template.description)
            project=Project(description=template.description,name=f"My {template.name}",users="",user_id=user_id,api_keys="{}",edges="",nodes="", snap_path="")
            try:
                collaborator_data = CollaboratorInfo(
                    role="owner", uid=user_id
                ).model_dump()
                users = CollaboratorUsersInfo(data=[collaborator_data])
                print("-->",template.graph)
                print(template.graph.edges)
                project.users = users.model_dump_json()
                project.nodes = template.graph.nodes
                project.edges = template.graph.edges
                project.api_keys = ""
                project.snap_path = ""


                response_flows = (
                    super_supabase.table("flows").insert(project.model_dump()).execute()
                )
                flow_id = response_flows.data[0].get("id")
                snap_path = upload_flow_snap(flow_id, fallback_snap.fallback)
                if snap_path:
                    # Update the flow with the snap path
                    super_supabase.table("flows").update({"snap_path": snap_path}).eq("id", flow_id).execute()
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

