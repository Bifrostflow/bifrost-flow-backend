from app.controllers.engine.tools.conditional.classify_message import classify_message
from app.controllers.engine.tools.conditional.route_query import route_query
from app.controllers.engine.tools.converters.doc_to_pdf import doc_to_pdf
from app.controllers.engine.tools.filmmaker.script_writer import script_writer
from app.controllers.engine.tools.messaging.write_mail_and_send import send_mail
from app.controllers.engine.tools.programmer.code_documentation import (
    code_documentation,
)
from app.controllers.engine.tools.programmer.evaluate_code import evaluate_code
from app.controllers.engine.tools.programmer.write_code import write_code
from app.controllers.engine.tools.write_message import write_message
from app.controllers.engine.tools.search.search_tavily import tavily_search


distribute = {
    "conditional_routing": route_query,
    "write_code": write_code,
    "write_mail_and_send": send_mail,
    "write_message": write_message,
    "classify_message": classify_message,
    "evaluate_code": evaluate_code,
    "code_documentation": code_documentation,
    "doc_to_pdf": doc_to_pdf,
    "tavily_search": tavily_search,
    "script_writer": script_writer,
}
