import openai.types.chat
from pathlib import Path
import time
from typing import Literal
import json


from supabase import SupabaseException
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
)
from app.controllers.engine.tools.filmmaker.script_writer import SCRIPT_WRITER
from app.controllers.engine.tools.programmer.code_documentation import (
    CODE_DOCUMENTATION,
)
from app.controllers.engine.tools.save.save_to_flow_bucket import save_to_storage
from app.controllers.engine.tools.search.google_trends import GOOGLE_TRENDS

from app.models.meta import DocToPDF
from app.models.models import LinkToOpen, State, Response
from xhtml2pdf import pisa
from app.controllers.get_system_node_by_id import get_node_ui_loading_failed_message


async def manage_file_store(file_name: str, state: State):
    # node_data=json.loads(state.get("node_data").get("node_input"))
    # storage_type=node_data.get("storage")
    local_file_path = Path(f"./temp/{state.get("flow_id")}/{file_name}").resolve()
    # if storage_type=="g_drive":
    #     # look for drive auth in node_data
    #     return True
    # else:
    print("before save", local_file_path.exists())
    doc_response_path=await save_to_storage(
        fileName=file_name,
        flow_id=state.get("flow_id"),
        local_file_path=local_file_path,
    )
    
    return doc_response_path

DOC_TO_PDF="doc_to_pdf"

async def doc_to_pdf(state: State):
    print("🤖 --- doing doc_to_pdf",state)
    # code_documentation
    # check if it has incoming documents
    meta_list = state.get("response").get("meta")
    filename = ""
    content = ""
    # check if content in meta
    if len(meta_list) > 0:
        for meta_string in reversed(meta_list):
            if not content:
                meta_data = json.loads(meta_string)
                meta_data_type = meta_data.get("type")
                if meta_data_type == CODE_DOCUMENTATION:
                    content = meta_data.get("content")
                    filename = (
                        f"{meta_data.get("file_name_without_extension")}_{time.time()}"
                    )
                if meta_data_type == GOOGLE_TRENDS:
                    content = meta_data.get("description")
                    filename = f"{time.time_ns()}"
                if meta_data_type == SCRIPT_WRITER:
                    content = meta_data.get("content")
                    filename = meta_data.get("slug_name")
                    
    else:
        content = state.get("response").get("messages")[-1].get("content")
        filename = f"{time.time_ns()}"
        
    response_filename = convert_to_pdf(
        content_type="html",
        flow_id=state.get("flow_id"),
        output_path=filename,
        content=content,
    )
    try:
        document_path=await manage_file_store(file_name=response_filename, state=state)
        response_chat_data = ChatCompletionAssistantMessageParam(
            role="assistant", content="PDF Document generated."
        )
        doc_meta=DocToPDF(node_id=state.get("node_data").get("node_graph_id"),type=DOC_TO_PDF,url=document_path)
        meta=doc_meta.model_dump()
        link_to_open=LinkToOpen(label="Open Document",url=document_path, node_id=state.get("node_data").get("node_graph_id"),type=DOC_TO_PDF)
        response: Response = {
            "type": "show-documents",
            "messages": [*state.get("response").get("messages"),response_chat_data],
            "meta": [*state.get("response").get("meta"), json.dumps(meta)],
            "links_to_open":[*state.get("response").get("links_to_open"),json.dumps(link_to_open)]
        }
        state["response"] = response
        return state

    except SupabaseException as error:
        print(error)
        state["ui_response"] = get_node_ui_loading_failed_message(state.get("node_data").get("node_graph_id"))
        return state
    


def convert_to_pdf(
    content: str,
    output_path: str,
    flow_id: str,
    content_type: Literal["markdown", "html"] = "markdown",
) -> str:
    # Convert markdown to HTML if needed
    if content_type.lower() == "markdown":
        html_content = f"""<div markdown="1" style="font-size:18px" >
        
        {content}
        
        </div>"""
    elif content_type.lower() == "html":
        html_content = content
    else:
        raise ValueError("content_type must be 'markdown' or 'html'")

    # Generate the PDF
    dir_path = Path(f"./temp/{flow_id}").resolve()
    dir_path.mkdir(parents=True, exist_ok=True)

    file_name = f"{output_path}.pdf"
    local_file_path = f"{dir_path}/{file_name}"
    is_success = convert_html_to_pdf(
        source_html=html_content, output_filename=local_file_path
    )
    if is_success:
        return file_name
    return None


def convert_html_to_pdf(source_html, output_filename):
    # with open("style.css") as css_file:
    #     css_content = css_file.read()
    with open(output_filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(
            # src=source_html, dest=result_file, default_css=css_content
            src=source_html,
            dest=result_file,
        )
        print("pisa_status ", pisa_status)
    return pisa_status.err == 0
