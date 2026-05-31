from main import app, model
import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def setup_data():
    app_test = TestClient(app)
    return app_test

@pytest.fixture(autouse=True)
def reset_model():
    # Setup
    before_function = model.model

    yield

    #Teardown
    model.model = before_function


def upload_model(api_service) -> None:
    with open('tests/model.pkl', 'rb') as file:
        api_service.post('/upload-model', files={'file': ('model.pkl', file)})


def test_health(setup_data):
    app = setup_data
    response = app.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 200, 'message': 'working'}
    app.close()

def test_upload_model(setup_data):
    app = setup_data
    with open('tests/model.pkl', 'rb') as file:
        response = app.post('/upload-model', files={'file': ('model.pkl', file)})

    assert response.status_code == 200
    assert response.json() == {'status': 200, 'message': 'Model loaded successfully'}

def test_upload_wrong_model(setup_data):
    with open('tests/dataset.csv', 'rb') as file:
        response = setup_data.post('/upload-model', files={'file': ('model.csv', file)})
    assert response.status_code == 415

def test_predict(setup_data):
    upload_model(setup_data)

    to_load = {
              "info": {
                      "person_age": 22,
                      "person_gender": "female",
                      "person_education": "Master",
                      "person_income": 71948,
                      "person_emp_exp": 0,
                      "person_home_ownership": "RENT",
                      "loan_amnt": 35000,
                      "loan_intent": "PERSONAL",
                      "loan_int_rate": 16.02,
                      "loan_percent_income": 0.49,
                      "cb_person_cred_hist_length": 3,
                      "credit_score": 561,
                      "previous_loan_defaults_on_file": "No"
              }
    }

    response = setup_data.post('/predict', json=to_load)
    assert response.status_code == 200
    assert response.json()['loan_status'] > 0.5

def test_predict_no_model(setup_data):
    to_load = {
              "info": {
                      "person_age": 22,
                      "person_gender": "female",
                      "person_education": "Master",
                      "person_income": 71948,
                      "person_emp_exp": 0,
                      "person_home_ownership": "RENT",
                      "loan_amnt": 35000,
                      "loan_intent": "PERSONAL",
                      "loan_int_rate": 16.02,
                      "loan_percent_income": 0.49,
                      "cb_person_cred_hist_length": 3,
                      "credit_score": 561,
                      "previous_loan_defaults_on_file": "No"
              }
    }

    response = setup_data.post('/predict', json=to_load)
    assert response.status_code == 405

def test_predict_csv(setup_data):
    upload_model(setup_data)
    with open('tests/dataset.csv', 'rb') as file:
        response = setup_data.post('/predict-from-csv', files={'file': ('dataset.csv', file)})
    assert float(response.headers['ROC-AUC']) > 0.95

def test_predict_csv_no_model(setup_data):
    with open('tests/dataset.csv', 'rb') as file:
        response = setup_data.post('/predict-from-csv', files={'file': ('dataset.csv', file)})
    assert response.status_code == 405

def test_predict_wrong_csv(setup_data):
    upload_model(setup_data)
    with open('tests/model.pkl', 'rb') as file:
        response = setup_data.post('/predict-from-csv', files={'file': ('dataset.pkl', file)})
    assert response.status_code == 415