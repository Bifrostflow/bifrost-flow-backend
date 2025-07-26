from pydantic import BaseModel, Field


class Meta(BaseModel):
    node_id: str
    type: str


class EvaluateCodeModel(Meta):
    rating: int=Field(description="give rating to provided code out of 10 where 10 is best and 1 is worst.")
    is_code: bool=Field(description="select where provided content is code or not")
    remark: str=Field(description="add a remark for betterment appreciation of provided code.(30 words limit.)",)
    code: str=Field(description="leave it blank",)


class CodeDocumentation(Meta):
    content: str=Field(description="Add main HTML content of code documentation.")
    file_name_without_extension: str=Field(description="Name for documentation file without any extension.")
    response_message: str=Field(description="Simple a human readable response message.")


class SearchableMeta(Meta):
    searchable_query: str


class TweetData(Meta):
    tweet: str
    image: str | None
    news_source: str | None

class DocToPDF(Meta):
    url:str|None

class ScriptWriterMeta(Meta):
    content:str=Field(description="Field to add Script content")
    response_message:str=Field(description="Field to add Human readable response message")
    slug_name:str=Field(description="Field to add slug name for script based on story title.")


class TrendData(SearchableMeta):
    title: str
    hashtag: str
    image: str
    image_source: str
    news_source: str
    news_source_name: str
    description: str
