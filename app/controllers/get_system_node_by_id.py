from fastapi import HTTPException
from app.db.jsonDB import tools_db


def use_get_system_node_by_id(node_id: str):
    node = tools_db.get_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node
