import json
from bs4 import BeautifulSoup
import feedparser
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
)
import requests
from app.models.models import State, Response, TrendData, TrendNews


async def get_html(path: str):
    url = path

    response = requests.get(url)
    if response.status_code != 200:
        print(url)
        raise Exception("Network response was not ok")

    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    return soup


async def get_rss(url: str):
    feed = feedparser.parse(url)
    items = feed.entries
    return items


async def google_trend(state: State):
    #
    messages = state.get("response").get("messages")

    # scrapping start
    trend_items = await get_rss(
        "https://trends.google.com/trending/rss?geo=IN&hours=24&status=active&sort=recency"
    )
    print("------------RSS", trend_items[0])
    top_news_item = trend_items[0].get

    top_news: TrendNews = {
        "image": top_news_item("ht_news_item_picture"),
        "title": top_news_item("title"),
        "image_source": top_news_item("ht_news_item_source"),
        "news_source": top_news_item("ht_news_item_url"),
        "news_source_name": top_news_item("ht_news_item_source"),
        "hashtag": f"#{"_".join(f"{top_news_item("title")}".split())}",
    }
    source_html = await get_html(top_news.get("news_source"))
    description_body = source_html.find("body")
    description_list = description_body.find_all("p")

    description = ""
    for desc in description_list:
        description += f"\n\n{ desc.get_text()}"
    print(description)
    top_news["description"] = description

    searchable_query = f"i need for info on this topic {top_news.get("title")}"
    message = f"Here is top trend found `{top_news.get("title")}`"

    # scrapping end
    #
    user_request = ChatCompletionUserMessageParam(
        role="user", content="Provide me top trend topic on google trend"
    )
    messages.append(user_request)
    response_chat_data = ChatCompletionAssistantMessageParam(
        role="assistant", content=message
    )
    messages.append(response_chat_data)

    # create meta start
    meta_response = TrendData(
        searchable_query=searchable_query,
        node_id=state.get("node_data").get("node_graph_id"),
        result=top_news,
        type="google_trends",
    )
    meta = meta_response.model_dump()
    # create meta end

    response: Response = {
        "messages": messages,
        "type": state.get("response").get("type"),
        "meta": [*state.get("response").get("meta"), json.dumps(meta)],
    }
    state["response"] = response
    state["ui_response"] = "Trend Search finished."

    return state
