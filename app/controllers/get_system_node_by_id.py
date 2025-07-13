from fastapi import HTTPException
from app.db.jsonDB import tools_db


def use_get_system_node_by_id(node_id: str):
    node = tools_db.get_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


def get_node_ui_loading_message(id:str):
    node_id=id.split("-")[1]
    return use_get_system_node_by_id(node_id).ui_loading_message

def get_node_ui_loading_failed_message(id:str):
    node_id=id.split("-")[1]
    return use_get_system_node_by_id(node_id).ui_loaded_message_error

def get_node_ui_loading_finished_message(id:str):
    node_id=id.split("-")[1]
    return use_get_system_node_by_id(node_id).ui_loaded_message
