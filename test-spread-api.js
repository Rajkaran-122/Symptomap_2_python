const axios = require('axios');

async function testSpreadPrediction() {
    try {
        console.log('Testing spread prediction API...');
        const response = await axios.post('http://localhost:8787/api/v1/spread/predict', {
            bounds_north: 29.0,
            bounds_south: 28.0,
            bounds_east: 78.0,
            bounds_west: 76.5
        });

        console.log('✅ SUCCESS!');
        console.log(JSON.stringify(response.data, null, 2));
    } catch (error) {
        console.error('❌ ERROR:');
        console.error('Status:', error.response?.status);
        console.error('Message:', error.response?.data);
        console.error('Full error:', error.message);
    }
}

testSpreadPrediction();
