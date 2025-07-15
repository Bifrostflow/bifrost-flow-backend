import json
from openai import OpenAI
from app.models.models import State, Response
from app.utils.constants import OPEN_AI_KEY
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
)

SPEECH_TO_TEXT = "speech_to_text"

def speech_to_text(state: State):
    print("🎙️ --- running speech_to_text tool", state.get("node_data"))

    user_openai_key = state.get("api_keys").get(OPEN_AI_KEY)
    client = OpenAI(api_key=user_openai_key)

    # Audio data should come from frontend (base64 string, blob, or file URL)
    audio_data = state.get("node_data", {}).get("audio_data")
    if not audio_data:
        raise ValueError("No audio data found in node_data")

    # Assumption: audio is being sent as a file path or bytes stored temporarily
    # You may need to update this section based on your frontend setup
    with open(audio_data, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            response_format="text",
            language="en"
        )

    print("📝 Transcription:", transcript)

    # Create a message simulating user message from transcript
    user_chat_message = ChatCompletionUserMessageParam(
        role="user",
        content=transcript
    )

    messages = state.get("response").get("messages")
    messages.append(user_chat_message)

    # Add dummy assistant message to maintain flow if needed
    assistant_msg = ChatCompletionAssistantMessageParam(
        role="assistant",
        content="Speech converted to text and added to chat flow."
    )
    messages.append(assistant_msg)

    response: Response = {
        "messages": messages,
        "type": state.get("response").get("type"),
        "meta": state.get("response").get("meta"),
        "links_to_open": state.get("response").get("links_to_open"),
    }

    state["response"] = response
    return state
