$demoData = Get-Content -Path "demo-outbreak-data.json" | ConvertFrom-Json

Write-Host "`n=== SUBMITTING OUTBREAK DATA TO BACKEND ===`n" -ForegroundColor Cyan

$successCount = 0
$failCount = 0

foreach ($hospital in $demoData.hospitals) {
    try {
        $body = $hospital.outbreak | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "http://localhost:8787/api/v1/outbreaks" -Method Post -ContentType "application/json" -Body $body
        Write-Host "✅ $($hospital.name): $($hospital.outbreak.case_count) $($hospital.outbreak.disease_type) cases" -ForegroundColor Green
        $successCount++
        Start-Sleep -Milliseconds 200
    } catch {
        Write-Host "❌ $($hospital.name): Failed - $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
}

Write-Host "`n📊 Results: $successCount submitted, $failCount failed" -ForegroundColor Yellow
Write-Host "`n✅ Outbreak data is now in the system!" -ForegroundColor Green
Write-Host "📍 Refresh http://localhost:3000 to see markers on the map`n" -ForegroundColor Cyan
