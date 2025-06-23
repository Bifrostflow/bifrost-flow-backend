from typing import List

from langgraph.graph import StateGraph
from models.models import Node,State
from app.controllers.tools.distribute import distribute
from app.controllers.tools.conditional.route_query import route_query

'''
Nodes
write code
write message
write email and send
convert message to md formate

Frontend:

Response: {  // for backend, no Response on frontend
            message:string, 
            type:node_type
        } 
Node: {
    id:string, 
    node_id:string, 
    prompt:string, 
    response:Response,
    flow_type: "linear" | "conditional",
    next_edge: node_id[]
}

flow_data:Node[] 
class Node(TypedDict):
    id: str
    node_id: str
    node_type: str
    prompt:str
    flow_type: str
    next_node_id: List[str]
[
    {
        id:"1j2uigbewiu2wke"
        node_id:"START", 
        prompt:"How are you?", 
        flow_type: "linear",
        next_edge: ["classify_message"]
    },
    {
        id:"12345678", 
        node_id:"classify_message", 
        prompt:"How are you?", 
        flow_type: "conditional",
        next_edge: ["write_message","write_code"]
    },
    {
        id:"12345678", 
        node_id:"write_code", 
        prompt:"How are you?", 
        flow_type: "linear"
        next_edge: ["evaluate_code"]
    },
    {
        id:"12345678", 
        node_id:"evaluate_code", 
        prompt:"How are you?", 
        flow_type: "linear"
        next_edge: ["END"]
    },
    {
        id:"12345678", 
        node_id:"write_message", 
        prompt:"How are you?", 
        flow_type: "linear"
        next_edge: ["END"]
    },
]


"next_nodes": ["write_code_id", "write_message_id"]

for every node
i will create a prompt like this 

nextNodeStepsCheck="Check if this prompt satisfy this below checks and along with response send the output of this check as type in JSON formate"
for next_node_id in node.next_nodes
    next_node = await db.get(next_node_id)
    nextNodeStepsCheck+=f"/n {next_node.what_i_do} return type as {next_node.type} if prompt satisfy this."

f"${node.prompt}/n/n/n ${nextNodeStepsCheck}" # this will return Eg: {response:"some message", type:"write_message"}
    "name": "Write Code",
    "type": "write_code",
    "gpt_model":"gpt-4.1",
    "llm": "openai",
    "description": "To write code based on prompt provided by user.",
    "what_i_do": "Check if the provided prompt satisfies this type 'write_code' if yes return type as 'write_code' else Ignore"

 {
      "id": "xy-edge__6-684a0a2a14df3de4f4f6845d-5-end",
      "source": "6-684a0a2a14df3de4f4f6845d",
      "target": "5-end"
    },    
'''

data:List[Node]=[
    {
        "id":"1j2uigbewiu2wke",
        "node_id":"START",
        "node_type":"START",
        "prompt":"How are you?",
        "flow_type": "linear",
        "next_node_id": ["classify_message"]
    },
    {
        "id":"12345678",
        "node_id":"classify_message",
        "node_type":"classify_message",
        "prompt":"How are you?",
        "flow_type": "conditional",
        "next_node_id": ["write_message","write_code"]
    },
    {
        "id":"12345678",
        "node_id":"write_code",
        "node_type":"write_code",
        "prompt":"How are you?",
        "flow_type": "linear",
        "next_node_id": ["evaluate_code"]
    },
    {
        "id":"12345678",
        "node_id":"evaluate_code",
        "node_type":"evaluate_code",
        "prompt":"How are you?",
        "flow_type": "linear",
        "next_node_id": ["END"]
    },
    {
        "id":"12345678",
        "node_id":"write_message",
        "node_type":"write_message",
        "prompt":"How are you?",
        "flow_type": "linear",
        "next_node_id": ["END"]
    },
]


_state: State = {
 "prompt":"Write a message",
    "response":None
}
graph_builder = StateGraph(State)
# Define Nodes here
# graph_builder.add_node("classify_message", classify_message)
# graph_builder.add_node("route_query", route_query)
# graph_builder.add_node("general_query", general_query)
# graph_builder.add_node("coding_query", coding_query)
# graph_builder.add_node("coding_validate_query", coding_validate_query)
#
#
# graph = graph_builder.compile()
# return graph
is_route_query_added=False
for node in data:
    req:Node=node

    function_tool_name  =   req.get("node_type")
    function_tool   =   distribute.get(req.get("node_type"))
    is_conditional  =   req.get("flow_type")    ==  "conditional"
    if is_conditional:
        print(f"graph_builder.add_node('route_query',route_query)")
        is_route_query_added=True
    if function_tool_name != "START" and function_tool_name != "END":
        print(f"graph_builder.add_node('{function_tool_name}',{function_tool_name})")

