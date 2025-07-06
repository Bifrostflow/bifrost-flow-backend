from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union
from datetime import datetime


class UserRef(BaseModel):
    id: str
    name: str


class ToolRef(BaseModel):
    id: str
    name: str


class Node(BaseModel):
    id: str
    type: str
    config: dict


class Edge(BaseModel):
    from_node: str
    to_node: str
    condition: Optional[str] = None


class JSONSchema(BaseModel):
    type: str
    properties: dict
    required: Optional[List[str]] = []


class APIConfig(BaseModel):
    apiKeyRequired: bool
    endpoint: str
    rateLimit: Optional[str] = None


class FlowTemplate(BaseModel):
    id: str
    name: str
    description: str
    category: str
    icon: Optional[str] = None
    visibility: Literal["public", "private", "draft"]

    createdBy: UserRef
    createdAt: datetime
    updatedAt: datetime

    class Graph(BaseModel):
        nodes: List[Node]
        edges: List[Edge]

    graph: Graph

    toolsUsed: List[ToolRef]
    systemToolsUsed: List[ToolRef]

    inputSchema: JSONSchema
    outputSchema: JSONSchema

    isSellable: bool
    price: Optional[float] = None
    keywords: List[str]
    tags: List[str]
    version: str

    apiConfig: Optional[APIConfig] = None
