import time
from typing import Literal
import json

from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam, \
    ChatCompletionAssistantMessageParam

from app.models.models import State, ChatHistory, Response
from app.tools.programmer.code_documentation import CODE_DOCUMENTATION

from xhtml2pdf import pisa

from app.tools.tools_helpers.manage_messages import manage_flow_chat_history


async def doc_to_pdf(state:State):
    print("🤖 --- doing doc_to_pdf", state.get("node_data"))
    # code_documentation
    # check if it has incoming documents
    meta = state.get("response").get("meta")
    if len(meta)>0:
        # return state
        for item in meta:
            # load documents to json
            json_data =json.loads(item)
            if json_data.get("type")==CODE_DOCUMENTATION:
                content=json_data.get("content")
                file_name_without_extension=json_data.get("file_name_without_extension")
                # write pdf to local_temp
                # upload pdf to remote
                convert_to_pdf(content,"html",file_name_without_extension)
        return state
    else:
        tool_chat = ChatCompletionUserMessageParam(role="user", content="")

        # Create chat data
        chat_data = ChatHistory(state=state, tool_prompt=tool_chat)
        messages = manage_flow_chat_history(data=chat_data)
        content = messages[0].get("content")
        print("content: ",content)
        convert_to_pdf(content, "html", f"{time.time()}")
        response_chat_data = ChatCompletionAssistantMessageParam(role="assistant", content="Document successfully generated.")
        messages.append(response_chat_data)

        response: Response = {
            "type": state.get("response").get("type"),
            "messages": messages,
            "meta": [*state.get("response").get("meta"),
                     json.dumps(meta)
                     ]
        }
        state["response"] = response
        return  state

def convert_to_pdf(content: str, content_type: Literal["markdown","html"] = "markdown", output_path: str="") -> str:
    # Convert markdown to HTML if needed
    if content_type.lower() == "markdown":
        html_content = f"""<div markdown="1" >
        
        {content}
        
        </div>"""
    elif content_type.lower() == "html":
        html_content = content
    else:
        raise ValueError("content_type must be 'markdown' or 'html'")

    # Generate the PDF
    file_name=f"{output_path}.pdf"
    is_success=convert_html_to_pdf(html_content,file_name)
    return file_name




def convert_html_to_pdf(source_html, output_filename):
    with open(output_filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(src=source_html, dest=result_file)
        print("pisa_status ",pisa_status)
    return pisa_status.err == 0
