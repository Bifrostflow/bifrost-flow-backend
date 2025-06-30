import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi_clerk_auth import ClerkHTTPBearer, ClerkConfig, HTTPAuthorizationCredentials
from pydantic import BaseModel
import requests
from supabase import SupabaseException
from app.controllers.create_node import use_create_node
from app.controllers.flow import load_nodes_controller, update_nodes_controller
from app.controllers.get_system_node_by_id import use_get_system_node_by_id
from app.controllers.get_system_nodes import use_get_system_nodes
from app.controllers.run_flow import use_run_flow
from app.controllers.supabase_auth.create_project import create_supabase_project, get_supabase_projects, \
    delete_supabase_project, get_supabase_project, edit_supabase_project
from app.models.models import CreateNode, GraphData
from app.controllers.supabase_auth.create_user import create_supabase_user, check_user_exist
from app.models.projects import Project, EditProject, UpdateFlowGraph

# Use your Clerk JWKS endpoint
clerk_config = ClerkConfig(jwks_url=os.getenv("JWKS"))

clerk_auth_guard = ClerkHTTPBearer(config=clerk_config)

class UserInfo(BaseModel):
    name:str

app = FastAPI(openapi_prefix="/api")
load_dotenv()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bifrostflow.com/","bifrostflow.com/","https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async  def test():
    return {"test":"test"}

@app.post("/run-flow")
async def run_flow(data:GraphData,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return await use_run_flow(jwks=jwks,token=credentials.credentials,data=data)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.","error":e}

@app.post("/create-node")
async def create_node(node_data:CreateNode):
    return await use_create_node(node_data)

@app.get("/system-tools")
async def get_system_nodes():
    return await use_get_system_nodes()

@app.get("/system-tools/{node_id}")
async def get_system_node_by_id(node_id:str):
    return await use_get_system_node_by_id(node_id=node_id)



# USER
@app.post("/verify-user")
async def verify_user(user:UserInfo,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    print(credentials.credentials,user)
    return "woho"

@app.post("/create-user")
async def create_user(credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        user_res = create_supabase_user(jwks,credentials.credentials)
        print("user_res: ",user_res)
        return user_res
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.","error":e}

@app.post("/check-exist")
async def check_exist(credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        user_res = check_user_exist(jwks,credentials.credentials)
        print("user_res: ",user_res)
        return user_res
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.","error":e}

# Flow
@app.post("/create-flow")
async def create_app(project:Project,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return create_supabase_project(jwks, credentials.credentials,project)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}

@app.post("/edit-flow")
async def edit_app(project:EditProject,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return edit_supabase_project(jwks, credentials.credentials,project)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}

@app.post("/delete-flow")
async def delete_flow(flow_id:str,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return delete_supabase_project(jwks, credentials.credentials,flow_id)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}

@app.get("/flow")
async def get_app_by_id(flow_id:str,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return get_supabase_project(jwks, credentials.credentials,flow_id)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}

@app.get("/flows")
async def get_flows(credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    try:
        return get_supabase_projects(jwks, credentials.credentials)
    except SupabaseException as e:
        return {"isSuccess": False, "message": "Something went wrong.", "error": e}

@app.post("/update-flow-graph")
async def update_nodes(flow_graph: UpdateFlowGraph,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    return await update_nodes_controller(flow_graph,credentials)

@app.get("/load-nodes")
async def load_nodes(flow_id: str,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    return await load_nodes_controller(flow_id,credentials)