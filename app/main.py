from dotenv import load_dotenv
from fastapi import FastAPI
from app.apis.chat_router import router as chat_router
from app.apis.agent_router import router as agent_router

load_dotenv()

app = FastAPI(title="FinBridge GraphRAG", version="0.1.0")

app.include_router(chat_router)
app.include_router(agent_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
