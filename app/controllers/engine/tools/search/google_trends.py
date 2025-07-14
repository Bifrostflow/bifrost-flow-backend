import json
from bs4 import BeautifulSoup
import feedparser
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
)
import requests
from app.models.meta import TrendData
from app.models.models import State, Response, TrendNews

GOOGLE_TRENDS = "google_trends"


async def get_html(path: str):
    url = path
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(url)
            raise Exception("Network response was not ok")

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        return soup
    except Exception:
        return None


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
    print("-----here")
    source_html = await get_html(top_news.get("news_source"))
    if source_html:
        print(source_html)
        description_body = source_html.find("body")
        description_list = description_body.find_all(["p", "div","article"])

        description = ""
        for desc in description_list:
            desc_text=desc.get_text()
            if len(desc_text)>80:
                description += f"\n\n{ desc.get_text()}"
        print("description: ", description)
        top_news["description"] = description
    else:
        top_news["description"] = top_news.get("title")
    searchable_query = f"i need info on this topic {top_news.get("title")}"
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
        type="google_trends",
        description=top_news.get("description"),
        hashtag=top_news.get("hashtag"),
        image=top_news.get("image"),
        image_source=top_news.get("image_source"),
        news_source=top_news.get("news_source"),
        news_source_name=top_news.get("news_source_name"),
        title=top_news.get("title"),
    )
    meta = meta_response.model_dump()
    # create meta end

    response: Response = {
        "messages": messages,
        "type": state.get("response").get("type"),
        "meta": [*state.get("response").get("meta"), json.dumps(meta)],
    }
    state["response"] = response

    return state
