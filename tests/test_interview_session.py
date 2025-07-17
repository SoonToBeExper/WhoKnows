
from models.interview import InterviewSession, InterviewStage
from datetime import datetime
import time  

def test_add_message():
    session = InterviewSession(
        session_id="123",
        user_id="abc",
        topic="logical_puzzles"
    )
    session.add_message("user", "Hello Mustafa!")
    assert len(session.messages) == 1
    assert session.messages[0].role == "user"
    assert session.messages[0].content == "Hello Mustafa!"

def test_advance_stage():
    session = InterviewSession(
        session_id="456",
        user_id="def",
        topic="pattern_recognition"
    )
    assert session.stage == "warm-up"
    session.advance_stage()
    assert session.stage == "core"
    session.advance_stage()
    assert session.stage == "stretch"
    session.advance_stage()
    assert session.stage == "stretch"

def test_get_stage_duration():
    session = InterviewSession(
        session_id="789",
        user_id="ghi",
        topic="abstract_thinking"
    )

    # Simulate a stage that has already started and ended
    start_time = datetime.now()
    time.sleep(1)
    end_time = datetime.now()

    session.stages.append(InterviewStage(
        name="warm-up",
        start_time=start_time,
        end_time=end_time
    ))

    session.stage = "warm-up"
    duration = session.get_stage_duration()
    assert duration >= 1.0 and duration < 2.0


