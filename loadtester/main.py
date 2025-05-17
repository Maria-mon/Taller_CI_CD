# loadtester/main.py
import requests
import time
import random

API_URL = "http://api-service:8000/predict"  # nombre del servicio en Kubernetes

def generate_random_input():
    return {
        "bill_length_mm": round(random.uniform(30, 60), 1),
        "bill_depth_mm": round(random.uniform(13, 21), 1),
        "flipper_length_mm": random.randint(170, 230),
        "body_mass_g": random.randint(2700, 6300)
    }

while True:
    try:
        payload = generate_random_input()
        response = requests.post(API_URL, json=payload)
        print("🔁 Sent:", payload, "✅ Response:", response.json())
    except Exception as e:
        print("❌ Error:", e)
    time.sleep(1)
