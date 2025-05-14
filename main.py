from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
AZURE_TOKEN = os.getenv("AZURE_TOKEN")  # token do Azure com User.ReadWrite.All

@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    pulse_id = data['event']['pulseId']
    board_id = data['event']['boardId']

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
