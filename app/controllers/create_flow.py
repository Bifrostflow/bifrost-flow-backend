from app.db.mongo import flow_collection
from app.models.models import CreateFlow


async def use_create_flow(flow_data:CreateFlow):
    flow_dict = flow_data.model_dump()
    result = await flow_collection.insert_one(flow_dict)
    return {"msg": "Flow added", "id": str(result.inserted_id)}