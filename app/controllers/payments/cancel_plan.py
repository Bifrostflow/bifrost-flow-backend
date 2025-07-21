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

async def cancel_plan(token:str):
    try:
        jwks_url = os.getenv("JWKS")
        jwks = requests.get(jwks_url).json()
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        
        razor_pay = razorpay_client()

        old_sub=super_supabase.table("subscriptions").select("sub_id").eq("user_id",user_id).eq("is_current",True).execute().data
        if len(old_sub)>0:
            try:
                razor_pay.subscription.cancel(old_sub[0]["sub_id"], {"cancel_at_cycle_end": True})
                update_user_role_controller(user_id=user_id)
            except Exception as e:
                return APIResponse(data=None,error="",isSuccess=False,message=f"Failed to cancel Razorpay sub: {e}")
            super_supabase.table("subscriptions").update({
            "status": "cancelled",
            "is_current": False
        }).eq("sub_id", old_sub[0]["sub_id"]).execute()

        # Store in Supabase
        return APIResponse(data=None,error=None,isSuccess=True,message="Plan cancelled successfully. Your current plan will remain active until the end of this billing period.")
    except Exception as e:
        print(e)
        return APIResponse(data=None,error="",isSuccess=False,message=f"Verification failed, contact admin in case of payment deduction and no subscription created.")