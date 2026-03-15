import sys
import os

# Add mood_engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../mood_engine"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from playlist_formatter import build_response

app = FastAPI(title="Mood Music API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")


class TranscriptRequest(BaseModel):
    transcript: str


@app.get("/")
def index():
    return FileResponse(os.path.join(frontend_path, "index.html"))


@app.post("/analyze")
def analyze(req: TranscriptRequest):
    """
    Takes a voice transcript, returns a 3-phase mood playlist.
    """
    result = build_response(req.transcript)
    return result


@app.get("/health")
def health():
    return {"status": "ok"}
