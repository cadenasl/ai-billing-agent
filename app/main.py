from fastapi import FastAPI

from app.api.routes import chat, health

app = FastAPI(title="Billing Agent API")

app.include_router(health.router)
app.include_router(chat.router)