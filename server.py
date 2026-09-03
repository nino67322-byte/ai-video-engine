import os
import uuid
import urllib.request
import urllib.error

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="AI Video Engine")


# Endereço do servidor que realmente executará o modelo open-source.
# Por enquanto ficará vazio.
AI_WORKER_URL = os.getenv("AI_WORKER_URL", "")


class GenerateRequest(BaseModel):
    prompt: str
    image_url: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-video-engine",
        "model": "open-source",
        "worker_connected": bool(AI_WORKER_URL)
    }


@app.post("/generate")
def generate(request: GenerateRequest):

    if not request.prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="O prompt não pode estar vazio."
        )

    if not request.image_url.strip():
        raise HTTPException(
            status_code=400,
            detail="A imagem é obrigatória."
        )

    job_id = str(uuid.uuid4())

    # Ainda não existe um servidor GPU conectado.
    # Quando conectarmos o Wan2.2, esta parte enviará
    # a imagem e o prompt para ele.
    if not AI_WORKER_URL:
        return {
            "status": "waiting_for_worker",
            "job_id": job_id,
            "message": "Pedido recebido. Servidor de IA ainda não conectado.",
            "prompt": request.prompt,
            "image_url": request.image_url
        }

    data = (
        '{"job_id":"' + job_id +
        '","prompt":"' + request.prompt.replace('"', '\\"') +
        '","image_url":"' + request.image_url.replace('"', '\\"') +
        '"}'
    ).encode("utf-8")

    req = urllib.request.Request(
        AI_WORKER_URL + "/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = response.read().decode("utf-8")

        return {
            "status": "sent_to_ai",
            "job_id": job_id,
            "worker_response": result
        }

    except urllib.error.URLError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Não foi possível conectar ao servidor de IA: {error}"
        )