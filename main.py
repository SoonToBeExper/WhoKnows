from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Simple session storage
sessions = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_system_prompt(stage, topic):
    return f"""
    You are a Cambridge University Computer Science supervisor conducting a mock interview session.

    The topic is {topic}. This is part of a 3-stage supervision session: warm-up, core, and stretch.

    Your job is to challenge the student’s thinking, assess their reasoning, and simulate the tone and rigor of a real interview. You are calm, direct, and analytical — avoid excessive friendliness or over-explaining.

    Use a Socratic style: ask focused follow-up questions, probe assumptions, and push the student to justify their thoughts. Do not offer answers unless the student is truly stuck or explicitly asks for help.

    Keep each response short — a single, meaningful question or analytical observation is best. Do not say things like “Great job!” or “That’s correct” unless it's part of the interviewer’s realistic behavior.

    Never give full feedback mid-session. Only summarize at the end or when specifically asked to debrief.

    Throughout the session, adapt your questioning based on the current stage ({stage}) and the student’s recent responses.
    """
    

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    user_input = data["message"]
    
    # Initialize or get session
    if session_id not in sessions:
        sessions[session_id] = {
            "stage": "warm-up",
            "topic": "Recursion",
            "history": [],
            "score": None
        }
    
    session = sessions[session_id]
    system_prompt = get_system_prompt(session["stage"], session["topic"])
    
    messages = [
        {"role": "system", "content": system_prompt},
        *session["history"],
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )

    ai_response = response["choices"][0]["message"]["content"]
    
    # Update session history
    session["history"].extend([
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": ai_response}
    ])

    return {
        "reply": ai_response,
        "stage": session["stage"],
        "session_id": session_id
    }

@app.post("/report")
async def generate_report(request: Request):
    data = await request.json()
    session_id = data["session_id"]
    
    if session_id not in sessions:
        return {"error": "Session not found"}
    
    session = sessions[session_id]
    
    # Generate final feedback
    feedback_prompt = f"""Based on this interview session about {session['topic']}, 
    provide a Cambridge-style supervision report including:
    1. Overall score (1-10)
    2. Strengths in logic and problem-solving
    3. Areas for improvement
    4. Final recommendation
    
    Interview history:
    {session['history']}"""
    
    feedback_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": feedback_prompt}]
    )
    
    return {
        "feedback": feedback_response["choices"][0]["message"]["content"],
        "session_id": session_id
    } 