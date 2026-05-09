from fastapi import FastAPI
from pydantic import BaseModel
from agent1 import run_agent
from agent1 import run_agent, chat_history

app = FastAPI()

class UserMessage(BaseModel):
    message: str

@app.get("/")
def home():
    return {"status": "Agent is running"}

@app.post("/chat")
def chat(user: UserMessage):
    result = run_agent(user.message)
    return {
        "you":   user.message,
        "agent": result
    }
@app.get("/history")
def history():
    return {"history": chat_history()}