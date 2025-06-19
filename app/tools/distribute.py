from app.tools.conditional.classify_message import classify_message
from app.tools.conditional.route_query import route_query
from app.tools.converters.doc_to_pdf import doc_to_pdf
from app.tools.programmer.code_documentation import code_documentation
from app.tools.programmer.evaluate_code import evaluate_code
from app.tools.programmer.write_code import write_code
from app.tools.messaging.write_mail_and_send import send_mail
from app.tools.write_message import write_message

distribute={
    "conditional_routing":route_query,
    "write_code":write_code,
    "write_mail_and_send":send_mail,
    "write_message":write_message,
    "classify_message":classify_message,
    "evaluate_code":evaluate_code,
    "code_documentation":code_documentation,
    "doc_to_pdf":doc_to_pdf
}