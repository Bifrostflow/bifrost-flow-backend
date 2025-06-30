from app.models.models import State

def send_mail(state:State):
    state["ui_response"] = "Mail Sent."
    return state
