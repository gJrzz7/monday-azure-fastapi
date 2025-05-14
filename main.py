from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class ChallengePayload(BaseModel):
    challenge: str | None = None
    event: dict | None = None

@app.post("/webhook")
async def webhook(payload: ChallengePayload):
    # Se for o desafio do webhook, devolve o challenge como string pura
    if payload.challenge:
        return payload.challenge
    
    # Caso contrário, é um evento real — você lida com ele aqui
    print("Evento recebido:", payload.event)
    return {"ok": True}
