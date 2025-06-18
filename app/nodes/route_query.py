from app.models.models import State
from langgraph.constants import END

ROUTE_QUERY="conditional_routing"

def route_query(state:State)->str:
    print("🤖 --- doing routing", state.get("node_data"))
    res=state.get("response")
    if res:
        q_type=res.get("type")
        return q_type
    return END

