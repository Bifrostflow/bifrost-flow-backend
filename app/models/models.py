from typing import List, Literal, Optional


from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage,AIMessage

class CreateFlow(BaseModel):
    name: str = Field(..., min_length=2, max_length=20)
    description: str = Field(..., min_length=2, max_length=100)
    data: str  # JSON stringify

class MessageResponse(TypedDict):
    role:Literal["assistant","system",'human', 'user', 'ai',  'function', 'tool', 'system', 'developer']
    content:str

class CreateNode(BaseModel):
    name: str = Field(..., min_length=2, max_length=20)
    type: str = Field(..., min_length=2, max_length=20)
    gpt_model: str = Field(..., min_length=2, max_length=20)
    llm: str = Field(..., min_length=2, max_length=20)
    description: str = Field(..., min_length=2, max_length=100)
    what_i_do: str  # only use if conditional, using this in prompt will return that the prompt satisfy what i do or not if yes return "type" else None


class UserEdge(TypedDict):
    id: str
    source: str
    target: str
    tool_input: Optional[str] | None
    # input_type: Literal["none", "string", "url", "pdf", "image"] | None


class GraphData(BaseModel):
    data: List[UserEdge]
    input: str
    flow_id: str


class Node(TypedDict):
    id: str
    node_id: str
    node_type: str
    prompt: str
    flow_type: str
    next_node_id: List[str]
    node_input: str | None

class LinkToOpen(TypedDict):
    label:str
    url:str
    node_id:str
    type:str

class Response(TypedDict):
    messages: List[MessageResponse]
    type: str | None
    meta: List[str]
    links_to_open:List[LinkToOpen]


class ClassifyRouteMessageClassification(BaseModel):
    type: str=Field(description="`type` of next tool based on provided `prefixed_type` value.")
    prefix: int=Field(description="`prefix` number based on provided `node_id_prefix` value.")
    message:str=Field(description="Generate a human readable message without any detail about tool or prefix just a generate message like ")


class NodeData(TypedDict):
    node_graph_id: str
    node_input: str | None
    next_nodes: None | List[str]


class State(TypedDict):
    response: Response
    ui_response: str
    flow_id: str
    user_id: str
    api_keys: dict[str, str]
    error: str
    node_data: None | NodeData  # node info only

class UserMessage(TypedDict):
    message:any  # node info only


class ChatHistory(TypedDict):
    state: State
    tool_prompt: None | HumanMessage
    user_prompt: None | HumanMessage


class TrendNews(TypedDict):
    title: str
    hashtag: str
    image: str
    image_source: str
    news_source: str
    news_source_name: str
    description: str


class TweetGenerationData(BaseModel):
    tweet: str=Field(description="generated tweet based on provided values.")

class ClerkUser(BaseModel):
    first_name:str
    last_name:str
    username:str

# title-> title
# hashtag-> title with _
# image-> ht_news_item_picture
# image_source-> ht_news_item_source
# news_source-> ht_news_item_url
# news_source_name -> ht_news_item_source
