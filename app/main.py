from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.controllers.create_flow import use_create_flow
from app.controllers.create_node import use_create_node
from app.controllers.get_flow import use_get_flow
from app.controllers.get_system_node_by_id import use_get_system_node_by_id
from app.controllers.get_system_nodes import use_get_system_nodes
from app.controllers.run_flow import use_run_flow

from app.models.models import CreateFlow, CreateNode, GraphData


app = FastAPI()
load_dotenv()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async  def test():
    return {"test":"test"}

@app.post("/create-flow")
async def create_flow(flow_data:CreateFlow):
    return await use_create_flow(flow_data)

@app.get("/flows")
async def get_flows():
    return await use_get_flow()

@app.post("/run-flow")
async def run_flow(data:GraphData):
    return await use_run_flow(data=data)

@app.post("/create-node")
async def create_node(node_data:CreateNode):
    return await use_create_node(node_data)

@app.get("/system-tools")
async def get_system_nodes():
    return await use_get_system_nodes()

@app.get("/system-tools/{node_id}")
async def get_system_node_by_id(node_id:str):
    return await use_get_system_node_by_id(node_id=node_id)
