from app.controllers.tools.conditional.classify_message import classify_message
from app.controllers.tools.conditional.route_query import route_query
from app.controllers.tools.converters.doc_to_pdf import doc_to_pdf
from app.controllers.tools.programmer.code_documentation import code_documentation
from app.controllers.tools.programmer.evaluate_code import evaluate_code
from app.controllers.tools.programmer.write_code import write_code
from app.controllers.tools.messaging.write_mail_and_send import send_mail
from app.controllers.tools.search.search_tavily import tavily_search
from app.controllers.tools.write_message import write_message

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