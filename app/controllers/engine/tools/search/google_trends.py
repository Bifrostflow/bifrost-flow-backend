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
        "https://trends.google.com/trending/rss?geo=IN-RJ&sort=recency&category=3"
    )
    print("------------RSS", trend_items[0])

    most_traffic=0
    most_traffic_index=0

    for i,t_item in enumerate(trend_items):
        traffic=int(str(t_item.get("ht_approx_traffic")).replace("+",""))
        print(traffic)
        if traffic>most_traffic:
            most_traffic=traffic
            most_traffic_index=i
    top_news_item = trend_items[most_traffic_index].get

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
        # print(source_html)
        description_body = source_html.find("body")
        description_list = description_body.find_all(["p", "div"])

        description = ""
        possible_length=0
        for desc in description_list:
            desc_text=desc.get_text()
            possible_length+=len(description)
            if len(desc_text)>80:
                if any(word in desc_text for word in  top_news.get("title").split(" ")):
                    description += f"\n\n{ desc.get_text()}"
        
        if len(description)>5000:
            mid = len(description) // 2
            start = max(mid - 5000 // 2, 0)
            end = start + 5000
            description = description[start:end]

        print("possible_length: ",possible_length)
        print("final_length: ",len(description))
            
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
        "links_to_open":state.get("response").get("links_to_open"),
    }
    state["response"] = response

    return state