# class Node(TypedDict):
#     id: str
#     node_id: str
#     prompt:str
#     flow_type: str
#     next_node_id: List[str]
# # Define Edges from START to END
# graph_builder.add_edge(START, "classify_message")
# graph_builder.add_conditional_edges("classify_message", route_query)
# graph_builder.add_edge("general_query", END)
#
# graph_builder.add_edge("coding_query", "coding_validate_query")
# graph_builder.add_edge("coding_validate_query", END)
#   {
#         "id":"1j2uigbewiu2wke",
#         "node_id":"START",
#         "node_type":"START",
#         "prompt":"How are you?",
#         "flow_type": "linear",
#         "next_node_id": ["classify_message"]
#     },
#     {
#         "id":"12345678",
#         "node_id":"classify_message",
#         "node_type":"classify_message",
#         "prompt":"How are you?",
#         "flow_type": "conditional",
#         "next_node_id": ["write_message","write_code"]
#     },
print("---------")
print("---------")
for node in data:
    req:Node=node
    node_type    =   req.get("node_type")
    is_start    =   node_type    ==  "START"
    is_conditional  =   req.get("flow_type")    ==  "conditional"
    next_node=None
    if is_conditional:
        next_node = route_query
    else:
        if req.get("next_node_id")[0]=="classify_message":
            next_node = "classify_message"
        if req.get("next_node_id")[0]=="END":
            next_node = "END"
        node_name_by_id=req.get("next_node_id")[0] # TODO:get this node's type from DB
        next_node = node_name_by_id
    if is_start:
        print(f"graph_builder.add_edge(START, '{next_node}')")
    else:
        print(f"graph_builder.add_edge({node_type}, '{next_node}')")




# print(graph_builder)

# CONDITIONAL
#  [
#     {
#         "source": "1-684d858808dca10a34a65a53",
#         "target": "2-684d8a5608dca10a34a65a55",
#         "id": "xy-edge__1-684d858808dca10a34a65a53-2-684d8a5608dca10a34a65a55"
#     },
#     {
#         "source": "2-684d8a5608dca10a34a65a55",
#         "target": "3-684a0a2a14df3de4f4f6845d",
#         "id": "xy-edge__2-684d8a5608dca10a34a65a55-3-684a0a2a14df3de4f4f6845d"
#     },
#     {
#         "source": "3-684a0a2a14df3de4f4f6845d",
#         "target": "6-684e733dc2b59ec01fb72c77",
#         "id": "xy-edge__3-684a0a2a14df3de4f4f6845d-6-684e733dc2b59ec01fb72c77"
#     },
#     {
#         "source": "2-684d8a5608dca10a34a65a55",
#         "target": "4-684a0c5df84f78f814367574",
#         "id": "xy-edge__2-684d8a5608dca10a34a65a55-4-684a0c5df84f78f814367574"
#     },
#     {
#         "source": "4-684a0c5df84f78f814367574",
#         "target": "5-684a08e28f7c63eb043302d1",
#         "id": "xy-edge__4-684a0c5df84f78f814367574-5-684a08e28f7c63eb043302d1"
#     },
#     {
#         "source": "5-684a08e28f7c63eb043302d1",
#         "target": "6-684e733dc2b59ec01fb72c77",
#         "id": "xy-edge__5-684a08e28f7c63eb043302d1-6-684e733dc2b59ec01fb72c77"
#     }
# ]

# LINEAR

# [
#     {
#         "source": "4-684a0c5df84f78f814367574",
#         "target": "3-684a0a2a14df3de4f4f6845d",
#         "id": "xy-edge__4-684a0c5df84f78f814367574-3-684a0a2a14df3de4f4f6845d"
#     },
#     {
#         "source": "1-684d858808dca10a34a65a53",
#         "target": "4-684a0c5df84f78f814367574",
#         "id": "xy-edge__1-684d858808dca10a34a65a53-4-684a0c5df84f78f814367574"
#     },
#     {
#         "source": "3-684a0a2a14df3de4f4f6845
#         "target": "7-684e733dc2b59ec01fb72c77",
#         "id": "xy-edge__3-684a0a2a14df3de4f4f6845d-7-684e733dc2b59ec01fb72c77"
#     }
# ]

# [
#     {
#         "source": "4-684a0c5df84f78f814367574",
#         "target": "3-6853a91c8ed701f2efcd6fd1",
#         "id": "xy-edge__4-684a0c5df84f78f814367574-3-6853a91c8ed701f2efcd6fd1",
#         "tool_input":""
#     },
#     {
#         "source": "1-684d858808dca10a34a65a53",
#         "target": "4-684a0c5df84f78f814367574",
#         "id": "xy-edge__1-684d858808dca10a34a65a53-4-684a0c5df84f78f814367574",
#         "tool_input":""
#     },
#     {
#         "source": "3-6853a91c8ed701f2efcd6fd1",
#         "target": "7-684e733dc2b59ec01fb72c77",
#         "id": "xy-edge__3-6853a91c8ed701f2efcd6fd1-7-684e733dc2b59ec01fb72c77",
#         "tool_input":""
#     }
# ]