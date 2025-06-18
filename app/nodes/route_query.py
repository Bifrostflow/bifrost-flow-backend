from app.models.models import State
from langgraph.constants import END

def route_query(state:State)->str:
    print("🤖 --- doing routing", state.get("node_data"))
    response=state.get("response")
    if response:
        node_type=response.get("type")
        return node_type
    return END

