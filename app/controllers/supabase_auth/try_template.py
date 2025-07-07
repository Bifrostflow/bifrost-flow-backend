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


def use_try_template(jwks: any, token: str, template_id: str) -> APIResponse:
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
            template=template_db.get_by_id(template_id)
            print("description:: ",template.description)
            project=Project(description=template.description,name=f"My {template.name}",users="",user_id=user_id,api_keys="{}",edges="",nodes="")
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

