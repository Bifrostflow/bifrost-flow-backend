import datetime
import os

from clerk_backend_api import Clerk
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi_clerk_auth import (
    ClerkHTTPBearer,
    ClerkConfig,
    HTTPAuthorizationCredentials,
)
from pydantic import BaseModel
import razorpay
import requests
from supabase import SupabaseException
from jose import jwt
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
from app.controllers.run_flow import use_run_flow
from app.controllers.supabase_auth.create_payment import Payment, SupabasePayment, create_supabase_payment, update_supabase_payment
from app.controllers.supabase_auth.create_project import (
    create_supabase_project,
    get_supabase_projects,
    delete_supabase_project,
    get_supabase_project,
    edit_supabase_project,
)
from app.controllers.supabase_auth.try_template import use_try_template
from app.models.models import ClerkUser, GraphData
from app.controllers.supabase_auth.create_user import (
    create_supabase_user,
    check_user_exist,
)
from app.models.projects import Project, EditProject, UpdateFlowGraph, UpdateFlowKeys
from app.models.response import APIResponse
import hmac
import hashlib

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
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    token_data = jwt.decode(credentials.credentials, jwks, algorithms=["RS256"])
    user_id = token_data["sub"]
    if not user_id:
        res = APIResponse(
                isSuccess=False, message="Authorization failed.", data=None, error=None
            )
        return res
    clerk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

    update_kwargs = {k: v for k, v in user.model_dump(exclude_none=True).items()}
    user = clerk.users.update(user_id=user_id, **update_kwargs)
    return APIResponse(
                isSuccess=True, message="User details updated.", data=user,error=None
            )

# payments

# @app.get("/test-payments")
# async def test_payment():

class OrderRequest(BaseModel):
    amount: int 
    currency: str 
    receipt: str 

@app.post("/create-order")
async def create_order(data: OrderRequest,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    try:
        jwks_url = os.getenv("JWKS")
        jwks = requests.get(jwks_url).json()
        token_data = jwt.decode(credentials.credentials, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        exist = check_user_exist(jwks, credentials.credentials)
        if not exist.isExist:
            res = APIResponse(
                isSuccess=False, message="User not exist", data=None, error=None
            )
            return res
        # check if same user is creating payment
        if user_id != f"user_{data.receipt.split("_")[1]}":
            # print(user_id,f"user_{data.receipt.split("_")[1]}")
            res = APIResponse(
                    isSuccess=False,
                    message="Access denied.",
                    data=None,
                    error=None,
                )
            return res
        payment=SupabasePayment(receipt_id=data.receipt)
        # print("cndition pass 308",payment)
        order_response=create_supabase_payment(jwks, credentials.credentials,payment )
        # print("order_response: ",order_response)
        if not order_response.isSuccess:

            res = APIResponse(
                    isSuccess=False,
                    message=order_response.message or "Failed to create order.",
                    data=None,
                    error=None,
                )
            return res
        razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_API_KEY"), os.getenv("RAZORPAY_API_SECRET_KEY")))
        razorpay_client.set_app_details({"title" : "bifrost flow", "version" : "0.1.0"})
        order = razorpay_client.order.create({
            "amount": data.amount,
            "currency": data.currency,
            "receipt": data.receipt,
            "payment_capture": 1
        })
        return APIResponse(data={
            "order_id": order["id"],
            "key_id": os.getenv("RAZORPAY_API_KEY"),
            "receipt_id":data.receipt
        },error=None,isSuccess=True,message="Order Created.")
    except Exception as e:
        # print(str(e))
        return APIResponse(data=None,error=None,isSuccess=False,message=str(e))
class PaymentVerificationRequest(BaseModel):
    order_id: str
    payment_id: str
    signature: str
    receipt_id:str

@app.post("/verify-payment")
async def verify_payment(data: PaymentVerificationRequest,credentials: HTTPAuthorizationCredentials | None = Depends(clerk_auth_guard)):
    generated_signature = hmac.new(
        os.getenv("RAZORPAY_API_SECRET_KEY").encode(),
        f"{data.order_id}|{data.payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()

    if generated_signature == data.signature:
        jwks_url = os.getenv("JWKS")
        jwks = requests.get(jwks_url).json()
        token_data = jwt.decode(credentials.credentials, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if user_id != f"user_{data.receipt_id.split("_")[1]}":
            # print(user_id,f"user_{data.receipt_id.split("_")[1]}")
            res = APIResponse(
                    isSuccess=False,
                    message="Access denied.",
                    data=None,
                    error=None,
                )
            return res
        exist = check_user_exist(jwks, credentials.credentials)
        if not exist:
            res = APIResponse(
                isSuccess=False, message="User not exist", data=None, error=None
            )
            return res
        razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_API_KEY"), os.getenv("RAZORPAY_API_SECRET_KEY")))
        razorpay_client.set_app_details({"title" : "bifrost flow", "version" : "0.1.0"})
        payment = razorpay_client.payment.fetch(data.payment_id)
        # print("payment:: ",payment)
        supabase_payment=Payment(receipt=data.receipt_id,
                                 amount=float(payment["amount"]),
                                 order_id=payment["order_id"],
                                 order_type="product",
                                 payment_id=data.payment_id,
                                status=payment["status"],
                                timestamp=payment["created_at"]
                                 )
        supabase_order_update_res=update_supabase_payment(jwks=jwks,token=credentials.credentials,payment=supabase_payment)
        if supabase_order_update_res.isSuccess:
            return APIResponse(data={"status":payment["status"]},error=None,isSuccess=True,message="Order created successfully, thanks for using our marketplace.")
        return APIResponse(data=None,error=None,isSuccess=True,message=supabase_order_update_res.message)
    else:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
