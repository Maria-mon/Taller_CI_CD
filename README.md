# Taller CI/CD 
Integrantes: 

* Andres Gomez
* Juan Felipe Forero
* Maria del Mar Montenegro

Este proyecto implementa una arquitectura completa de CI/CD usando GitOps para desplegar una API en Kubernetes con FastAPI, Docker, Prometheus, Grafana y Argo CD. El pipeline de CI/CD entrena automáticamente un modelo de Machine Learning y realiza despliegues controlados vía manifiestos YAML sincronizados con Argo CD.

Repositorio GitHub: [https://github.com/Maria-mon/Taller_CI_CD](https://github.com/Maria-mon/Taller_CI_CD)

## Estructura del Proyecto

Taller_CI_CD/
├── .github/workflows/ci-cd.yml # Pipeline CI/CD en GitHub Actions
├── api/ # API FastAPI + entrenamiento modelo
│ ├── Dockerfile # Imagen Docker de la API
│ ├── requirements.txt
│ ├── train_model.py # Entrenamiento automático
│ └── app/
│ ├── main.py # Endpoint /predict y /metrics
│ └── model.pkl # Modelo generado y cargado automáticamente
├── loadtester/ # Generador de carga para la API
│ ├── Dockerfile
│ ├── requirements.txt
│ └── main.py
├── manifests/ # Manifiestos YAML para K8s
│ ├── api-deployment.yaml # Despliegue de API
│ ├── script-deployment.yaml # Despliegue de LoadTester
│ ├── prometheus-deployment.yaml # Prometheus + ConfigMap
│ ├── grafana-deployment.yaml # Grafana + ConfigMap
│ ├── prometheus.yml
│ └── kustomization.yaml
└── argo-cd/
└── app.yaml # Declaración GitOps para Argo CD

##  Dockerfiles funcionales

- `api/Dockerfile`: construye una imagen ligera basada en `python:3.10-slim`, instala dependencias y lanza `uvicorn`.
- `loadtester/Dockerfile`: genera carga con peticiones aleatorias al endpoint `/predict` cada segundo.

Ambas imágenes son publicadas en DockerHub automáticamente desde el pipeline.

![dockerhub](https://github.com/user-attachments/assets/37f726a7-5eeb-4a7c-8301-10330228c14f)


##  Entrenamiento Automatizado en CI/CD

El archivo `train_model.py`:

- Preprocesa el dataset `penguins_size.csv`
- Entrena un modelo `LogisticRegression`
- Guarda el modelo como `model.pkl` en `api/app/`

Este script se ejecuta automáticamente en GitHub Actions durante cada push a `main`, y el artefacto `model.pkl` se incluye en la imagen Docker de la API.

## Instrumentación con Prometheus

- El endpoint `/metrics` de FastAPI expone métricas en formato Prometheus (usando `prometheus_client`).
- El manifiesto `prometheus-deployment.yaml` despliega Prometheus en el clúster y lo configura para hacer scraping del endpoint de la API.
- Las métricas capturadas incluyen:
  - Latencias de inferencia
  - Número de peticiones

![Screenshot from 2025-05-18 16-58-44](https://github.com/user-attachments/assets/02458587-4498-420d-8025-5fb2dcd476c0)


## Visualización en Grafana

- Grafana se despliega con `grafana-deployment.yaml` y se configura con un `ConfigMap`.
- La fuente de datos es Prometheus.
- Se habilita un dashboard para visualizar:
  - Número total de requests
  - Latencias promedio por segundo


Acceso vía `kubectl port-forward` a `grafana-service`.

![Screenshot from 2025-05-18 16-59-04](https://github.com/user-attachments/assets/67756caf-078d-4b96-bf65-dd7fd0a31a79)


## GitOps con GitHub Actions + Argo CD

El flujo completo incluye:

1. **Entrenamiento** del modelo con `train_model.py`
2. **Construcción y publicación** de imágenes Docker para `api` y `loadtester`
3. **Actualización automática** del manifiesto `api-deployment.yaml` con el nuevo tag (`github.sha`)
4. **Commit y push del manifiesto** de forma automática desde el workflow
5. **Argo CD detecta los cambios** y sincroniza el clúster con el estado del repositorio

Todo el despliegue es **declarativo y rastreable**, alineado con buenas prácticas GitOps.

## Como desplegar y probar

1. Clonar el repositorio: git clone https://github.com/Maria-mon/Taller_CI_CD.git
2. Entrenar el modelo y construir imágenes automáticamente
   Cada vez que haces git push al branch main:
    Se ejecuta el pipeline de GitHub Actions (.github/workflows/ci-cd.yml)
    Se entrena el modelo (train_model.py)
    Se genera model.pkl
    Se construyen las imágenes api y loadtester
    Se suben a DockerHub con un tag único (:github.sha)
    El manifiesto api-deployment.yaml se actualiza automáticamente
    El pipeline hace git push con el manifiesto actualizado
3. Desplegar en Kubernetes con Argo CD:
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   kubectl apply -f argo-cd/app.yaml
4.  Ver servicios desplegados: kubectl get pods
5.  Acceder a los servicios:
   kubectl port-forward svc/api-service 8000:8000
   kubectl port-forward svc/prometheus-service 9090:9090
   kubectl port-forward svc/grafana-service 3000:3000
Accede en navegador a: http://localhost:<reemplazar puerto>
6. Visualizar métricas en Prometheus o Grafana
Prometheus muestra las métricas /metrics expuestas por FastAPI.
Ejemplos de queries:
http_requests_total
request_latency_seconds_count
request_latency_seconds_bucket

7. En Grafana crear paneles personalizados usando Prometheus como datasource.
