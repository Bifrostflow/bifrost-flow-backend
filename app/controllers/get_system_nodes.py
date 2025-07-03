# from app.utils.utils import serialize_doc
from app.db.jsonDB import tools_db


def use_get_system_nodes():
    nodes_cursor = tools_db.get_by_state("active")
    nodes = []
    for node in nodes_cursor:
        nodes.append(node)
    return nodes
