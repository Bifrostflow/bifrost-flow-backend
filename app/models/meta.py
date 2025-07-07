from pydantic import BaseModel


class Meta(BaseModel):
    node_id: str
    type: str


class EvaluateCodeModel(Meta):
    rating: int
    is_code: bool
    remark: str
    code: str


class CodeDocumentation(Meta):
    content: str
    file_name_without_extension: str
    response_message: str


class SearchableMeta(Meta):
    searchable_query: str


class TweetData(Meta):
    tweet: str
    image: str | None
    news_source: str | None


class TrendData(SearchableMeta):
    title: str
    hashtag: str
    image: str
    image_source: str
    news_source: str
    news_source_name: str
    description: str
