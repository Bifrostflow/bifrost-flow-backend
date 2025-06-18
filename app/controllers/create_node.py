from app.db.mongo import node_collection
from app.models.models import CreateNode

async def use_create_node(node_data:CreateNode):
    node_dict = node_data.model_dump()
    result = await node_collection.insert_one(node_dict)
    return {"msg": "Node added", "id": str(result.inserted_id)}