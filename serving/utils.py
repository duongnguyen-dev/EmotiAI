import mlflow   

def make_prediction(input, registered_model: str, tracking_uri: str = "http://localhost:5000"):

    mlflow.set_tracking_uri(tracking_uri)
    loaded_model = mlflow.pyfunc.load_model(registered_model)

    y_pred = loaded_model.predict(input.numpy().reshape(-1, len(input)))

    return y_pred