from typing import List, Literal, Optional

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionUserMessageParam,
)
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class CreateFlow(BaseModel):
    name: str = Field(..., min_length=2, max_length=20)
    description: str = Field(..., min_length=2, max_length=100)
    data: str  # JSON stringify


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


class Response(TypedDict):
    messages: List[ChatCompletionUserMessageParam | ChatCompletionAssistantMessageParam]
    type: str | None
    meta: List[str]


class ResponseModel(BaseModel):
    type: str
    prefix: int


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
    tool_prompt: None | ChatCompletionUserMessageParam
    user_prompt: None | ChatCompletionUserMessageParam


class TrendNews(TypedDict):
    title: str
    hashtag: str
    image: str
    image_source: str
    news_source: str
    news_source_name: str
    description: str


class TweetGenerationData(BaseModel):
    tweet: str

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
