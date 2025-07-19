from pydantic import BaseModel


class PaymentVerificationRequest(BaseModel):
    order_id: str
    payment_id: str
    signature: str
    receipt_id:str

class TemplateOrderRequest(BaseModel):
    currency: str 
    receipt: str 