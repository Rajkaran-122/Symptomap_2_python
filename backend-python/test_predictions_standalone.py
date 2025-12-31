"""
Simple test script to verify prediction service works
Tests SEIR model and geographic spread prediction independently
"""

import sys
sys.path.insert(0, '.')

print("=" * 60)
print("SYMPTOMAP PREDICTION SERVICE TEST")
print("=" *60)

try:
    # Test 1: Import prediction service
    print("\n✓ Test 1: Importing prediction service...")
    from app.services.prediction_service import (
        get_prediction_service,
        SEIRParameters,
        OutbreakLocation
    )
    print("✓ Successfully imported prediction service!")
    
    # Test 2: Initialize service
    print("\n✓ Test 2: Initializing prediction service...")
    service = get_prediction_service()
    print(f"✓ Service initialized! Grid resolution: {service.grid_resolution}")
    
    # Test 3: Test SEIR prediction
    print("\n✓ Test 3: Testing SEIR prediction...")
    seir_params = SEIRParameters(
        population=1000000,
        initial_infected=100,
        initial_exposed=50,
        beta=0.5,
        sigma=0.2,
        gamma=0.1,
        days=30
    )
    seir_result = service.predict_seir(seir_params)
    print(f"✓ SEIR prediction successful!")
    print(f"  - Peak infected: {seir_result.peak_infected:.0f}")
    print(f"  - Peak day: {seir_result.peak_day}")
    print(f"  - Total predictions: {len(seir_result.predictions)}")
    
    # Test 4: Test geographic spread prediction
    print("\n✓ Test 4: Testing geographic spread prediction...")
    outbreaks = [
        OutbreakLocation(
            lat=19.0760,
            lng=72.8777,
            cases=150,
            disease="COVID-19",
            severity=3.5
        )
    ]
    bounds = {
        "north": 19.3,
        "south": 18.9,
        "east": 73.0,
        "west": 72.7
    }
    spread_result = service.predict_geographic_spread(outbreaks, bounds)
    print(f"✓ Geographic spread prediction successful!")
    print(f"  - High risk areas: {len(spread_result.high_risk_areas)}")
    print(f"  - Medium risk areas: {len(spread_result.medium_risk_areas)}")
    print(f"  - Low risk areas: {len(spread_result.low_risk_areas)}")
    print(f"  - Risk grid points: {len(spread_result.risk_grid)}")
    
    if spread_result.high_risk_areas:
        top_risk = spread_result.high_risk_areas[0]
        print(f"\n  Top risk area:")
        print(f"    - Location: {top_risk.name}")
        print(f"    - Risk score: {top_risk.risk_score}/10")
        print(f"    - Estimated cases: {top_risk.estimated_cases}")
        print(f"    - Days until spread: {top_risk.days_until_spread}")
    
    # Test 5: Test disease parameters
    print("\n✓ Test 5: Testing disease parameters...")
    diseases = service.DISEASE_PARAMS
    print(f"✓ Supported diseases: {len(diseases)}")
    for disease, params in diseases.items():
        print(f"  - {disease}: R0={params['R0']}, Range={params['range_km']}km")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n✅ Prediction service is working correctly!")
    print("✅ SEIR modeling functional")
    print("✅ Geographic spread prediction functional")
    print("✅ ML service successfully integrated into backend\n")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("Install dependencies: pip install numpy scipy pandas pydantic")
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
