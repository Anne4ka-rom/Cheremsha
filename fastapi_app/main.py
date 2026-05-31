from fastapi import FastAPI, HTTPException, status, File, UploadFile
from fastapi.responses import Response
from models import RequestStatus, PredictRequest, PredictResponse, DatasetResponse
import uvicorn
from ml_utils import ModelController


app = FastAPI()
model = ModelController()


@app.get('/health')
async def health() -> RequestStatus:
    return RequestStatus(status=200, message='working')

@app.post('/upload-model')
async def upload_model(file: UploadFile) -> RequestStatus:
    if not file.filename.endswith('.pkl'):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    file_data = await file.read()

    try:
        model.load_model(file_data)
        return RequestStatus(status=200, message='Model loaded successfully')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

@app.post('/predict')
async def predict(data: PredictRequest) -> PredictResponse:
    if not model:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    try:
        redacted_dataset, loan_status = model.predict(data.info)
        return PredictResponse(info=redacted_dataset, loan_status=loan_status)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

@app.post('/predict-from-csv')
async def predict_from_csv(file: UploadFile) -> Response:
    if not model:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    try:
        file_data = await file.read()
        redacted_dataset, roc_auc = model.predict_from_csv(file_data)

        new_file = Response(content=redacted_dataset, media_type='text/csv',
                            headers={'Content-Disposition': f'attachment; filename=new_{file.filename}',
                                     'ROC-AUC': f'{roc_auc}'})
        return new_file

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


uvicorn.run(app, log_config="log.ini")