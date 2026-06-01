import pandas as pd
import joblib
from sklearn.metrics import roc_auc_score
import io

class ModelController:
    def __init__(self):
        self.model = None

    def load_model(self, file: bytes) -> None:
        # Joblib loads only
        self.model = joblib.load(io.BytesIO(file))

    def predict(self, data: dict) -> tuple[dict, int]:
        if not self.model:
            raise ValueError("ML model is not loaded")

        dataset = pd.DataFrame([data])
        loan_status = self.model.predict_proba(dataset)[:, 1]
        return data, loan_status[0]

    def predict_from_csv(self, data: bytes):
        if not self.model:
            raise ValueError("ML model is not loaded")

        need_roc_auc = False
        original_y = None
        roc_auc = None
        dataset = pd.read_csv(io.BytesIO(data))

        if 'loan_status' in dataset.columns:
            original_y = dataset['loan_status']
            dataset = dataset.drop('loan_status', axis=1)
            need_roc_auc = True

        prepared_data = dataset.to_dict('records')

        predicted_loans = self.model.predict_proba(pd.DataFrame(prepared_data))[:, 1]
        dataset['loan_status'] = [status for status in predicted_loans]

        if need_roc_auc:
            roc_auc = roc_auc_score(original_y, dataset['loan_status'])

        return dataset.to_csv(), roc_auc
