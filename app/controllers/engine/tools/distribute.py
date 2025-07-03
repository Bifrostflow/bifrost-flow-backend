from app.controllers.engine.tools import write_message
from app.controllers.engine.tools.conditional import classify_message, route_query
from app.controllers.engine.tools.converters import doc_to_pdf
from app.controllers.engine.tools.messaging.write_mail_and_send import send_mail
from app.controllers.engine.tools.programmer import code_documentation, evaluate_code, write_code
from app.controllers.engine.tools.search.search_tavily import tavily_search


distribute={
    "conditional_routing":route_query,
    "write_code":write_code,
    "write_mail_and_send":send_mail,
    "write_message":write_message,
    "classify_message":classify_message,
    "evaluate_code":evaluate_code,
    "code_documentation":code_documentation,
    "doc_to_pdf":doc_to_pdf,
    "tavily_search":tavily_search,
}