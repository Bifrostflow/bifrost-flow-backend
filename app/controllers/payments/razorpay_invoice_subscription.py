import os
from app.controllers.payments.razorpay_client import razorpay_client
from clerk_backend_api import Clerk




async def subscription_invoice(user_id,plan_id):
    try:
        # user=super_supabase.table("users").select("email","name")
        clerk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))
        user = clerk.users.get(user_id=user_id)
        razor_pay=razorpay_client()
        plan=razor_pay.plan.fetch(plan_id)
        invoice_data = {
        "type": "invoice",
        "description": f"Invoice for {plan["item"]["name"]} Plan",
        "customer": {
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email_addresses[0],
            "contact": user.primary_phone_number_id or None
        },
        "line_items": [ 
            {
                "name": f"{plan["item"]["name"]} Plan - Monthly",
                "amount": plan["item"]["amount"]/100,
                "currency": "INR"
            }
        ],
        "sms_notify": 1,
        "email_notify": 1,
        }
        print(invoice_data)
        invoice = razor_pay.invoice.create(invoice_data)
        print(invoice)
    except Exception as e:
        print(e)
