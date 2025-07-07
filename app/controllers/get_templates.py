from app.db.template_data import template_db


def use_get_templates():
    nodes_cursor = template_db.get_by_state("public")
    templates = []
    for template in nodes_cursor:
        templates.append(template)
    return {
        "isSuccess": True,
        "data": templates,
        "message": "",
    }

def use_get_template_by_id(id:str):
    template = template_db.get_by_id(id=id)
    return {
        "isSuccess": True,
        "data": template,
        "message": "",
    }
