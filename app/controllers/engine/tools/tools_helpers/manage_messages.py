from typing import List

from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
)

from app.models.models import Response, ChatHistory


# system: SYSTEM_PROMPT --- temp : TOOL
# user: USER_PROMPT (will be there from start) :STATE
# assistant: PREV_ASSISTANT_MESSAGE (LAST MESSAGE) :STATE
# user: ASSISTANT_PROMPT(TOOL_SPECIFIC) --temp :TOOL


def manage_flow_chat_history(
    data: ChatHistory,
) -> List[ChatCompletionUserMessageParam | ChatCompletionAssistantMessageParam]:
    response: Response = data.get("state").get("response")
    messages: List[
        ChatCompletionUserMessageParam | ChatCompletionAssistantMessageParam
    ] = response.get("messages")
    is_untouched_prompt = len(messages) == 1
    if data.get("tool_prompt") and not is_untouched_prompt:
        messages.append(data.get("tool_prompt"))
    if data.get("user_prompt"):
        messages.append(data.get("user_prompt"))
    return messages
