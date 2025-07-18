import hmac
import hashlib
import os
from fastapi import  HTTPException
import requests
from jose import jwt
from app.controllers.supabase_auth.create_payment import Payment, update_supabase_payment
from app.controllers.supabase_auth.create_user import (
    check_user_exist,
)

from app.models.payment_models import PaymentVerificationRequest
from app.models.response import APIResponse
from app.controllers.payments.razorpay_client import razorpay_client

NO_ACCESS="Access denied."
NO_USER="User not exist"
ORDER_SUCCESS="Order created successfully, thanks for using our marketplace."
INVALID_PAYMENT="Invalid payment signature"

async def verify_payment_controller(data: PaymentVerificationRequest,token:str):
    generated_signature = hmac.new(
        os.getenv("RAZORPAY_API_SECRET_KEY").encode(),
        f"{data.order_id}|{data.payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()

    if generated_signature == data.signature:
        jwks_url = os.getenv("JWKS")
        jwks = requests.get(jwks_url).json()
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if user_id != f"user_{data.receipt_id.split("_")[1]}":
            # print(user_id,f"user_{data.receipt_id.split("_")[1]}")
            res = APIResponse(
                    isSuccess=False,
                    message=NO_ACCESS,
                    data=None,
                    error=None,
                )
            return res
        exist = check_user_exist(jwks, token)
        if not exist:
            res = APIResponse(
                isSuccess=False, message=NO_USER, data=None, error=None
            )
            return res
        razor_pay = razorpay_client()
        
        payment = razor_pay.payment.fetch(data.payment_id)
        # print("payment:: ",payment)
        supabase_payment=Payment(receipt=data.receipt_id,
                                 amount=float(payment["amount"]),
                                 order_id=payment["order_id"],
                                 order_type="product",
                                 payment_id=data.payment_id,
                                status=payment["status"],
                                timestamp=payment["created_at"]
                                 )
        supabase_order_update_res=update_supabase_payment(jwks=jwks,token=token,payment=supabase_payment)
        if supabase_order_update_res.isSuccess:
            return APIResponse(data={"status":payment["status"]},error=None,isSuccess=True,message=ORDER_SUCCESS)
        
        return APIResponse(data=None,error=None,isSuccess=True,message=supabase_order_update_res.message)
    else:
        raise HTTPException(status_code=400, detail=INVALID_PAYMENT)