from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import os
from msal import ConfidentialClientApplication

app = FastAPI()

# Variáveis de ambiente
TENANT_ID = os.getenv("1436d330-e66f-494a-a875-019ab08f0fb2")
CLIENT_ID = os.getenv("ff6a39d1-f4ac-4cb5-9a7e-2a56075600b0")
CLIENT_SECRET = os.getenv("0kB8Q~Lz1HFSeVXYzjdyDIg8p3ibDottxb9GcbJC")
MONDAY_API_KEY = os.getenv("eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUwOTA5Njc2NSwiYWFpIjoxMSwidWlkIjo3NTczODMwOSwiaWFkIjoiMjAyNS0wNS0wNlQxNjozNzowOS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6Mjk0MDA0ODQsInJnbiI6InVzZTEifQ.BvAgqehIqjQEjwBdm4EV6nSPeT89ta2kVK06BzkUTHk")

# Modelo do payload
class WebhookPayload(BaseModel):
    challenge: str | None = None
    event: dict | None = None

def get_azure_token():
    app = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}"
    )
    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return token["access_token"]

@app.get("/")
def root():
    return {"message": "FastAPI rodando com sucesso"}

@app.post("/webhook")
async def webhook(payload: WebhookPayload, request: Request):
    if payload.challenge:
        return payload.challenge

    data = await request.json()
    pulse_id = data['event']['pulseId']
    board_id = data['event']['boardId']

    headers = {
        "Authorization": MONDAY_API_KEY,
        "Content-Type": "application/json"
    }

    query = {
        "query": f'''
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
        '''
    }

    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.monday.com/v2", json=query, headers=headers)
        item = res.json()["data"]["boards"][0]["items"][0]
        columns = {col['id']: col['text'] for col in item['column_values']}

    display_name = item['name']
    email = columns["text_mkqp680d"]

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

    access_token = get_azure_token()
    azure_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://graph.microsoft.com/v1.0/users",
            json=user_data,
            headers=azure_headers
        )

    return {"status": "ok", "response": response.json()}
