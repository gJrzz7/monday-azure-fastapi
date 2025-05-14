from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

MONDAY_API_KEY = os.getenv("eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUwOTA5Njc2NSwiYWFpIjoxMSwidWlkIjo3NTczODMwOSwiaWFkIjoiMjAyNS0wNS0wNlQxNjozNzowOS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6Mjk0MDA0ODQsInJnbiI6InVzZTEifQ.BvAgqehIqjQEjwBdm4EV6nSPeT89ta2kVK06BzkUTHk")
AZURE_TOKEN = os.getenv("eyJ0eXAiOiJKV1QiLCJub25jZSI6InNTNlVjdVJ4Yk9pT3d4dHgyeGFFS3Rla21Wa1EzM3BhRmVXS01uZ1BnWlkiLCJhbGciOiJSUzI1NiIsIng1dCI6IkNOdjBPSTNSd3FsSEZFVm5hb01Bc2hDSDJYRSIsImtpZCI6IkNOdjBPSTNSd3FsSEZFVm5hb01Bc2hDSDJYRSJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8xNDM2ZDMzMC1lNjZmLTQ5NGEtYTg3NS0wMTlhYjA4ZjBmYjIvIiwiaWF0IjoxNzQ3MjI0Njg0LCJuYmYiOjE3NDcyMjQ2ODQsImV4cCI6MTc0NzIyODU4NCwiYWlvIjoiazJSZ1lIRDF1U1R4NGx2bjdmMTdGcXlkZUdwWlBnQT0iLCJhcHBfZGlzcGxheW5hbWUiOiJVc2VyQ3JlYXRvckJvdCIsImFwcGlkIjoiZmY2YTM5ZDEtZjRhYy00Y2I1LTlhN2UtMmE1NjA3NTYwMGIwIiwiYXBwaWRhY3IiOiIxIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvMTQzNmQzMzAtZTY2Zi00OTRhLWE4NzUtMDE5YWIwOGYwZmIyLyIsImlkdHlwIjoiYXBwIiwib2lkIjoiMzAwMTYzZTktMDIxYy00ZTIzLWFlN2YtZjViOGYzNWQ1Mjg4IiwicmgiOiIxLkFTVUFNTk0yRkdfbVNrbW9kUUdhc0k4UHNnTUFBQUFBQUFBQXdBQUFBQUFBQUFEdEFBQWxBQS4iLCJyb2xlcyI6WyJVc2VyLlJlYWRXcml0ZS5BbGwiXSwic3ViIjoiMzAwMTYzZTktMDIxYy00ZTIzLWFlN2YtZjViOGYzNWQ1Mjg4IiwidGVuYW50X3JlZ2lvbl9zY29wZSI6IlNBIiwidGlkIjoiMTQzNmQzMzAtZTY2Zi00OTRhLWE4NzUtMDE5YWIwOGYwZmIyIiwidXRpIjoiY0hIYkVQZWJLVTZhR2Z1X1B5TkFBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiMDk5N2ExZDAtMGQxZC00YWNiLWI0MDgtZDVjYTczMTIxZTkwIl0sInhtc19pZHJlbCI6IjcgOCIsInhtc190Y2R0IjoxNDk5MzM4MjAxfQ.UrPsd4EZgIbJn_xHkj43DUCLeS9la-RtWJsWikRQE_vJgnQ-WlL0ZCP27Fj-kAQKiI20AMeOFqgquChcwi0DNG9d9SQG7dHUzQ9cy8Im4O-rVbNlgxcAP-c0XrTSNn3XBNx5axscA51Ws7qJTUyY4Mn5QCJWBj0yB650TnzSkKTxwzBCOuD_8MRAejwNSV8pBsSQKicozXIHv5iseaxv1ZG5kwaxWTh0ryT--NQxcnefyTR7ZIc-r-6rTMv3KhggWRNc6AYqGMzEmtbYylosGf4Xos-Dhd_OtY_d_dh1PwKKVWOTgnlxJWDeDj9--ZIx0hrDvQLx_-ZVg4mIs8HzEA")  # token do Azure com User.ReadWrite.All

# Modelo para lidar com o desafio do Monday
class WebhookPayload(BaseModel):
    challenge: str | None = None
    event: dict | None = None

@app.post("/webhook")
async def webhook(payload: WebhookPayload):
    if payload.challenge:
    return payload.challenge  # <-- ESSA linha resolve o challenge
    # Aqui você processa o evento normalmente depois
    print("Evento recebido:", payload.event)
    return {"ok": True}
    headers = {
        "Authorization": MONDAY_API_KEY,
        "Content-Type": "application/json"
    }

    query = {
        "query": f"""
        query {{
            boards(ids: {board_id}) {{
                items(ids: {pulse_id}) {{
                    name
                    column_values {{
                        id
                        text
                    }}
                }}
            }}
        }}
        """
    }

    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.monday.com/v2", json=query, headers=headers)
        item = res.json()["data"]["boards"][0]["items"][0]
        columns = {col['id']: col['text'] for col in item['column_values']}

    display_name = item['name']
    email = columns["text_mkqp680d"]
    telefone = columns["phone_mkqp5ar5"]
    departamento = columns["dropdown_mkqpnh1h"]
    filial = columns["dropdown_mkqpfaxp"]
    funcao = columns["dropdown_mkqp7hbk"]

    user_data = {
        "accountEnabled": True,
        "displayName": display_name,
        "mailNickname": email.split("@")[0],
        "userPrincipalName": email,
        "passwordProfile": {
            "forceChangePasswordNextSignIn": False,
            "password": "M0nt32025!"
        }
    }

    azure_headers = {
        "Authorization": f"Bearer {AZURE_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://graph.microsoft.com/v1.0/users",
            json=user_data,
            headers=azure_headers
        )

    return {"status": "ok", "microsoft_response": response.json()}
