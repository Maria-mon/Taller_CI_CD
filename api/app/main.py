from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
import pickle
import numpy as np
import os

# Inicializar FastAPI
app = FastAPI()

# Definir el esquema de entrada
class PenguinData(BaseModel):
    bill_length_mm: float
    bill_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float

# Cargar el modelo
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    model = None
    print(f"Error al cargar el modelo: {e}")

# Métricas Prometheus
PREDICTION_COUNTER = Counter("prediction_requests_total", "Número total de predicciones")
PREDICTION_LATENCY = Histogram("prediction_latency_seconds", "Duración de las predicciones")

@app.post("/predict")
@PREDICTION_LATENCY.time()
def predict(data: PenguinData):
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo no disponible")

    input_array = np.array([[data.bill_length_mm, data.bill_depth_mm, data.flipper_length_mm, data.body_mass_g]])
    prediction = model.predict(input_array)[0]
    PREDICTION_COUNTER.inc()
    predicted_label = "Male" if prediction == 1 else "Female"
    return {"prediction": predicted_label}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

