import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import httpx

app = FastAPI()

TARGET_HOST = os.environ.get('TARGET_HOST')
headers = {'connection': 'keep-alive', 'cache-control': 'max-age=0', 'upgrade-insecure-requests': '1', 
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0', 
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'}

@app.get("/{path:path}")
async def proxy(request: Request, path: str):
    url = f"https://{TARGET_HOST}/{path}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers = headers, params=request.query_params)
    return HTMLResponse(content=response.text, status_code=response.status_code)
