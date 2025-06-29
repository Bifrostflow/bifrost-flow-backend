from typing import Optional, Literal

from pydantic import BaseModel

class Project(BaseModel):
    name: str
    description: Optional[str] = None
    user_id: Optional[str] = None

class EditProject(BaseModel):
    name: str
    description: Optional[str] = None
    id: str

class EdgeDB(BaseModel):
    data: Optional[str] = None
    api_keys: Optional[str] = None
    flow_id: str

class NodeDB(BaseModel):
    data: Optional[str] = None
    flow_id: str

class CollaboratorDB(BaseModel):
    users: Optional[str] = None
    flow_id: str
class CollaboratorInfo(BaseModel):
    uid:str
    role:Literal["owner","viewer","editor","tester"]

class CollaboratorUsersInfo(BaseModel):
    data:list[CollaboratorInfo]