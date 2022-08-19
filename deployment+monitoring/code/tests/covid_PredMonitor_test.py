# from pathlib import Path
import numpy as np

import covid_PredMonitor


def test_rmse():
    x = np.random.randint(1,101,5)
    y = np.random.randint(1,101,5)
    actual_result = covid_PredMonitor.rmse(x, y)
    
    summation = 0  #variable to store the summation of differences
    n = len(y) #finding total number of items in list
    for i in range (0,n):  #looping through each element of the list
        difference = y[i] - x[i]  #finding the difference between observed and predicted value
        squared_difference = difference**2  #taking square of the differene 
        summation = summation + squared_difference  #taking a sum of all the differences
    MSE = summation/n 
    expected_result = np.sqrt(MSE)
    
    assert actual_result == expected_result
    # assert 1 == 1 #NOTE: dummy test







# def read_text(file):
#     test_directory = Path(__file__).parent

#     with open(test_directory / file, 'rt', encoding='utf-8') as f_in:
#         return f_in.read().strip()


# def test_base64_decode():
#     base64_input = read_text('data.b64')

#     actual_result = model.base64_decode(base64_input)
#     expected_result = {
#         "ride": {
#             "PULocationID": 130,
#             "DOLocationID": 205,
#             "trip_distance": 3.66,
#         },
#         "ride_id": 256,
#     }

#     assert actual_result == expected_result
#     # assert 1 == 1 #NOTE: dummy test


# def test_prepare_features():
#     model_service = model.ModelService(None)

#     ride = {
#         "PULocationID": 130,
#         "DOLocationID": 205,
#         "trip_distance": 3.66,
#     }

#     actual_features = model_service.prepare_features(ride)

#     expected_fetures = {
#         "PU_DO": "130_205",
#         "trip_distance": 3.66,
#     }

#     assert actual_features == expected_fetures
#     # assert 1 == 1 #NOTE: dummy test


# class ModelMock:
#     def __init__(self, value):
#         self.value = value

#     def predict(self, X):
#         n = len(X)
#         return [self.value] * n


# def test_predict():
#     model_mock = ModelMock(10.0)
#     model_service = model.ModelService(model_mock)

#     features = {
#         "PU_DO": "130_205",
#         "trip_distance": 3.66,
#     }

#     actual_prediction = model_service.predict(features)
#     expected_prediction = 10.0

#     assert actual_prediction == expected_prediction
#     # assert 1 == 1 #NOTE: dummy test


# def test_lambda_handler():
#     model_mock = ModelMock(10.0)
#     model_version = 'Test123'
#     model_service = model.ModelService(model_mock, model_version)

#     base64_input = read_text('data.b64')

#     event = {
#         "Records": [
#             {
#                 "kinesis": {
#                     "data": base64_input,
#                 },
#             }
#         ]
#     }

#     actual_predictions = model_service.lambda_handler(event)
#     expected_predictions = {
#         'predictions': [
#             {
#                 'model': 'ride_duration_prediction_model',
#                 'version': model_version,
#                 'prediction': {
#                     'ride_duration': 10.0,
#                     'ride_id': 256,
#                 },
#             }
#         ]
#     }

#     assert actual_predictions == expected_predictions
    # assert 1 == 1 #NOTE: dummy test
