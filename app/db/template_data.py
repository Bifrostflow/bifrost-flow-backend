from pydantic import BaseModel
from typing import List, Optional, Literal
from typing import Dict


class UserRef(BaseModel):
    id: str
    user_id: str


class ToolRef(BaseModel):
    id: str
    name: str
    description: str


class Node(BaseModel):
    id: str
    type: str
    config: Optional[dict] = None


class Edge(BaseModel):
    from_node: str
    to_node: str
    condition: Optional[str] = None


class JSONSchema(BaseModel):
    type: str
    properties: dict
    required: Optional[List[str]] = []


# class APIConfig(BaseModel):
#     apiKeyRequired: bool
#     keysRequired: List[str]
#     endpoint: str
#     rateLimit: Optional[str] = None


class Graph(BaseModel):
    nodes: str
    edges: str


class FlowTemplate(BaseModel):
    id: str
    name: str
    description: str
    category: Literal[
        "social-media",
        "office",
        "software-development",
        "writing",
        "communication",
        "blogging",
    ]
    icon: Optional[str] = None
    visibility: Literal["public", "private", "draft"]

    createdBy: str
    createdAt: str
    updatedAt: str

    graph: Graph

    toolsUsed: List[ToolRef]
    systemToolsUsed: List[ToolRef]

    inputSchema: JSONSchema | None
    outputSchema: str | None
    isSellable: bool
    price: Optional[float] = None
    keywords: List[str]
    tags: List[str]
    version: str

    # apiConfig: Optional[APIConfig] = None


template_data: dict[str, FlowTemplate] = {
    "6909ccff-4474-4cf6-8218-b5fce2f37122": FlowTemplate(
        category="social-media",
        createdAt="2025-07-06 11:00:00.117264+00",
        createdBy="admin",
        description="""Generate Viral Tweets Instantly with Trending Tweet Generator:
Stay ahead of the curve with our Trending Tweet Generator — a smart tool that creates tweets based on the hottest topics from Google Trends. Simply plug in your OpenAI API key, and let the magic happen. In seconds, a fresh, relevant tweet will be auto-filled right into your browser — ready to copy, share, or post.
Perfect for content creators, marketers, and anyone looking to ride the wave of trending conversations on X (Twitter). Stay tuned for more updates...""",
        graph=Graph(
            edges="""{\"data\":[{\"tool_input\":\"\",\"source\":\"1-686a060b7493977b931934c3\",\"target\":\"2-686915a6acd2b4a126714ec3\",\"id\":\"xy-edge__1-686a060b7493977b931934c3-2-686915a6acd2b4a126714ec3\"},{\"tool_input\":\"\",\"source\":\"2-686915a6acd2b4a126714ec3\",\"target\":\"3-686a027e7493977b931934c2\",\"id\":\"xy-edge__2-686915a6acd2b4a126714ec3-3-686a027e7493977b931934c2\"},{\"tool_input\":\"\",\"source\":\"3-686a027e7493977b931934c2\",\"target\":\"4-684e733dc2b59ec01fb72c77\",\"id\":\"xy-edge__3-686a027e7493977b931934c2-4-684e733dc2b59ec01fb72c77\"}]}""",
            nodes="""{\"data\":[{\"id\":\"1-686a060b7493977b931934c3\",\"type\":\"initiate\",\"data\":{\"id\":\"686a060b7493977b931934c3\"},\"position\":{\"x\":244,\"y\":240.5},\"measured\":{\"width\":84,\"height\":25},\"selected\":false,\"dragging\":false},{\"id\":\"2-686915a6acd2b4a126714ec3\",\"type\":\"action\",\"data\":{\"id\":\"686915a6acd2b4a126714ec3\"},\"position\":{\"x\":106,\"y\":299.5},\"measured\":{\"width\":361,\"height\":34},\"selected\":false,\"dragging\":false},{\"id\":\"3-686a027e7493977b931934c2\",\"type\":\"generate\",\"data\":{\"id\":\"686a027e7493977b931934c2\"},\"position\":{\"x\":141,\"y\":391.5},\"measured\":{\"width\":291,\"height\":43},\"selected\":false,\"dragging\":false},{\"id\":\"4-684e733dc2b59ec01fb72c77\",\"type\":\"close\",\"data\":{\"id\":\"684e733dc2b59ec01fb72c77\"},\"position\":{\"x\":256,\"y\":473.5},\"measured\":{\"width\":62,\"height\":25},\"selected\":true,\"dragging\":false}]}""",
        ),
        icon=None,
        id="6909ccff-4474-4cf6-8218-b5fce2f37122",
        inputSchema=None,
        isSellable=False,
        keywords=["twitter", "google trend", "tweet generator"],
        name="Trending Tweet Generator",
        outputSchema="",
        price=0,
        systemToolsUsed=[
            ToolRef(
                id="686915a6acd2b4a126714ec3",
                name="Google Trends",
                description="Find top trending topic on google trend and make full use out of it. More tools coming soon in this suit family...",
            ),
            ToolRef(
                id="686a027e7493977b931934c2",
                name="Create Tweet",
                description="Write/ Generate tweet based on provided data in prompt or based on past response.",
            ),
        ],
        tags=["tweet_generator", "twitter", "google_trends"],
        toolsUsed=[],
        updatedAt="2025-07-06 11:00:00.117264+00",
        version="1.0.0",
        visibility="public",
    )
}


class TemplateDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TemplateDB, cls).__new__(cls)
        return cls._instance

    def _load_templates(self) -> Dict[str, FlowTemplate]:
        return template_data

    def get_by_id(self, id: str) -> Optional[FlowTemplate]:
        templates = self._load_templates()
        return templates.get(id)

    def get_by_state(
        self, state: Literal["public", "private", "draft"]
    ) -> List[FlowTemplate]:
        templates = self._load_templates()
        return [
            template for template in templates.values() if template.visibility == state
        ]

    def get_by_category(
        self,
        category: Literal[
            "social-media",
            "office",
            "software-development",
            "writing",
            "communication",
            "blogging",
        ],
    ) -> List[FlowTemplate]:
        templates = self._load_templates()
        return [
            template
            for template in templates.values()
            if template["category"] == category
        ]

    def get_by_key_value(self, key: str, value: str) -> List[FlowTemplate]:
        templates = self._load_templates()
        return [
            template for template in templates.values() if template.get(key) == value
        ]


# ✅ Use the singleton
template_db = TemplateDB()
