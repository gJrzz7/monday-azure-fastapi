from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import os
from msal import ConfidentialClientApplication
from fastapi.responses import Response

app = FastAPI()

# Variáveis de ambiente
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")

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
        return Response(content=payload.challenge, media_type="text/plain")
    return {"ok": True}


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
