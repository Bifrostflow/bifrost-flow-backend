from pydantic import BaseModel
from typing import Any

class APIResponse(BaseModel):
    message:str
    isSuccess:bool
    error:str|None
    data:Any|None