@app.post("/webhook")
async def webhook(payload: WebhookPayload, request: Request):
    if payload.challenge:
        return Response(content=payload.challenge, media_type="text/plain")

    # ↓ esse trecho só é executado em chamadas reais (depois do desafio)
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
