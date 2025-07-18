import os

from fastapi import FastAPI, Depends, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi_clerk_auth import (
    ClerkHTTPBearer,
    ClerkConfig,
    HTTPAuthorizationCredentials,
)
from pydantic import BaseModel
import requests
from supabase import SupabaseException
from jose import jwt
from app.controllers.engine.tools.speech.transcribe import transcribe_audio_controller
from app.controllers.flow import (
    get_flow_docs_controller,
    load_nodes_controller,
    open_flow_docs_controller,
    update_flow_keys_controller,
    update_nodes_controller,
)
from app.controllers.get_system_node_by_id import use_get_system_node_by_id
from app.controllers.get_system_nodes import use_get_system_nodes
from app.controllers.get_templates import use_get_template_by_id, use_get_templates

from app.controllers.payments.create_order import create_order_controller
from app.controllers.payments.verify_payment import verify_payment_controller
from app.controllers.run_flow import use_run_flow

from app.controllers.supabase_auth.create_project import (
    create_supabase_project,
    get_supabase_projects,
    delete_supabase_project,
    get_supabase_project,
    edit_supabase_project,
)
from app.controllers.supabase_auth.try_template import use_try_template
from app.controllers.user.update_user import update_user_controller
from app.models.models import ClerkUser, GraphData
from app.controllers.supabase_auth.create_user import (
    create_supabase_user,
    check_user_exist,
)
from app.models.payment_models import PaymentVerificationRequest, TemplateOrderRequest
from app.models.projects import Project, EditProject, UpdateFlowGraph, UpdateFlowKeys

# Use your Clerk JWKS endpoint
clerk_config = ClerkConfig(jwks_url=os.getenv("JWKS"))

clerk_auth_guard = ClerkHTTPBearer(config=clerk_config)


class UserInfo(BaseModel):
    name: str


app = FastAPI(openapi_prefix="/api")
load_dotenv()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://bifrostflow.com/",
        "bifrostflow.com/",
        os.getenv("LOCALHOST"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/test")
async def test():
    return {"test": "test"}


@app.get("/system-tools")
async def get_system_nodes(credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),):
    return use_get_system_nodes()

@app.get("/templates")
async def get_templates(credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    return use_get_templates()

@app.get("/template")
async def get_templates(template_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    return use_get_template_by_id(id=template_id,token=credentials.credentials)


@app.get("/system-tools/{node_id}")
async def get_system_node_by_id(node_id: str,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),):
    return use_get_system_node_by_id(node_id=node_id)


# USER
@app.post("/create-user")
async def create_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        user_res = create_supabase_user(jwks, credentials.credentials)
        # print("user_res: ", user_res)
        return user_res
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}


@app.post("/check-exist")
async def check_exist(
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        user_res = check_user_exist(jwks, credentials.credentials)
        # print("user_res: ", user_res)
        return user_res
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}


# Flow
@app.post("/create-flow")
async def create_app(
    project: Project,
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return create_supabase_project(jwks, credentials.credentials, project)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}


@app.post("/edit-flow")
async def edit_app(
    project: EditProject,
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return edit_supabase_project(jwks, credentials.credentials, project)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}


@app.post("/delete-flow")
async def delete_flow(
    flow_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return delete_supabase_project(jwks, credentials.credentials, flow_id)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}


@app.get("/flow")
async def get_app_by_id(
    flow_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return get_supabase_project(jwks, credentials.credentials, flow_id)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}


@app.get("/flows")
async def get_flows(
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return get_supabase_projects(jwks, credentials.credentials)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}


@app.post("/update-flow-graph")
async def update_nodes(
    flow_graph: UpdateFlowGraph,
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    return await update_nodes_controller(flow_graph, credentials)


@app.post("/update-flow-keys")
async def update_flow_keys(
    flow_keys: UpdateFlowKeys,
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    return await update_flow_keys_controller(flow_keys, credentials)

@app.get("/get-flow-docs")
async def get_flow_docs(
    flow_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    return await get_flow_docs_controller(flow_id, credentials)

@app.get("/open-doc")
async def get_flow_docs(
    flow_id: str,
    name:str,
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    return await open_flow_docs_controller(flow_id,name, credentials)


@app.get("/load-nodes")
async def load_nodes(
    flow_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    return await load_nodes_controller(flow_id, credentials)



@app.post("/run-flow")
async def run_flow(
    data: GraphData,
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return await use_run_flow(jwks=jwks, token=credentials.credentials, data=data)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}

@app.post("/transcribe")
async def transcribe_audio(flow_id:str= Form(...),audio: UploadFile = File(...),credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),):
    return await transcribe_audio_controller(flow_id=flow_id,audio=audio,token=credentials.credentials)

@app.get("/try-template")
async def try_template(
    template_id: str,
    credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard),
):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return use_try_template(jwks=jwks, token=credentials.credentials, template_id=template_id)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}
    
# user
@app.post("/update-user")
async def update_user(user:ClerkUser,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    return await update_user_controller(user,credentials.credentials)

@app.post("/create-order")
async def create_order(data: TemplateOrderRequest,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    return await create_order_controller(data,credentials.credentials)

@app.post("/verify-payment")
async def verify_payment(data: PaymentVerificationRequest,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    return await verify_payment_controller(data,credentials.credentials)