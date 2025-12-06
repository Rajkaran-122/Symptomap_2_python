$demoData = Get-Content -Path "demo-outbreak-data.json" | ConvertFrom-Json

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   SymptoMap - Mumbai Outbreak Simulation & Prediction" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Prepare outbreaks data for ML service
$outbreakLocations = @()
foreach ($hospital in $demoData.hospitals) {
    $outbreakLocations += @{
        lat = $hospital.latitude
        lng = $hospital.longitude
        cases = $hospital.outbreak.case_count
        disease = $hospital.outbreak.disease_type
        severity = $hospital.outbreak.severity_level
    }
}

# Create request body
$requestBody = @{
    outbreaks = $outbreakLocations
    bounds = $demoData.prediction_bounds
} | ConvertTo-Json -Depth 10

Write-Host "🧠 Getting Geographic Spread Prediction for Mumbai...`n" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/predict/spread" -Method Post -ContentType "application/json" -Body $requestBody
    
    Write-Host "✅ ML Service Response:" -ForegroundColor Green
    Write-Host "   High Risk Areas: $($response.high_risk_areas.Count)" -ForegroundColor White
    Write-Host "   Medium Risk Areas: $($response.medium_risk_areas.Count)" -ForegroundColor White
    Write-Host "   Risk Grid Points: $($response.risk_grid.Count)`n" -ForegroundColor White
    
    # Display top 5 high-risk areas
    Write-Host "🔴 TOP 5 HIGH-RISK AREAS FOR DISEASE SPREAD:`n" -ForegroundColor Red
    
    $topAreas = $response.high_risk_areas | Select-Object -First 5
    $i = 1
    foreach ($area in $topAreas) {
        Write-Host "$i. $($area.name)" -ForegroundColor Yellow
        Write-Host "   Location: $([math]::Round($area.lat, 4))°N, $([math]::Round($area.lng, 4))°E" -ForegroundColor White
        Write-Host "   Risk Score: $($area.risk_score)/10" -ForegroundColor Red
        Write-Host "   Spread Probability: $([math]::Round($area.probability * 100, 0))%" -ForegroundColor Red
        Write-Host "   Estimated Cases: $($area.estimated_cases)" -ForegroundColor White
        Write-Host "   Days Until Spread: $($area.days_until_spread) days`n" -ForegroundColor White
        $i++
    }
    
    # Save results
    $response | ConvertTo-Json -Depth 10 | Out-File -FilePath "prediction-results.json"
    Write-Host "💾 Full prediction saved to: prediction-results.json`n" -ForegroundColor Green
    
    # Generate alert summary
    Write-Host "⚠️  ALERT SUMMARY:" -ForegroundColor Yellow
    Write-Host "Current Outbreaks: $($demoData.hospitals.Count) hospitals in Mumbai reporting cases" -ForegroundColor White
    
    $viralFeverCount = ($demoData.hospitals | Where-Object { $_.outbreak.disease_type -eq "Viral Fever" }).Count
    $totalViralFeverCases = ($demoData.hospitals | Where-Object { $_.outbreak.disease_type -eq "Viral Fever" } | ForEach-Object { $_.outbreak.case_count } | Measure-Object -Sum).Sum
    
    Write-Host "Viral Fever: $viralFeverCount hospitals, $totalViralFeverCases total cases" -ForegroundColor Red
    
    if ($response.high_risk_areas.Count -gt 0) {
        $topArea = $response.high_risk_areas[0]
        Write-Host "`n⚠️  URGENT: Highest risk area is $($topArea.name)" -ForegroundColor Red
        Write-Host "   Expected spread in $($topArea.days_until_spread) days with $([math]::Round($topArea.probability * 100, 0))% probability" -ForegroundColor Red
    }
    
    Write-Host "`n✅ Simulation Complete!`n" -ForegroundColor Green
    Write-Host "📍 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Open http://localhost:3000 to see outbreaks on map" -ForegroundColor White
    Write-Host "   2. Check prediction-results.json for detailed analysis" -ForegroundColor White
    Write-Host "   3. High-risk areas should prepare for cases in 2-5 days`n" -ForegroundColor White
    
} catch {
    Write-Host "`n❌ Prediction failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure the ML Service is running on http://localhost:8000`n" -ForegroundColor Yellow
}
