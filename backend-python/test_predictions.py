"""Test AI Prediction System"""
import requests
import json

API_URL = "http://localhost:8000/api/v1"

print("\n🧪 TESTING AI PREDICTION SYSTEM\n")
print("="*80)

# Test 1: Get 30-day forecast
print("\n1️⃣ Testing 30-Day Forecast (Most Likely Scenario)...")
try:
    resp = requests.get(f"{API_URL}/predictions/forecast?days=30&scenario=likely", timeout=15)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ SUCCESS!")
        print(f"\n   📊 Prediction Summary:")
        print(f"   - Current Active Cases: {data['summary']['current_active_cases']}")
        print(f"   - Peak Cases: {data['summary']['peak_cases']}")
        print(f"   - Peak Date: {data['summary']['peak_date']}")
        print(f"   - R₀ (Reproduction Number): {data['summary']['reproduction_number']}")
        print(f"   - Risk Level: {data['summary']['risk_assessment']['level']}")
        print(f"   - Forecast Points: {len(data['time_series'])}")
        print(f"   - Geographic Predictions: {len(data['geographic_predictions'])}")
        print(f"   - Recommendations: {len(data['recommendations'])}")
    else:
        print(f"   ❌ FAILED: {resp.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 2: Scenario Comparison
print("\n2️⃣ Testing Scenario Comparison...")
try:
    resp = requests.get(f"{API_URL}/predictions/scenarios?days=30", timeout=15)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ SUCCESS!")
        print(f"\n   📈 Scenario Comparison:")
        if 'best' in data['scenarios']:
            print(f"   Best Case - Peak: {data['scenarios']['best']['peak_cases']} | R₀: {data['scenarios']['best']['reproduction_number']}")
        if 'likely' in data['scenarios']:
            print(f"   Likely   - Peak: {data['scenarios']['likely']['peak_cases']} | R₀: {data['scenarios']['likely']['reproduction_number']}")
        if 'worst' in data['scenarios']:
            print(f"   Worst Case - Peak: {data['scenarios']['worst']['peak_cases']} | R₀: {data['scenarios']['worst']['reproduction_number']}")
    else:
        print(f"   ❌ FAILED")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 3: Different time periods
print("\n3️⃣ Testing Different Forecast Periods...")
for days in [7, 14, 60]:
    try:
        resp = requests.get(f"{API_URL}/predictions/forecast?days={days}&scenario=likely", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ {days}-day forecast: {len(data['time_series'])} data points")
        else:
            print(f"   ❌ {days}-day forecast failed")
    except Exception as e:
        print(f"   ❌ {days}-day forecast error: {e}")

print("\n" + "="*80)
print("✨ AI PREDICTION SYSTEM TEST COMPLETE!")
print("="*80)
print("\n📍 Access Prediction Dashboard at: http://localhost:3000/predictions")
print("\n🎯 Features:")
print("   - SEIR Epidemiological Model")
print("   - Time Series Forecasting")
print("   - Geographic Spread Predictions")
print("   - Hospital Capacity Planning")
print("   - Risk Assessment")
print("   - Multi-Scenario Analysis")
print("   - Interactive Charts & Visualizations")
print("   - AI-Generated Recommendations\n")
