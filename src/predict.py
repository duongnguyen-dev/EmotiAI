import mlflow   

def make_prediction(input, registered_model: str, tracking_uri: str = "http://localhost:5000"):
    logged_model = 'models:/goemotion_MLP/7'
    # Load model as a PyFuncModel.

    mlflow.set_tracking_uri()
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    y_pred = loaded_model.predict(input.numpy().reshape(-1, len(input)))

    return y_pred