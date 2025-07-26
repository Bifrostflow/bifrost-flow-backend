import os
from fastapi import  File, Form, UploadFile
from openai import OpenAI
import requests
from jose import jwt
from app.controllers.run_flow import check_collaborator_access, get_user_keys
from app.models.response import APIResponse
from app.utils.constants import OPEN_AI_KEY

async def transcribe_audio_controller(token:str,flow_id:str= Form(...),audio: UploadFile = File(...)):
    jwks_url = os.getenv("JWKS") 
    jwks = requests.get(jwks_url).json()
    token_data = jwt.decode(token, jwks, algorithms=["RS256"])
    user_id = token_data["sub"]
    # ADD USERS CHECK FROM FLOW TABLE
    if not user_id:
            res = APIResponse(
                isSuccess=False, message="Authorization failed.", data=None, error=None
            )
            return res
    has_access=await check_collaborator_access(user_id=user_id,flow_id=flow_id)
    if not has_access:
        res = APIResponse(
                isSuccess=False, message="Access denied.", data=None, error=None
            )
        return res
    try:
        # Read audio file bytes
        audio_bytes = await audio.read()
        print("audio_bytes: ",audio_bytes)
        keys=await get_user_keys(user_id=user_id,flow_id=flow_id)
        user_openai_key = keys.get(OPEN_AI_KEY)
        client = OpenAI(api_key=user_openai_key)
        # Save temporarily to disk (required by OpenAI API)
        temp_file_path = f"temp_{audio.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(audio_bytes)

        # Use Whisper-1 for transcription
        print("temp_file_path: ",temp_file_path)
        with open(temp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        # Delete the temp file
        os.remove(temp_file_path)

        return APIResponse(data={"text": transcript.text},error=None,isSuccess=True,message="success")
    except Exception as e:
        return APIResponse(data=None,error=None,isSuccess=False,message=f"failed: {e}")