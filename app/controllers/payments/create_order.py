import os
import requests
from jose import jwt
from app.controllers.payments.razorpay_client import razorpay_client
from app.controllers.supabase_auth.create_payment import  SupabasePayment, create_supabase_payment
from app.controllers.supabase_auth.create_user import (check_user_exist)
from app.models.payment_models import TemplateOrderRequest
from app.models.response import APIResponse

NO_ACCESS="Access denied."
NO_USER="User not exist"
ORDER_SUCCESS="Order created"
ORDER_FAILED="Failed to create order."

async def create_order_controller(data: TemplateOrderRequest,token:str):
    try:
        jwks_url = os.getenv("JWKS")
        jwks = requests.get(jwks_url).json()
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        exist = check_user_exist(jwks, token)
        if not exist.isExist:
            res = APIResponse(
                isSuccess=False, message=NO_USER, data=None, error=None
            )
            return res
        # check if same user is creating payment
        if user_id != f"user_{data.receipt.split("_")[1]}":
            # print(user_id,f"user_{data.receipt.split("_")[1]}")
            res = APIResponse(
                    isSuccess=False,
                    message=NO_ACCESS,
                    data=None,
                    error=None,
                )
            return res
        payment=SupabasePayment(receipt_id=data.receipt)
        # print("condition pass 308",payment)
        order_response=create_supabase_payment(jwks, token,payment )
        # print("order_response: ",order_response)
        if not order_response.isSuccess:

            res = APIResponse(
                    isSuccess=False,
                    message=order_response.message or ORDER_FAILED,
                    data=None,
                    error=None,
                )
            return res
        RAZORPAY_API_KEY=os.getenv("RAZORPAY_API_KEY")
        razor_pay = razorpay_client()
        order = razor_pay.order.create({
            "amount": data.amount,
            "currency": data.currency,
            "receipt": data.receipt,
            "payment_capture": 1
        })
        return APIResponse(data={
            "order_id": order["id"],
            "key_id": RAZORPAY_API_KEY,
            "receipt_id":data.receipt
        },error=None,isSuccess=True,message=ORDER_SUCCESS)
    except Exception as e:
        return APIResponse(data=None,error=None,isSuccess=False,message=str(e))