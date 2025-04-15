from openai import OpenAI
import os
from dotenv import load_dotenv


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

AgentResponse = []
UserResponse = []
Dialogue = {}

def get_recurring_prompt():
    return f"""
    You are a Cambridge University Computer Science supervisor conducting a mock interview session.

    This is part of a 3-stage supervision session: warm-up, core, and stretch.

    Your job is to challenge the student’s thinking, assess their reasoning, and simulate the tone and rigor of a real interview. You are calm, direct, and analytical — avoid excessive friendliness or over-explaining.

    Use a Socratic style: ask focused follow-up questions, probe assumptions, and push the student to justify their thoughts. Do not offer answers unless the student is truly stuck or explicitly asks for help.

    Keep each response short — a single, meaningful question or analytical observation is best. Do not say things like “Great job!” or “That’s correct” unless it's part of the interviewer’s realistic behavior.

    Never give full feedback mid-session. Only summarize at the end or when specifically asked to debrief.

     Throughout the session, adapt your questioning to become more complex and use the recent dialogue : ({Dialogue}) Please speak as if you are actually in a dialogue and not like text.Once the session has been concluded, print the word "break" only,nothing else.
    """

def get_system_prompt(stage, topic):
    return f"""
    You are a Cambridge University Computer Science supervisor conducting a mock interview session.

     This is part of a 3-stage supervision session: warm-up, core, and stretch.

    Your job is to challenge the student’s thinking, assess their reasoning, and simulate the tone and rigor of a real interview. You are calm, direct, and analytical — avoid excessive friendliness or over-explaining.

    Use a Socratic style: ask focused follow-up questions, probe assumptions, and push the student to justify their thoughts. Do not offer answers unless the student is truly stuck or explicitly asks for help.

    Keep each response short — a single, meaningful question or analytical observation is best. Do not say things like “Great job!” or “That’s correct” unless it's part of the interviewer’s realistic behavior.

    Never give full feedback mid-session. Only summarize at the end or when specifically asked to debrief.

   
    """


response = client.chat.completions.create(
    model = 'openai/gpt-4o',
    messages = [
        {"role" : "user",
        "content" : get_system_prompt("Warm up","mathematical logic"),
        }
    ],
)

def recurring(userAnswer):
    if userAnswer == None:      #If there is no user input then the chat is fresh and must start a new interview
        print(response)
        AgentResponse.append(response)
        NewUserAnswer = input()
        Dialogue.update({response:NewUserAnswer})           #Dialogue dictionary saved so api can recall
        return recurring(NewUserAnswer)
    else:                       #If there is an input then the dialogue is traced to check previous answers
        reply = client.chat.completions.create(         
            model = 'openai/gpt-4o',
            messages = [
            {"role" : "user",
            "content" : get_system_prompt("Warm up",get_recurring_prompt()),
             }
        ],
        )
        hi = reply.choices[0].message.content
        if hi == "break":
            exit
        print(hi)
        NewUserAnswer = input()
        return recurring(NewUserAnswer)

    



recurring(None)