from app.db.mongo import flow_collection
from app.utils.utils import serialize_doc


async def use_get_flow():
    flows_cursor = flow_collection.find({})
    flows = []
    async for flow in flows_cursor:
        flows.append(serialize_doc(flow))
    return flows