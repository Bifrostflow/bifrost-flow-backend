# def create_classify_id():
#     # manage classification id
#     classification_id = ""
#     for key, value in classification_id_tracker.items():
#         if not value:
#             classification_id = key
#             classification_id_tracker[classification_id] = True
#     if classification_id == "":
#         classify_count_edge = classify_count_edge + 1
#         classification_id = f"{classify_count_edge}-{CLASSIFY_MESSAGE}"
#         classification_id_tracker[classification_id] = False
#     # manage classification id


import os

from langchain_core.language_models.chat_models import BaseChatModel

def load_model_with_key(api_key: str, model: str) -> BaseChatModel:
    import os
    os.environ["OPENAI_API_KEY"] = api_key

    from langchain.chat_models import init_chat_model
    return init_chat_model(model, model_provider="openai")

