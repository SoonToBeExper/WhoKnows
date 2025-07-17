from fastapi import APIRouter, HTTPException
from typing import List, Dict
from ..models.interview import InterviewSession, InterviewMessage, InterviewStage
from ..models.requests import CreateSessionRequest, SendMessageRequest
from ..services.interview_service import InterviewService
from datetime import datetime
import uuid

router = APIRouter()
interview_service = InterviewService()
sessions: Dict[str, InterviewSession] = {}

@router.post("/sessions", response_model=InterviewSession)
async def create_session(request: CreateSessionRequest):
    session_id = str(uuid.uuid4())
    session = InterviewSession(
        session_id=session_id,
        user_id=request.user_id,
        topic=request.topic,
        stages=[InterviewStage(name="warm-up", start_time=datetime.now())]
    )
    sessions[session_id] = session
    return session

@router.get("/sessions/{session_id}", response_model=InterviewSession)
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

@router.post("/sessions/{session_id}/messages", response_model=str)
async def send_message(session_id: str, request: SendMessageRequest):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    session.add_message("user", request.message)
    
    response = interview_service.generate_response(session, request.message)
    session.add_message("assistant", response)
    
    return response

@router.post("/sessions/{session_id}/advance", response_model=str)
async def advance_stage(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    current_stage = next((s for s in session.stages if s.name == session.stage), None)
    if current_stage:
        current_stage.end_time = datetime.now()
    
    new_stage = session.advance_stage()
    session.stages.append(InterviewStage(name=new_stage, start_time=datetime.now()))
    
    return new_stage

@router.get("/sessions/{session_id}/feedback", response_model=str)
async def get_feedback(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return interview_service.generate_feedback(session) 