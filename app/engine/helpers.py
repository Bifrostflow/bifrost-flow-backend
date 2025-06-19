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