import logging
from contextlib import asynccontextmanager
from typing import Literal
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
import joblib
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fraud_inference_api")

# In-memory storage for ML artifacts
model_artifacts = {}


# Lifespan context manager for artifact loading and overall app info
@asynccontextmanager
async def lifespan(app: FastAPI):

   
    try:
        model_artifacts["pipeline"] = joblib.load( "artifacts/fraud_detection_pipeline.joblib")
        metadata = joblib.load("artifacts/model_metadata.joblib")
        model_artifacts["threshold"] = metadata.get("optimal_threshold", 0.5)
        model_artifacts["version"] = metadata.get("model_version", "1.0.0")
        logger.info(f"Pipeline loaded successfully. Threshold: {model_artifacts['threshold']:.4f}")
    except Exception as e:
        logger.error(f"Failed to load artifacts from 'artifacts/' folder: {e}")
        raise RuntimeError("Initialization error: Saved pipeline artifacts missing.") from e
    yield
    model_artifacts.clear()


app = FastAPI(
    title="PaySim Pure Inference Microservice",
    description="FastAPI endpoint receiving pre-engineered feature vectors from Streamlit.",
    version="1.0.0",
    lifespan=lifespan,
)


# Payload schema matching exact Streamlit keys and types
class EngineeredFeaturePayload(BaseModel):
    type: Literal["TRANSFER", "CASH_OUT"] = Field(..., description="Transaction channel")
    amount: float = Field(..., gt=0.0)
    oldbalanceOrg: float = Field(..., ge=0.0)
    newbalanceOrig: float = Field(..., ge=0.0)
    oldbalanceDest: float = Field(..., ge=0.0)
    newbalanceDest: float = Field(..., ge=0.0)
    errorBalanceOrig: float
    errorBalanceDest: float
    is_orig_zero: int = Field(..., ge=0, le=1)
    ratio_orig_amount: float
    ratio_Dest_amount: float
    hour_of_day: int = Field(..., ge=0, le=23)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "TRANSFER",
                "amount": 181.0,
                "oldbalanceOrg": 181.0,
                "newbalanceOrig": 0.0,
                "oldbalanceDest": 0.0,
                "newbalanceDest": 0.0,
                "errorBalanceOrig": 0.0,
                "errorBalanceDest": 181.0,
                "is_orig_zero": 1,
                "ratio_orig_amount": 0.9999,
                "ratio_Dest_amount": 181000.0,
                "hour_of_day": 1
            }
        }
    )


class PredictionResponse(BaseModel):
    is_fraud: bool
    risk_score: float
    decision_threshold: float
    model_version: str


@app.get("/health",status_code=status.HTTP_200_OK)
def health_check():
    if "pipeline" not in model_artifacts:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not initalised"
        )
    else:
        return {
            "status": "healthy",
            "model_version": model_artifacts["version"],
            "threshold": model_artifacts["threshold"]
        }


@app.get("/")
def read_root():
    return {
        "service": "PaySim Fraud Inference API",
        "status": "online",
        "docs": "/docs",
        "health": "/health"
    }


@app.post("/predict",status_code=status.HTTP_200_OK,response_model=PredictionResponse)
def predict_fraud(payload:EngineeredFeaturePayload):
    if "pipeline" not in model_artifacts:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model artifact uninitialized."
        )

    try:
        #pydantic to dataframe
        input_df=pd.DataFrame([payload.model_dump()])

        #run the pipelines via sckit learn
        pipeline = model_artifacts["pipeline"]
        risk_score = float(pipeline.predict_proba(input_df)[0, 1])

        threshold = model_artifacts["threshold"]
        is_fraud = bool(risk_score >= threshold)

        return PredictionResponse(
            is_fraud=is_fraud,
            risk_score=round(risk_score, 4),
            decision_threshold=round(threshold, 4),
            model_version=model_artifacts["version"]
        )

    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference execution failure."
        ) from e