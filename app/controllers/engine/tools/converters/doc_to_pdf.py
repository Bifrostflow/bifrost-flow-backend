from pathlib import Path
import time
from typing import Literal
import json

from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
)

from app.controllers.engine.tools.programmer.code_documentation import (
    CODE_DOCUMENTATION,
)
from app.controllers.engine.tools.save.save_to_flow_bucket import save_to_storage
from app.controllers.engine.tools.tools_helpers.manage_messages import (
    manage_flow_chat_history,
)
from app.models.models import State, ChatHistory, Response


from xhtml2pdf import pisa


async def manage_file_store(file_name: str, state: State):
    # node_data=json.loads(state.get("node_data").get("node_input"))
    # storage_type=node_data.get("storage")
    local_file_path = Path(f"./temp/{state.get("flow_id")}/{file_name}").resolve()
    # if storage_type=="g_drive":
    #     # look for drive auth in node_data
    #     return True
    # else:
    print("before save", local_file_path.exists())
    await save_to_storage(
        fileName=file_name,
        flow_id=state.get("flow_id"),
        local_file_path=local_file_path,
    )
    return True


async def doc_to_pdf(state: State):
    print("🤖 --- doing doc_to_pdf", state.get("node_data"))
    # code_documentation
    # check if it has incoming documents
    meta = state.get("response").get("meta")
    if len(meta) > 0:
        # return state
        for item in meta:
            # load documents to json
            json_data = json.loads(item)
            if json_data.get("type") == CODE_DOCUMENTATION:
                content = json_data.get("content")
                file_name_without_extension = (
                    f"{json_data.get("file_name_without_extension")}_{time.time()}"
                )
                # write pdf to local_temp
                # upload pdf to remote
                filename = convert_to_pdf(
                    content_type="html",
                    flow_id=state.get("flow_id"),
                    output_path=file_name_without_extension,
                    content=content,
                )
                await manage_file_store(file_name=filename, state=state)
        state["ui_response"] = "Added to queue"
        return state
    else:
        tool_chat = ChatCompletionUserMessageParam(role="user", content="")

        # Create chat data
        chat_data = ChatHistory(state=state, tool_prompt=tool_chat)
        messages = manage_flow_chat_history(data=chat_data)
        content = messages[0].get("content")
        filename = convert_to_pdf(
            flow_id=state.get("flow_id"),
            content=content,
            content_type="html",
            output_path=f"{time.time()}",
        )
        if filename:
            # save to selected storage
            await manage_file_store(file_name=filename, state=state)
            response_chat_data = ChatCompletionAssistantMessageParam(
                role="assistant", content="Document successfully generated."
            )
            messages.append(response_chat_data)
            response: Response = {
                "type": state.get("response").get("type"),
                "messages": messages,
                "meta": state.get("response").get("meta"),
            }
            state["response"] = response
            state["ui_response"] = "Document successfully generated."
            return state
        else:
            response: Response = {
                "type": state.get("response").get("type"),
                "messages": messages,
                "meta": state.get("response").get("meta"),
            }
            state["response"] = response
            state["ui_response"] = "Failed to generate."
            return state


def convert_to_pdf(
    content: str,
    output_path: str,
    flow_id: str,
    content_type: Literal["markdown", "html"] = "markdown",
) -> str:
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
    with open(output_filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(src=source_html, dest=result_file)
        print("pisa_status ", pisa_status)
    return pisa_status.err == 0
