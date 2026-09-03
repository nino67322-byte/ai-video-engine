from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Video Engine")


class GenerateRequest(BaseModel):
    prompt: str
    image_url: str | None = None


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-video-engine",
        "model": "not-loaded"
    }


@app.post("/generate")
def generate(request: GenerateRequest):
    return {
        "status": "received",
        "message": "Pedido recebido pelo servidor de IA.",
        "prompt": request.prompt,
        "image_received": request.image_url is not None
    } 