from inspect import isawaitable

from app.models.models import State, NodeData

def with_node_data(data:NodeData, tool:callable):
    print("⚙️: ",data,tool)
    async def wrapper_handler(state:State):
            state["node_data"]=data
            result=tool(state)
            if isawaitable(result):
                return await result
            return result
    return wrapper_handler