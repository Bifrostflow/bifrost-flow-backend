import datetime
import time
from typing import Literal
from pydantic import BaseModel
from supabase import SupabaseException
from app.models.response import APIResponse
from jose import jwt
from app.controllers.supabase_auth.create_user import check_user_exist
from app.db.supa_base import super_supabase

class SupabasePayment(BaseModel):
    receipt_id:str

class Payment(BaseModel):
    receipt:str
    payment_id:str
    order_id:str
    amount:float
    status:str
    timestamp:int
    order_type:Literal["product","subscription"]

def create_supabase_payment(jwks: any, token: str, payment: SupabasePayment) -> APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        # check if same user is creating payment
        # print("PAYMENT: ",payment)
        if user_id != f"user_{payment.receipt_id.split("_")[1]}":
            # print(user_id,f"user_{payment.receipt_id.split("_")[1]}")
            res = APIResponse(
                    isSuccess=False,
                    message="Access denied.",
                    data=None,
                    error=None,
                )
            return res
        
        retries = 2
        is_success = False
        res = None  # 👈 define before
        exist_order_data= super_supabase.table("payments").select("payment_id","order_id","status").eq("receipt",payment.receipt_id).execute()
        # print("exist_order_data: ",exist_order_data)
        # # print("exist_order_data: 1 ",exist_order_data.data[0])
        # # print("exist_order_data: payment_id: ",exist_order_data.data[0].get("payment_id"))
        if len(exist_order_data.data)>0:
            p_id=exist_order_data.data[0].get("payment_id")
            o_status=exist_order_data.data[0].get("status")
            if p_id!="" or o_status!="":
                return APIResponse(isSuccess=False, message="Order already exist!", data=None, error=None)
            else:
                return  APIResponse(
                    isSuccess=True,
                    message="Project created Successfully.",
                    data=None,
                    error=None,
                )
                #  and o_id=="":
        while retries > 0 and not is_success:
            try:
                payment_order = Payment(
                    receipt=payment.receipt_id,
                    amount=0,            # ✅ actual amount
                    order_id='',        # ✅ actual order_id
                    order_type='product',
                    payment_id='',
                    status='',
                    timestamp=int(time.time() * 1000), 
                )
                # print(payment_order)
                response_order = super_supabase.table("payments").insert(
                    payment_order.model_dump()
                ).execute()
                # print("response_order: ",response_order)

                is_success = True
                res = APIResponse(
                    isSuccess=True,
                    message="Project created Successfully.",
                    data=None,
                    error=None,
                )
                break  # 👈 break after success

            except Exception as e:  # broader catch
                retries -= 1
                if retries == 0:
                    res = APIResponse(
                        isSuccess=False,
                        message=e.message or "Project creation failed after retries.",
                        data=None,
                        error=str(e),
                    )
        return res
    except SupabaseException as e:
        # print("EXP: ",f"{e}")
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res

def update_supabase_payment(jwks: any, token: str, payment: Payment) -> APIResponse:
    token_data = jwt.decode(token, jwks, algorithms=["RS256"])
    user_id = token_data["sub"]
        # check if same user is creating payment
    if user_id != f"user_{payment.receipt.split("_")[1]}":
        # print(user_id,f"user_{payment.receipt.split("_")[1]}")
        res = APIResponse(
                    isSuccess=False,
                    message="Access denied.",
                    data=None,
                    error=None,
                )
        return res

    try:
        response_order = super_supabase.table("payments").update(
                    payment.model_dump()
        ).eq("receipt",payment.receipt).execute()
        # print("response_order:: ",response_order)
        res = APIResponse(
                    isSuccess=True,
                    message="Order updated successfully.",
                    data=None,
                    error=None,
                )
        return res

    except Exception as e:  # broader catch
        # print(e)
        res = APIResponse(
                        isSuccess=False,
                        message=str(e) or  "Order update failed.",
                        data=None,
                        error=str(e),
                    )
        return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e.message}", data=None, error=None)
        return res