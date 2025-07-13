import os
import requests
from app.db.template_data import template_db
from jose import jwt
from app.controllers.supabase_auth.create_user import check_user_exist
from app.db.supa_base import super_supabase

def use_get_templates():
    nodes_cursor = template_db.get_by_state("public")
    templates = []
    for template in nodes_cursor:
        templates.append(template)
    return {
        "isSuccess": True,
        "data": templates,
        "message": "",
    }

def use_get_template_by_id(id:str, token: str,):
    template = template_db.get_by_id(id=id)
    jwks_url = os.getenv("JWKS")
    jwks = requests.get(jwks_url).json()
    token_data = jwt.decode(token, jwks, algorithms=["RS256"])
    user_id = token_data["sub"]
    possible_receipt=f"{template.product_id}_{str(user_id).split("_")[1]}"
    # print("possible_receipt: ",possible_receipt)
    order_response=super_supabase.table("payments").select("status").eq("receipt",possible_receipt).execute()
    is_purchased=False
    if len(order_response.data)>0:
        is_purchased=order_response.data[0].get("status")=="captured"

    # captured
    template.is_purchased=is_purchased
    return {
        "isSuccess": True,
        "data": template,
        "message": "",
    }
