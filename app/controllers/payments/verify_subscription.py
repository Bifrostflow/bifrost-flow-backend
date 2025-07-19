from jose import jwt
from openai import APIResponse
import requests
from app.controllers.payments.razorpay_invoice_subscription import subscription_invoice
from app.controllers.user.update_user import update_user_role_controller
from  app.db.supa_base import super_supabase
import hashlib
import hmac
import os
from fastapi import HTTPException
from pydantic import BaseModel

from app.controllers.payments.razorpay_client import razorpay_client
from app.models.response import APIResponse


class VerifySub(BaseModel):
    razorpay_payment_id: str
    razorpay_subscription_id: str
    razorpay_signature: str


TEST_PLAN_NAME_MAP = {
    os.getenv("DEMIGOD_PLAN_ID"):"demigod",
   os.getenv("DEITY_PLAN_ID"):"deity"
}

async def verify_subscription_controller(data:VerifySub,token:str):
    print(data)
    try:
        jwks_url = os.getenv("JWKS")
        jwks = requests.get(jwks_url).json()
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        
        msg = f"{data.razorpay_payment_id}|{data.razorpay_subscription_id}"
        print(msg)
        print("RAZORPAY_API_SECRET_KEY: ",os.getenv("RAZORPAY_API_SECRET_KEY"))
        print("RAZORPAY_API_SECRET_KEY encode: ",os.getenv("RAZORPAY_API_SECRET_KEY").encode())
        print("msg.encode(): ",msg.encode())
        sig = hmac.new(os.getenv("RAZORPAY_API_SECRET_KEY").encode(), msg.encode(), hashlib.sha256).hexdigest()
        if sig != data.razorpay_signature:
            raise HTTPException(400, "Invalid signature")
        razor_pay = razorpay_client()

        sub = razor_pay.subscription.fetch(data.razorpay_subscription_id)
        print(sub)
        old_sub=super_supabase.table("subscriptions").select("sub_id").eq("user_id",user_id).eq("is_current",True).execute().data
        print("old_sub: ",old_sub)
        if len(old_sub)>0:
            try:
                razor_pay.subscription.cancel(old_sub[0]["sub_id"], {"cancel_at_cycle_end": False})
            except Exception as e:
                return APIResponse(data=None,error="",isSuccess=False,message=f"Failed to cancel Razorpay sub: {e}")
            super_supabase.table("subscriptions").update({
            "status": "cancelled",
            "is_current": False
        }).eq("sub_id", old_sub[0]["sub_id"]).execute()
        # Store in Supabase
        super_supabase.table("subscriptions").insert({
        "sub_id": sub["id"],
        "user_id": user_id,
        "start_at": None,
        "end_at": None,
        "status": sub["status"],
        "plan_id": sub["plan_id"],
        "is_current":True
        }).execute()
        
        update_user_role_controller(role=TEST_PLAN_NAME_MAP[sub["plan_id"]],user_id=user_id)
        
        super_supabase.table("users").update({
        "user_plan": TEST_PLAN_NAME_MAP[sub["plan_id"]],
        }).eq("clerk_id",user_id).execute()
        await subscription_invoice(user_id=user_id,plan_id=sub["plan_id"])
        return APIResponse(data={"status": sub["status"]},error=None,isSuccess=True,message=f"Subscription successful, you are an {TEST_PLAN_NAME_MAP[sub["plan_id"]].capitalize()} now.")
    except Exception as e:
        print(e)
        return APIResponse(data=None,error="",isSuccess=False,message=f"Verification failed, contact admin in case of payment deduction and no subscription created.")