# SymptoMap ML Service

This service provides advanced epidemiological modeling (SEIR, etc.) for the SymptoMap platform.

## Prerequisites
*   Python 3.11+
*   Docker (optional, recommended)

## Running Locally
1.  Run the startup script:
    ```bash
    .\run_ml_service.bat
    ```
    This will create a virtual environment, install dependencies, and start the service on port 8000.

2.  Verify it's running:
    Open [http://localhost:8000/docs](http://localhost:8000/docs) to see the API documentation.

## Running with Docker
The service is included in the main `docker-compose.yml`.
```bash
docker-compose up --build
```
