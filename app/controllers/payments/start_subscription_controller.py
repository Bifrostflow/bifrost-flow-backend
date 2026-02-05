import os

from fastapi import HTTPException
from jose import jwt
import requests
from app.controllers.payments.razorpay_client import razorpay_client
from app.models.response import APIResponse
from  app.db.supa_base import super_supabase

TEST_PLAN_MAP = {
    "demigod": os.getenv("DEMIGOD_PLAN_ID"),
    "deity": os.getenv("DEITY_PLAN_ID")
}


async def start_subscription_controller(plan:str,token:str):
    print(plan)
    try:
        jwks_url = os.getenv("JWKS")
        print(jwks_url)
        jwks = requests.get(jwks_url).json()
        print(jwks)
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        print(token_data)
        user_id = token_data["sub"]
        print(user_id,TEST_PLAN_MAP[plan])
        if not TEST_PLAN_MAP[plan]:
            return APIResponse(data=None,error="",isSuccess=False,message="Invalid plan")
        razor_pay = razorpay_client()
        try:
            print("TEST_PLAN_MAP[plan]: ",TEST_PLAN_MAP[plan])
            rzp_sub=razor_pay.subscription.create({
                "plan_id":TEST_PLAN_MAP[plan],
                "total_count":12,
                "customer_notify":1
            })
            return APIResponse(isSuccess=True,data= {
                    "sub_id": rzp_sub["id"],
                },error="",message="",
                )
        except Exception as e:
            return APIResponse(data=None,error="",isSuccess=False,message=f"Razorpay error: {str(e)}")

    except Exception as e:
        print(e)
        return APIResponse(data=None,error="",isSuccess=False,message=f"Subscription process failed.")