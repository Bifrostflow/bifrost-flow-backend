from bson import ObjectId
from fastapi import HTTPException

from app.utils.utils import serialize_doc
from app.db.jsonDB import tools_db


async def use_get_system_node_by_id(node_id: str):
    try:
        obj_id = ObjectId(node_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId")

    node = await tools_db.get_by_id(obj_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return serialize_doc(node)
