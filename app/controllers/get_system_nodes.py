from pydantic import BaseModel
from app.db.jsonDB import tools_db

class SystemToolsResponse(BaseModel):
    id: str
    name: str
    type: str
    gpt_model: str
    llm: str
    description: str
    category: str
    state: str
    require_key: bool
    key_name: str | None
    input_type: str
    object_schema: str | None

def use_get_system_nodes():
    nodes_cursor = tools_db.get_by_state("active")
    nodes = []
    for node in nodes_cursor:
        modified_nodes=SystemToolsResponse(
        id=node.id,
        name=node.name,
        type=node.type,
        gpt_model=node.gpt_model,
        llm=node.llm,
        description=node.description,
        category=node.category,
        state=node.state,
        require_key=node.require_key,
        key_name=node.key_name,
        input_type=node.input_type,
        object_schema=node.object_schema,
        )
        nodes.append(modified_nodes)
    return nodes
