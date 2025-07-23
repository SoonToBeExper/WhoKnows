from openai import OpenAI
import os
from typing import List, Dict
from datetime import datetime
from ..models.interview import InterviewSession, InterviewMessage, InterviewStage

class InterviewService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )

    def get_system_prompt(self, session: InterviewSession) -> str:
        topic_prompts = {
            "logical_puzzles": """
            You are a Cambridge University Computer Science supervisor conducting a mock interview session focused on logical thinking.
            The session will involve puzzles and problems that test the candidate's ability to think logically and systematically.
            Start with simple puzzles and gradually increase complexity. Focus on how the candidate approaches problems and their reasoning process.
            """,
            "pattern_recognition": """
            You are a Cambridge University Computer Science supervisor conducting a mock interview session focused on pattern recognition.
            Present sequences, shapes, or scenarios where the candidate needs to identify and explain patterns.
            Start with simple patterns and gradually introduce more complex ones. Focus on how the candidate identifies and describes patterns.
            """,
            "problem_decomposition": """
            You are a Cambridge University Computer Science supervisor conducting a mock interview session focused on problem decomposition.
            Present real-world problems that can be broken down into smaller, manageable parts.
            Start with simple problems and gradually increase complexity. Focus on how the candidate breaks down problems and organizes their thoughts.
            """,
            "abstract_thinking": """
            You are a Cambridge University Computer Science supervisor conducting a mock interview session focused on abstract thinking.
            Present scenarios that require thinking beyond concrete examples to general principles.
            Start with simple abstractions and gradually increase complexity. Focus on how the candidate generalizes from specific cases.
            """,
            "algorithmic_thinking": """
            You are a Cambridge University Computer Science supervisor conducting a mock interview session focused on algorithmic thinking.
            Present problems that require step-by-step solutions, focusing on the process rather than the answer.
            Start with simple processes and gradually increase complexity. Focus on how the candidate structures their approach.
            """
        }

        base_prompt = f"""
        You are conducting a Cambridge-style interview to assess a candidate's potential for studying Computer Science.
        The topic is {session.topic}. This is part of a 3-stage supervision session: warm-up, core, and stretch.
        Current stage: {session.stage}

        Your job is to:
        1. Challenge the candidate's thinking and assess their reasoning
        2. Focus on how they approach problems, not just the answers
        3. Ask follow-up questions to understand their thought process
        4. Push them to justify their reasoning
        5. Help them explore different approaches if they get stuck

        Keep responses short and focused. Do not give away solutions.
        Never say things like "Great job!" or "That's correct" unless it's part of realistic interviewer behavior.
        Only give feedback at the end or when specifically asked.

        {topic_prompts.get(session.topic, topic_prompts["logical_puzzles"])}
        """

        return base_prompt

    def generate_response(self, session: InterviewSession, user_input: str) -> str:
        messages = [
            {"role": "system", "content": self.get_system_prompt(session)},
            *[{"role": msg.role, "content": msg.content} for msg in session.messages],
            {"role": "user", "content": user_input}
        ]

        response = self.client.chat.completions.create(
            model="openai/gpt-4o",
            messages=messages
        )

        return response.choices[0].message.content

    def generate_feedback(self, session: InterviewSession) -> str:
        transcript = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in session.messages
        ])

        prompt = f"""
        You are a Cambridge Computer Science supervisor.

        Based on the following mock interview transcript on the topic of {session.topic}, write a supervisor-style report focusing on the candidate's potential for Computer Science. Assess:

        1. **Logical Thinking (1–10)**
           - Ability to reason systematically
           - Clarity of thought
           - Approach to problem-solving

        2. **Pattern Recognition (1–10)**
           - Ability to identify patterns
           - Generalization skills
           - Abstraction ability

        3. **Problem-Solving Approach (1–10)**
           - Methodical thinking
           - Breaking down complex problems
           - Exploring multiple solutions

        4. **Communication (1–10)**
           - Clarity of explanation
           - Ability to articulate thoughts
           - Response to feedback

        5. **Progression**: (Warm-up, Core, Stretch)
           - How they developed through the session
           - Areas of improvement
           - Strengths demonstrated

        6. **Overall Potential for CS (1–10)**
           - Natural aptitude
           - Learning capacity
           - Problem-solving mindset

        7. **Recommendation**
           - Specific areas to develop
           - Suggested next steps
           - Potential for success in CS

        Transcript:
        {transcript}
        """

        response = self.client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content 