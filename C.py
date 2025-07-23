from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

dialogue_history = []



def get_prompt(stage, topic, history):
    history_text = "\n".join([f"Student: {h['user']}\nSupervisor: {h['assistant']}" for h in history])
    return f"""
You are a Cambridge University Computer Science supervisor conducting a mock interview session.

The topic is {topic}. This is part of a 3-stage supervision session: warm-up, core, and stretch.

Your job is to challenge the student’s thinking, assess their reasoning, and simulate the tone and rigor of a real interview. You are calm, direct, and analytical — still be friendly but not too overfriendly. Introduce yourself and begin

Use a Socratic style: ask focused follow-up questions, probe assumptions, and push the student to justify their thoughts. Do not offer answers unless the student is truly stuck or explicitly asks for help.

Keep each response short — a single, meaningful question or analytical observation is best. Do not say things like “Great job!” or “That’s correct” unless it's part of the interviewer’s realistic behavior.

Never give full feedback mid-session. Only summarize at the end or when specifically asked to debrief.

This is the ongoing dialogue so far:
{history_text}

Now continue the interview. Speak naturally as if you're live in dialogue.
If the session is concluded, say only "break".
"""

def format_transcript(dialogue):
    return "\n".join([
        f"Student: {entry['user']}\nSupervisor: {entry['assistant']}"
        for entry in dialogue
    ])



def generate_score_report(dialogue, topic):
    transcript = format_transcript(dialogue,topic)

    prompt = f"""
You are a Cambridge Computer Science supervisor.

Based on the following mock interview transcript on the topic of {topic}, write a supervisor-style report in this format:

1. **Reasoning & Problem Solving (1–10)**
2. **Communication (1–10)**
3. **Responsiveness (1–10)**
4. **Progression**: (Warm-up, Core, Stretch)
5. **Strengths**
6. **Areas for Improvement**
7. **Overall Interview Score (1–10)**
8. **Recommendation**

Transcript:
{transcript}
"""

    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    print("\n📋 INTERVIEW REPORT:\n")
    print(response.choices[0].message.content)


def interview_loop(stage="warm-up", topic="further mathematics a level"):
    InterviewS = True
    while InterviewS:
        prompt = get_prompt(stage, topic, dialogue_history)
        
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        supervisor_reply = response.choices[0].message.content
        print(f"\n🧑‍🏫 Supervisor: {supervisor_reply}\n")

        if supervisor_reply.strip().lower() == "break":
            print("Interview ended.")
            InterviewS = False

        user_input = input("👨‍🎓 You: ")
        dialogue_history.append({
            "user": user_input,
            "assistant": supervisor_reply
        })
    generate_score_report(dialogue_history,topic)

# Start the loop
interview_loop()
