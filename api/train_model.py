import pandas as pd
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import os

# Leer el CSV original
df = pd.read_csv("penguins_size.csv")

df = df[['culmen_length_mm', 'culmen_depth_mm', 'flipper_length_mm', 'body_mass_g', 'sex']].dropna()

# Mostrar tamaño antes de filtrar
print(f"Registros antes de filtrar sex: {len(df)}")

# Renombrar columnas
df.rename(columns={
    'culmen_length_mm': 'bill_length_mm',
    'culmen_depth_mm': 'bill_depth_mm'
}, inplace=True)

# Filtrar valores válidos de 'sex'
df = df[df['sex'].str.strip().str.lower().isin(['male', 'female'])]
df['sex'] = df['sex'].str.strip().str.capitalize().map({'Male': 1, 'Female': 0})

print(f"Registros válidos después de limpieza: {len(df)}")

# Separar variables y objetivo
X = df[['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']]
y = df['sex']

# Dividir datos
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Entrenar modelo
model = LogisticRegression(random_state=42, max_iter=500, C=1)
model.fit(X_train, y_train)

# Evaluar
print("Validation Accuracy:", accuracy_score(y_val, model.predict(X_val)))
print("Test Accuracy:", accuracy_score(y_test, model.predict(X_test)))

# Guardar modelo directamente en app/
os.makedirs("app", exist_ok=True)
with open("app/model.pkl", "wb") as f:
    pickle.dump(model, f)
print("Modelo guardado en app/model.pkl")
