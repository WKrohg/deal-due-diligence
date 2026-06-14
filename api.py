import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pipeline import ScreeningPipeline
from models import ScreeningReport

app = FastAPI(title="Deal Screening API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
pipeline = ScreeningPipeline()


class ScreenRequest(BaseModel):
    listing_text: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/screen", response_model=ScreeningReport)
def screen(req: ScreenRequest):
    if not req.listing_text.strip():
        raise HTTPException(status_code=400, detail="listing_text is required")
    return pipeline.run(req.listing_text)
