import os
from clerk_backend_api import Clerk, ClerkErrors
import requests
from jose import jwt
from app.models.models import ClerkUser
from app.models.response import APIResponse




async def update_user_controller(user:ClerkUser,token:str):
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    token_data = jwt.decode(token, jwks, algorithms=["RS256"])
    user_id = token_data["sub"]
    if not user_id:
        res = APIResponse(
                isSuccess=False, message="Authorization failed.", data=None, error=None
            )
        return res
    clerk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

    update_kwargs = {k: v for k, v in user.model_dump(exclude_none=True).items()}
    try:
        user = clerk.users.update(user_id=user_id, **update_kwargs)
        return APIResponse(
                    isSuccess=True, message="User details updated.", data=user,error=None
                )
    except ClerkErrors as e:
        return APIResponse(
                    isSuccess=False, message=e.data.errors[0].long_message, data=user,error=None
                )

def update_user_role_controller(user_id:str,role:str="mortal"):
    clerk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

    try:
        
        user = clerk.users.update(user_id=user_id,public_metadata={
  "plan": role
})
        return APIResponse(
                    isSuccess=True, message="User details updated.", data=user,error=None
                )
    except ClerkErrors as e:
        return APIResponse(
                    isSuccess=False, message=e.data.errors[0].long_message, data=user,error=None
                )
        