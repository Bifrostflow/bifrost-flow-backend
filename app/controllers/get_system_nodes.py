from app.db.mongo import node_collection
from app.utils.utils import serialize_doc


async def use_get_system_nodes():
    nodes_cursor = node_collection.find({})
    nodes = []
    async for node in nodes_cursor:
        nodes.append(serialize_doc(node))
    return nodes