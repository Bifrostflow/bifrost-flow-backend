from app.db.template_data import template_db

# from app.utils.utils import serialize_doc


def use_get_templates():
    nodes_cursor = template_db.get_by_state("public")
    templates = []
    for template in nodes_cursor:
        templates.append(template)
    return templates
