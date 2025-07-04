from dotenv import load_dotenv
from fastapi_clerk_auth import HTTPAuthorizationCredentials
from supabase import SupabaseException

from app.controllers.supabase_auth.create_project import (
    load_supabase_nodes,
    update_supabase_flow_keys,
    update_supabase_nodes,
)
from app.models.projects import UpdateFlowGraph, UpdateFlowKeys
import os
import requests

load_dotenv()


async def update_nodes_controller(
    flow_graph: UpdateFlowGraph, credentials: HTTPAuthorizationCredentials
):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return update_supabase_nodes(jwks, credentials.credentials, flow_graph)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}


async def update_flow_keys_controller(
    flow_keys: UpdateFlowKeys, credentials: HTTPAuthorizationCredentials
):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return update_supabase_flow_keys(jwks, credentials.credentials, flow_keys)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}


async def load_nodes_controller(
    flow_id: str, credentials: HTTPAuthorizationCredentials
):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return load_supabase_nodes(jwks, credentials.credentials, flow_id)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}
