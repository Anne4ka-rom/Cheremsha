from pydantic import BaseModel, Field
from typing import Optional


class RequestStatus(BaseModel):
    status: int
    message: str

class PredictRequest(BaseModel):
    info: dict

class PredictResponse(BaseModel):
    info: dict
    loan_status: int | float

class DatasetResponse(BaseModel):
    dataset: bytes
    roc_auc: Optional[float] = Field(default=None)