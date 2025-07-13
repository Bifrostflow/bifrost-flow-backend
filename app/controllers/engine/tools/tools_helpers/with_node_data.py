from inspect import isawaitable


from app.models.models import State, NodeData
from app.controllers.get_system_node_by_id import get_node_ui_loading_message


def with_node_data(data: NodeData, tool: callable):
    print("⚙️: ", data, tool)

    async def wrapper_handler(state: State):
        state["node_data"] = data
        next_node_loading_message=get_node_ui_loading_message(data.get("next_nodes")[0])
        state["ui_response"] = next_node_loading_message
        result = tool(state)
        if isawaitable(result):
            return await result
        return result
    return wrapper_handler
