# Hospital Integration Guide - SymptoMap API

## Overview
This guide helps hospitals integrate their systems with SymptoMap to automatically submit outbreak reports. This enables real-time disease surveillance and proactive spread prediction.

---

## Quick Start

### API Endpoint
```
POST https://symptomap-api.example.com/api/v1/outbreaks
```

### Authentication
Contact your SymptoMap administrator for API credentials:
- `X-API-Key` header for authentication
- JWT token support (optional)

---

## Submitting Outbreak Reports

### Required Data
```json
{
  "disease_type": "Viral Fever",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "case_count": 45,
  "severity_level": 3,
  "symptoms": ["fever", "cough", "headache"],
  "location_name": "Apollo Hospital, Delhi"
}
```

### Field Specifications

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `disease_type` | String | Yes | Name of disease | "Viral Fever", "COVID-19", "Dengue" |
| `latitude` | Number | Yes | Hospital latitude | 28.6139 |
| `longitude` | Number | Yes | Hospital longitude | 77.2090 |
| `case_count` | Number | Yes | Number of confirmed cases | 45 |
| `severity_level` | Number | Yes | 1-5 scale (1=mild, 5=critical) | 3 |
| `symptoms` | Array | No | List of common symptoms | ["fever", "cough"] |
| `location_name` | String | No | Hospital/clinic name | "Apollo Hospital" |

---

## Code Examples

### Python
```python
import requests

API_URL = "https://symptomap-api.example.com/api/v1/outbreaks"
API_KEY = "your-api-key-here"

def submit_outbreak(disease, lat, lng, cases, severity):
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    payload = {
        "disease_type": disease,
        "latitude": lat,
        "longitude": lng,
        "case_count": cases,
        "severity_level": severity,
        "location_name": "Your Hospital Name"
    }
    
    response = requests.post(API_URL, json=payload, headers=headers)
    
    if response.status_code == 201:
        print(f"✅ Outbreak reported successfully! ID: {response.json()['data']['id']}")
    else:
        print(f"❌ Error: {response.json()['message']}")

# Example usage
submit_outbreak("Viral Fever", 28.6139, 77.2090, 45, 3)
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const API_URL = 'https://symptomap-api.example.com/api/v1/outbreaks';
const API_KEY = 'your-api-key-here';

async function submitOutbreak(disease, lat, lng, cases, severity) {
    try {
        const response = await axios.post(API_URL, {
            disease_type: disease,
            latitude: lat,
            longitude: lng,
            case_count: cases,
            severity_level: severity,
            location_name: 'Your Hospital Name'
        }, {
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            }
        });
        
        console.log(`✅ Outbreak reported! ID: ${response.data.data.id}`);
    } catch (error) {
        console.error(`❌ Error: ${error.response?.data?.message || error.message}`);
    }
}

// Example usage
submitOutbreak('Viral Fever', 28.6139, 77.2090, 45, 3);
```

### cURL (Testing)
```bash
curl -X POST https://symptomap-api.example.com/api/v1/outbreaks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "disease_type": "Viral Fever",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "case_count": 45,
    "severity_level": 3,
    "location_name": "Apollo Hospital, Delhi"
  }'
```

---

## Automated Integration Strategies

### 1. **Daily Batch Upload**
- Export outbreak data from your hospital system at EOD
- Parse and format as JSON
- Submit via API

**Recommended for:** Hospitals with existing data export capabilities

### 2. **Real-Time Event-Driven**
- Trigger API call when new outbreak case is confirmed
- Use webhooks or message queues (Kafka, RabbitMQ)

**Recommended for:** Hospitals with modern systems (FHIR, HL7)

### 3. **Scheduled Aggregation**
- Run cron job every 4-6 hours
- Query your database for new cases
- Submit aggregated reports

**Recommended for:** Smaller facilities without real-time infrastructure

---

## Receiving Spread Predictions

After submitting outbreak data, you can query for risk predictions in your area:

```bash
POST /api/v1/spread/predict
{
  "bounds_north": 29.0,
  "bounds_south": 28.0,
  "bounds_east": 78.0,
  "bounds_west": 76.5,
  "disease_type": "Viral Fever"
}
```

**Response:**
```json
{
  "data": {
    "current_outbreaks": [...],
    "high_risk_areas": [
      {
        "name": "Area_28.62N_77.25E",
        "lat": 28.62,
        "lng": 77.25,
        "risk_score": 7.5,
        "probability": 0.75,
        "estimated_cases": 18,
        "days_until_spread": 3
      }
    ],
    "alert_summary": [
      "Viral Fever detected (77 cases). High risk of spread to Area_28.62N_77.25E, Area_28.54N_77.39E in next 3 days (72% probability)"
    ]
  }
}
```

---

## Best Practices

### Data Privacy
- ✅ **DO**: Submit aggregated case counts
- ❌ **DON'T**: Include patient names or identifiable data

### Severity Levels
- **1** (Mild): Outpatient treatment, no hospitalization
- **2** (Low-Moderate): Some hospitalizations, manageable
- **3** (Moderate): Regular hospitalization rate
- **4** (High): High hospitalization, ICU beds needed
- **5** (Critical): Overwhelming healthcare resources

### Update Frequency
- **Recommended**: 1-2 times per day
- **Maximum**: Every 4 hours (avoid API rate limits)

---

## Error Handling

### Common Errors

| Status Code | Error | Solution |
|-------------|-------|----------|
| 400 | Validation Error | Check payload format |
| 401 | Unauthorized | Verify API key |
| 429 | Rate Limit | Wait before retrying |
| 500 | Server Error | Contact support |

### Retry Strategy
```python
import time

def submit_with_retry(payload, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise e
```

---

## Support & Contact

- **Technical Support**: support@symptomap.example.com
- **API Status**: status.symptomap.example.com
- **Documentation**: docs.symptomap.example.com

**Emergency Hotline**: +1-800-SYMPTOMAP (for critical outbreaks)

---

## Testing Environment

Use our sandbox environment for integration testing:

**Sandbox API**: `https://sandbox.symptomap.example.com/api/v1`  
**Test API Key**: `test_key_1234567890`

All data submitted to sandbox is cleared every 24 hours.
