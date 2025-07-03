from collections import defaultdict
from typing import List
from bson import ObjectId
from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from app.models.models import UserEdge, NodeData
from app.db.mongo import node_collection
from app.controllers.engine.tools.conditional.classify_message import CLASSIFY_MESSAGE, classify_message
from app.controllers.engine.tools.distribute import distribute
from app.models.models import  Node, State
from app.controllers.engine.tools.tools_helpers.with_node_data import with_node_data


async def convert_edges_to_nodes(edges: List[UserEdge]) -> List[Node]:
    node_map = defaultdict(list)
    node_input_map = dict()

    # Step 1: Build mapping of source -> list of targets
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        node_input = edge["tool_input"]

        node_map[source].append(target)
        node_input_map[source]=node_input

    nodes: List[Node] = []
    for source_node_id, targets in node_map.items():
        node_id=source_node_id.split("-")[1]
        found_node = await node_collection.find_one({"_id":ObjectId(node_id)},{"_id":0,"type": 1})
        node_type = found_node.get("type")

        # Flow type based on node_type
        flow_type = "conditional" if (len(targets)>1) else "linear"

        # Node ID and ID field logic
        node_id:str = source_node_id
        generated_id = node_id + "-" + "-".join(targets)
        node_input:str|None =node_input_map.get(node_id)
        print("===>>> ",node_input)
        node: Node = {
            "id": generated_id,
            "node_id": node_id,
            "node_type": node_type,
            "prompt": "",  # placeholder
            "flow_type": flow_type,
            "next_node_id": targets,
            "node_input": node_input
        }
        nodes.append(node)

    return nodes

async def create_graph(nodes:List[Node])->CompiledStateGraph:
    graph_builder = StateGraph(State)

    # CREATE NODES
    classify_count=1
    for node in nodes:
        req: Node = node
        node_graph_id=req.get("node_id")
        node_db_id=node_graph_id.split('-')[1]
        node_type_tool = distribute.get(req.get("node_type"))
        is_conditional = req.get("flow_type") == "conditional"
        node_data=await node_collection.find_one({"_id":ObjectId(node_db_id)},{"_id":0,"category": 1})
        node_input=req.get("node_input")
        print("node input here ",node_input)

        if is_conditional:
            classify_node_id=f"{classify_count}-{CLASSIFY_MESSAGE}"
            print(f"61: graph_builder.add_node({classify_node_id},{classify_message})")
            next_nodes_graph_id=req.get("next_node_id")
            data=NodeData(node_graph_id=classify_node_id,next_nodes=next_nodes_graph_id,node_input=node_input)
            graph_builder.add_node(classify_node_id,with_node_data(data=data,tool=classify_message))
            classify_count=classify_count+1

        if node_data.get("category")!="initiate":
            print(f"63: graph_builder.add_node({node_graph_id},{node_type_tool})")
            req.get("next_node_id")
            data=NodeData(node_graph_id=node_graph_id,next_nodes=req.get("next_node_id"),node_input=node_input)
            graph_builder.add_node(node_graph_id,with_node_data(data=data,tool=node_type_tool))


    # CREATE EDGES
    classification_id_tracker=dict()
    classify_count_edge=0
    for node in nodes:
        req: Node = node
        node_type = req.get("node_type")

        is_start = node_type == "on_prompt"
        is_conditional = req.get("flow_type") == "conditional"
        next_edge_graph_id=node.get('next_node_id')[0]
        next_edge_db_id=next_edge_graph_id.split("-")[1]
        next_edge_data=await node_collection.find_one({"_id":ObjectId(next_edge_db_id)},{"_id":0,"category": 1,"type":1})

        if is_start:
            if next_edge_data.get("category")=='conditional':
                # manage classification id
                classification_id = ""
                for key, value in classification_id_tracker.items():
                    if not value:
                        classification_id = key
                        classification_id_tracker[classification_id] = True
                if classification_id == "":
                    classify_count_edge = classify_count_edge + 1
                    classification_id = f"{classify_count_edge}-{CLASSIFY_MESSAGE}"
                    classification_id_tracker[classification_id] = False
                # manage classification id

                print(f"82: graph_builder.add_edge({START},{classification_id})")
                graph_builder.add_edge(START,classification_id)
            else:
                print(f"85: graph_builder.add_edge({START},{next_edge_graph_id})")
                graph_builder.add_edge(START,next_edge_graph_id)
        elif is_conditional:
            next_routing_tool=distribute.get(req.get("node_type"))
            # manage classification id
            classification_id = ""
            for key, value in classification_id_tracker.items():
                if not value:
                    classification_id = key
                    classification_id_tracker[classification_id] = True
            if classification_id == "":
                classify_count_edge = classify_count_edge + 1
                classification_id = f"{classify_count_edge}-{CLASSIFY_MESSAGE}"
                classification_id_tracker[classification_id] = False
            # manage classification id

            print(f"89: graph_builder.add_conditional_edges({classification_id}, {next_routing_tool})")
            graph_builder.add_conditional_edges(classification_id, next_routing_tool)
        else:
            start_edge_graph_id=node.get('node_id')
            if next_edge_data.get("category")=='conditional':
                # manage classification id
                classification_id = ""
                for key, value in classification_id_tracker.items():
                    if not value:
                        classification_id = key
                        classification_id_tracker[classification_id] = True
                if classification_id == "":
                    classify_count_edge = classify_count_edge + 1
                    classification_id = f"{classify_count_edge}-{CLASSIFY_MESSAGE}"
                    classification_id_tracker[classification_id] = False
                # manage classification id
                print(f"96: graph_builder.add_edge({start_edge_graph_id},{classification_id})")
                graph_builder.add_edge(start_edge_graph_id,classification_id)
            elif next_edge_data.get("category")=='close':
                print(f"99: graph_builder.add_edge({start_edge_graph_id},{END})")
                graph_builder.add_edge(start_edge_graph_id,END)
            else:
                print(f"102: graph_builder.add_edge({start_edge_graph_id},{next_edge_graph_id})")
                graph_builder.add_edge(start_edge_graph_id,next_edge_graph_id)

    return graph_builder.compile()