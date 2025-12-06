# SymptoMap ML Service Implementation Walkthrough

## Overview
I have successfully initialized the **Phase 2** of the Predictions Module roadmap by creating a dedicated Python ML Service and integrating it with the existing Node.js backend.

## Changes Implemented

### 1. New Python ML Service (`/ml-service`)
*   **Framework**: FastAPI (High performance, easy to use).
*   **Model**: Implemented a mechanistic **SEIR (Susceptible-Exposed-Infectious-Recovered)** model using `scipy.integrate.odeint`.
*   **Endpoints**:
    *   `GET /`: Service status.
    *   `GET /health`: Health check.
    *   `POST /predict/seir`: Runs the SEIR simulation and returns predictions.
*   **Docker**: Created a `Dockerfile` for containerization.

### 2. Backend Integration (`/backend`)
*   **Adapter Pattern**: Created `src/services/mlServiceAdapter.ts` to handle communication with the Python service.
*   **Prediction Service Update**: Modified `src/services/predictionService.ts` to:
    *   Check `diseaseType`. If it is `COVID-19` or `SEIR_TEST`, it routes the request to the new ML Service.
    *   Fallback to the legacy Linear Regression model if the ML Service fails.
    *   Convert the SEIR output into the standard `MLPrediction` format.

### 3. Infrastructure (`docker-compose.yml`)
*   Added `ml-service` to the composition.
*   Configured networking so `backend` can talk to `ml-service` at `http://ml-service:8000`.

## How to Test

### 1. Start the Stack
```bash
docker-compose up --build
```

### 2. Verify ML Service
You can curl the ML service directly (if port 8000 is exposed):
```bash
curl http://localhost:8000/
# Output: {"status": "online", "service": "SymptoMap ML Service"}
```

### 3. Test Prediction API
Make a POST request to the backend to trigger the SEIR model:

**Endpoint**: `POST http://localhost:8787/api/predictions` (or wherever the route is exposed)
**Body**:
```json
{
  "region": { "north": 40, "south": 30, "east": -70, "west": -80 },
  "horizonDays": 30,
  "diseaseType": "SEIR_TEST"
}
```

**Expected Response**:
You should see a prediction object with `modelVersion: "SEIR-1.0.0"` and a curve that follows epidemiological dynamics (peak and decline) rather than a straight line.

## Next Steps
*   **Parameter Fitting**: Currently, the SEIR parameters (beta, gamma) are hardcoded defaults. The next step is to implement an endpoint that fits these parameters to the historical data provided in the request.
*   **More Models**: Add LSTM or Prophet models to the Python service.
