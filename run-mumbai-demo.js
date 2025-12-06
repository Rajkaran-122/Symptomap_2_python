const fs = require('fs');
const axios = require('axios');

const BACKEND_URL = 'http://localhost:8787/api/v1';
const ML_SERVICE_URL = 'http://localhost:8000';

// Read the demo data
const demoData = JSON.parse(fs.readFileSync('demo-outbreak-data.json', 'utf8'));

async function submitOutbreaks() {
    console.log('📊 Submitting Mumbai Hospital Outbreak Data...\n');

    let successCount = 0;
    let failCount = 0;

    for (const hospital of demoData.hospitals) {
        try {
            const response = await axios.post(`${BACKEND_URL}/outbreaks`, hospital.outbreak);
            console.log(`✅ ${hospital.name}: ${hospital.outbreak.case_count} ${hospital.outbreak.disease_type} cases reported`);
            successCount++;
        } catch (error) {
            console.error(`❌ ${hospital.name}: Failed - ${error.message}`);
            failCount++;
        }

        // Small delay to avoid overwhelming the server
        await new Promise(resolve => setTimeout(resolve, 200));
    }

    console.log(`\n📈 Summary: ${successCount} submitted, ${failCount} failed\n`);
}

async function getSpreadPrediction() {
    console.log('🧠 Getting Geographic Spread Prediction for Mumbai...\n');

    try {
        // First, let's test the ML service directly
        console.log('Testing ML Service directly...');

        const outbreakLocations = demoData.hospitals.map(h => ({
            lat: h.latitude,
            lng: h.longitude,
            cases: h.outbreak.case_count,
            disease: h.outbreak.disease_type,
            severity: h.outbreak.severity_level
        }));

        const mlResponse = await axios.post(`${ML_SERVICE_URL}/predict/spread`, {
            outbreaks: outbreakLocations,
            bounds: demoData.prediction_bounds
        });

        console.log('✅ ML Service Response:');
        console.log(`   High Risk Areas: ${mlResponse.data.high_risk_areas.length}`);
        console.log(`   Medium Risk Areas: ${mlResponse.data.medium_risk_areas.length}`);
        console.log(`   Risk Grid Points: ${mlResponse.data.risk_grid.length}\n`);

        // Display top 5 high-risk areas
        console.log('🔴 TOP 5 HIGH-RISK AREAS FOR SPREAD:\n');
        mlResponse.data.high_risk_areas.slice(0, 5).forEach((area, i) => {
            console.log(`${i + 1}. ${area.name}`);
            console.log(`   Location: ${area.lat}°N, ${area.lng}°E`);
            console.log(`   Risk Score: ${area.risk_score}/10`);
            console.log(`   Spread Probability: ${(area.probability * 100).toFixed(0)}%`);
            console.log(`   Estimated Cases: ${area.estimated_cases}`);
            console.log(`   Days Until Spread: ${area.days_until_spread} days\n`);
        });

        // Save prediction results
        fs.writeFileSync('prediction-results.json', JSON.stringify(mlResponse.data, null, 2));
        console.log('💾 Full prediction saved to: prediction-results.json\n');

    } catch (error) {
        console.error('❌ Prediction failed:', error.response?.data || error.message);
    }
}

async function main() {
    console.log('═══════════════════════════════════════════════════════');
    console.log('   SymptoMap - Mumbai Outbreak Simulation & Prediction');
    console.log('═══════════════════════════════════════════════════════\n');

    // Step 1: Submit outbreak data
    await submitOutbreaks();

    // Step 2: Get spread prediction
    await getSpreadPrediction();

    console.log('✅ Simulation Complete!\n');
    console.log('📍 Next Steps:');
    console.log('   1. Open http://localhost:3000 to see outbreaks on map');
    console.log('   2. Check prediction-results.json for detailed analysis');
    console.log('   3. High-risk areas should prepare for cases in 2-5 days\n');
}

main().catch(console.error);
