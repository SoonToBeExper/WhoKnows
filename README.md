# WhoKnows
Just a personal
This project helps students understand and practice in a university interview environment, something that would probably help out many students. However, since I've obviously only done the cs interview at cam and jmc interview at imperial I will be starting off trying to emulate those interviews first.

# Week 1 tasks
- understand code
- Write unit tests for InterviewSession.add_message() + InterviewSession.advance_stage() + InterviewSession.get_stage_duration()
- Set up FastAPI
- Implement simple interview logic - (select questions based on topic and skill level --> advance stages based on message count or time spent --> give a score)
I think that's about it. If it's finished early then we can deal with some other stuff after but tbh not much else.

# note
uploaded the other files needed aswell, forgot to put them up yday - includes some html css etc + all the api stuff to connect the different api's to each other.

# Updates
wrote up code for unit tests for addmessages, advance stage and stage duration
all tests successfully passed using pytest
tweaked interview.py file by changing the advance_stage section of the code to now track the start and end time of each stage 

# Update 2
Currently directories are messed up and committing from vscode is difficult since file structure is horrible
