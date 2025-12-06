@echo off
echo ===============================================================
echo    SymptoMap - Mumbai Outbreak Demonstration
echo===============================================================
echo.
echo Testing ML Service with realistic Mumbai hospital outbreak data...
echo.
echo 📊 Outbreak Data:
echo    - 10 Hospitals across Mumbai
echo    - 478 Total Cases (Viral Fever, Dengue, COVID-19, Influenza)  
echo    - Geographic spread across North to South Mumbai
echo.
echo Running prediction...
echo.

curl -X POST http://localhost:8000/predict/spread ^
  -H "Content-Type: application/json" ^
  -d "{\"outbreaks\": [{\"lat\": 19.0596, \"lng\": 72.8295, \"cases\": 67, \"disease\": \"Viral Fever\", \"severity\": 4}, {\"lat\": 19.0330, \"lng\": 72.8397, \"cases\": 52, \"disease\": \"Viral Fever\", \"severity\": 3}, {\"lat\": 18.9894, \"lng\": 72.8439, \"cases\": 89, \"disease\": \"Viral Fever\", \"severity\": 4}, {\"lat\": 18.9968, \"lng\": 72.8390, \"cases\": 34, \"disease\": \"Dengue\", \"severity\": 3}, {\"lat\": 18.9670, \"lng\": 72.8040, \"cases\": 41, \"disease\": \"Influenza\", \"severity\": 2}, {\"lat\": 19.1334, \"lng\": 72.8267, \"cases\": 45, \"disease\": \"Viral Fever\", \"severity\": 3}, {\"lat\": 19.1076, \"lng\": 72.8405, \"cases\": 58, \"disease\": \"Viral Fever\", \"severity\": 3}, {\"lat\": 19.1722, \"lng\": 72.9563, \"cases\": 23, \"disease\": \"COVID-19\", \"severity\": 2}, {\"lat\": 19.2812, \"lng\": 72.8579, \"cases\": 31, \"disease\": \"Viral Fever\", \"severity\": 2}, {\"lat\": 19.0330, \"lng\": 73.0297, \"cases\": 38, \"disease\": \"Viral Fever\", \"severity\": 3}], \"bounds\": {\"north\": 19.35, \"south\": 18.85, \"east\": 73.10, \"west\": 72.75}}" ^
  > prediction-results.txt

echo.
echo ✅ Prediction complete! Results saved to prediction-results.txt
echo.
echo 📍 Next Steps:
echo    1. Open prediction-results.txt to see detailed risk analysis
echo    2. Visit http://localhost:3000 to visualize on map
echo    3. High-risk areas identified for disease spread
echo.
pause
