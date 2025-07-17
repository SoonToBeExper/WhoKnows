from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class InterviewStage(BaseModel):
    name: str  # warm-up, core, stretch
    start_time: datetime
    end_time: Optional[datetime] = None
    performance_score: Optional[float] = None

class InterviewMessage(BaseModel):
    role: str  # user or assistant
    content: str
    timestamp: datetime

class InterviewSession(BaseModel):
    session_id: str
    user_id: str
    topic: str
    stage: str = "warm-up"
    messages: List[InterviewMessage] = []
    stages: List[InterviewStage] = []
    created_at: datetime = datetime.now()
    overall_score: Optional[float] = None

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(InterviewMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        ))

    def advance_stage(self) -> str:
        now = datetime.now()

        # End the current stage if it's active
        if self.stages and self.stages[-1].name == self.stage and self.stages[-1].end_time is None:
            self.stages[-1].end_time = now

        # Advance stage logic
        if self.stage == "warm-up":
            self.stage = "core"
        elif self.stage == "core":
            self.stage = "stretch"
        else:
            return self.stage  # Already at final stage

        # Start the new stage
        self.stages.append(InterviewStage(
            name=self.stage,
            start_time=now
        ))

        return self.stage

    def get_stage_duration(self) -> float:
        current_stage = next((s for s in self.stages if s.name == self.stage), None)
        if current_stage and current_stage.end_time:
            return (current_stage.end_time - current_stage.start_time).total_seconds()
        return 0.0