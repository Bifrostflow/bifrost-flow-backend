from jose import jwt
from pydantic import BaseModel
from supabase import SupabaseException

from app.controllers.user.update_user import update_user_role_controller
from app.db.supa_base import super_supabase
from app.models.response import APIResponse


def create_supabase_user(jwks:any,token:str)->APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        email = token_data["email"]
        if not user_id:
            res = APIResponse(isSuccess=False, message="Authorization failed.", data=None, error=None)
            return res
        exist = check_user_exist(jwks,token)
        if exist.isExist:
            res=APIResponse(isSuccess=True,message="User created Successfully.",data=None,error=None)
            return res
    except Exception as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res
    try:
        super_supabase.table("users").insert(({"clerk_id":user_id,"email":email})).execute()
        update_user_role_controller(user_id=user_id)
        res = APIResponse(isSuccess=True, message="User created Successfully.", data=None, error=None)
        return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message=f"{e}", data=None, error=None)
        return res

def get_supabase_user(jwks:any,token:str)->APIResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res = APIResponse(isSuccess=False, message="Authorization failed.", data=None, error=None)
            return res
    except Exception as e:
        res = APIResponse(isSuccess=False, message="failed", data=None, error=f"{e}")
        return res
    try:
        response = super_supabase.table("users").select("*").eq("clerk_id",user_id).execute()
        # print("RES44 ",response.data[0])
        res = APIResponse(isSuccess=True, message="fetched", data=response.data[0], error=None)
        return res
    except SupabaseException as e:
        res = APIResponse(isSuccess=False, message="failed", data=None, error=f"{e.message}")
        return res


class UserExistResponse(BaseModel):
    isExist:bool
def check_user_exist(jwks:any,token:str)->UserExistResponse:
    try:
        token_data = jwt.decode(token, jwks, algorithms=["RS256"])
        user_id = token_data["sub"]
        if not user_id:
            res=UserExistResponse(isExist=False)
            return res
    except SupabaseException as e:
        # print(e)
        res = UserExistResponse(isExist=False)
        return res
    try:
        response = super_supabase.table("users").select("clerk_id").eq("clerk_id",user_id).execute()
        # print("RES ",response.data)
        res = UserExistResponse(isExist=len(response.data)==1)
        # print("",res)
        return res
    except SupabaseException as e:
        # print(e)
        res = UserExistResponse(isExist=False)
        return res
