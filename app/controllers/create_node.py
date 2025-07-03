from app.models.models import CreateNode


async def use_create_node(node_data: CreateNode):
    return {
        "msg": "Node added",
    }
