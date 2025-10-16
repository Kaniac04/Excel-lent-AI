
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
import uvicorn
from interview_service import InterviewSession
from services.logger_service import get_logger
from services.connections_service import test_all_services
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Interview Session API")

interview_params = {}
sessions = {}

logger = get_logger("main")


class InterviewRequest(BaseModel):
    name: str


class ResponseRequest(BaseModel):
    session_id: str
    user_input: str

class ParamRequest(BaseModel):
    interview_topic : str
    description : Optional[str] = None

@app.post("/set_params")
async def set_params(request: ParamRequest):
    interview_params["topic"] = request.interview_topic
    interview_params["description"] = request.description
    return {"message" : "Interview Set."}

@app.post("/interview")
async def start_interview(request: InterviewRequest):
    session_id = str(uuid4())
    message = f"Hello {request.name}, welcome to the interview! Please introduce yourself."
    sessions[session_id] = {"name": request.name, "history": [{"role": "Interviewer", "content": message}]}
    logger.info(f"Started interview session for {request.name} (session_id={session_id})")
    return {"session_id": session_id, "message": message}


@app.post("/response")
async def handle_response(request: ResponseRequest):
    session = sessions.get(request.session_id)
    if not session:
        logger.error(f"Session ID not found: {request.session_id}")
        raise HTTPException(status_code=404, detail="Session ID not found")

    session["history"].append({"role": "user", "content" : request.user_input})
    logger.info(f"Received user input for session {request.session_id}: {request.user_input}")
    interview_session = InterviewSession(session, interview_params)
    try:
        response_gen = await interview_session.generate_response(request)
        logger.info(f"Streaming response for session {request.session_id}")
        return StreamingResponse(response_gen, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error generating response for session {request.session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    logger.info("Performing checks...")
    check_bool,checks = test_all_services(
        llm_url="http://localhost:1234/v1/models"
    )
    if check_bool:
        logger.info("All services functioning perfectly!")
        logger.info("Starting FastAPI server...")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        logger.ingo(f"Initial Checks Failed for : {checks}")

