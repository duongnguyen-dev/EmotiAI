import numpy as np
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from services.mlp_service import MultiLayerPerceptronService
from src.models.mlp.config import MLPConfig

model = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    model["mlp"] = MultiLayerPerceptronService('mlp', MLPConfig.SEQUENCE_LENGTH, MLPConfig.OUTPUT_MODE)
    yield
    model.clear()

app = FastAPI(lifespan=lifespan)

@app.post("/mlp", response_model=dict)
async def MLP(prompt: str):
    try:
        result = np.argmax(model["mlp"].predict(prompt), axis=0)

        classnames = [
            "admiration",
            "amusement",
            "anger",
            "annoyance",
            "approval",
            "caring",
            "confusion",
            "curiosity",
            "desire",
            "disappointment",
            "disapproval",
            "disgust",
            "embarrassment",
            "excitement",
            "fear",
            "gratitude",
            "grief",
            "joy",
            "love",
            "nervousness",
            "optimism",
            "pride",
            "realization",
            "relief",
            "remorse",
            "sadness",
            "surprise",
            "neutral"
        ]

        return {"prediction": classnames[result]}
    except Exception as error:
        raise HTTPException(status_code=500, detail="Failed to classify input prompt.")