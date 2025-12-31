# Business Requirements Document (BRD)
## SymptoMap Doctor Station - Complete Implementation

---

## 1. EXECUTIVE SUMMARY

Create a fully functional, secure, and deployable Doctor Station web application that allows healthcare professionals to manually submit outbreak data, create health alerts, and mark locations on an interactive map. The system must be production-ready, shareable via URL, and include robust security measures.

---

## 2. PROJECT OBJECTIVES

### Primary Goals
1. **Create a secure, password-protected web portal** for doctors to submit outbreak data
2. **Enable manual data entry** with comprehensive form validation
3. **Implement interactive map interface** for precise location marking
4. **Deploy shareable application** accessible via public URL
5. **Establish real-time dashboard integration** showing submitted data instantly
6. **Ensure data persistence** in database with backup capabilities
7. **Provide Alert Management System** for creating and managing health alerts

### Success Criteria
- Doctors can access portal via shareable link (e.g., `https://symptomap.com/doctor`)
- Login success rate > 99%
- Data submission completion rate > 95%
- Map location accuracy within 100 meters
- Dashboard updates within 30 seconds
- Zero data loss incidents
- Support for 100+ concurrent doctor users

---

## 3. FUNCTIONAL REQUIREMENTS

### 3.1 Authentication & Security

#### FR-3.1.1: Doctor Login System
**Description**: Secure authentication system for doctor access

**Requirements**:
- Single password authentication: `Doctor@SymptoMap2025`
- JWT token-based session management
- 24-hour token expiry with auto-renewal option
- Password displayed on login page for easy access
- "Remember Me" functionality (optional)
- Failed login attempt tracking (max 5 attempts, 15-minute lockout)
- Session timeout after 2 hours of inactivity

**Technical Implementation**:
```python
# Backend: FastAPI + JWT
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "symptomap-doctor-secret-key-2025"
ALGORITHM = "HS256"
DOCTOR_PASSWORD = "Doctor@SymptoMap2025"

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/api/v1/doctor/login")
async def doctor_login(password: str):
    if password != DOCTOR_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    token = create_access_token({"sub": "doctor"})
    return {"access_token": token, "token_type": "bearer"}
```

**Frontend Implementation**:
```typescript
// React TypeScript
const DoctorLogin = () => {
    const [password, setPassword] = useState('');
    
    const handleLogin = async () => {
        const response = await fetch('/api/v1/doctor/login', {
            method: 'POST',
            body: JSON.stringify({ password }),
        });
        const data = await response.json();
        localStorage.setItem('doctor_token', data.access_token);
        navigate('/doctor/station');
    };
};
```

---

### 3.2 Outbreak Data Submission

#### FR-3.2.1: Comprehensive Outbreak Form
**Description**: Multi-field form for detailed outbreak reporting

**Data Fields Required**:
1. **Disease Type** (Dropdown):
   - Dengue, Malaria, COVID-19, Influenza, Typhoid, Chikungunya
   - Tuberculosis, Hepatitis A/B/C, Cholera, Measles
   - Other (with text input)

2. **Patient Count** (Number input):
   - Range: 1-10,000
   - Validation: Positive integers only
   - Warning if > 100 cases

3. **Severity Level** (Radio buttons):
   - Mild (Green badge)
   - Moderate (Orange badge)
   - Severe (Red badge)

4. **Location Details**:
   - Hospital/Clinic Name
   - City (Text input with autocomplete)
   - State (Dropdown of Indian states)
   - Country (Default: India, editable)

5. **Geographic Coordinates**:
   - Latitude (Auto-filled from map)
   - Longitude (Auto-filled from map)
   - Manual override option

6. **Date Reported**:
   - Calendar picker
   - Default: Today
   - Cannot be future date

7. **Additional Information**:
   - Description (500 char max)
   - Symptoms observed
   - Treatment status
   - Contact information (optional)

**Database Schema**:
```sql
CREATE TABLE doctor_outbreaks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_type VARCHAR(100) NOT NULL,
    patient_count INTEGER NOT NULL CHECK(patient_count > 0),
    severity VARCHAR(20) NOT NULL CHECK(severity IN ('mild', 'moderate', 'severe')),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    location_name VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'India',
    description TEXT,
    symptoms TEXT,
    treatment_status VARCHAR(50),
    date_reported DATE NOT NULL,
    submitted_by VARCHAR(100),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    verification_status VARCHAR(20) DEFAULT 'pending'
);
```

**API Endpoint**:
```python
@router.post("/api/v1/doctor/outbreak")
async def submit_outbreak(
    outbreak: OutbreakSubmission,
    token: str = Depends(verify_token)
):
    # Validate data
    if outbreak.patient_count < 1:
        raise HTTPException(400, "Patient count must be positive")
    
    # Insert into database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO doctor_outbreaks 
        (disease_type, patient_count, severity, latitude, longitude,
         location_name, city, state, description, date_reported, submitted_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (outbreak.disease_type, outbreak.patient_count, ...))
    conn.commit()
    
    return {"success": True, "id": cursor.lastrowid}
```

---

### 3.3 Interactive Map Integration

#### FR-3.3.1: Map Location Picker
**Description**: Interactive map for precise location marking

**Map Features**:
1. **Base Map Provider**: OpenStreetMap or MapLibre GL JS
2. **Search Functionality**:
   - City search with autocomplete
   - Hospital/clinic search
   - Address lookup via geocoding API

3. **Location Marking**:
   - Click on map to set coordinates
   - Draggable marker for adjustment
   - Current location button (GPS)
   - Manual lat/long input fields

4. **Predefined Locations**:
```typescript
const MAJOR_CITIES = [
    { name: "Mumbai", lat: 19.0760, lon: 72.8777 },
    { name: "Delhi", lat: 28.7041, lon: 77.1025 },
    { name: "Bangalore", lat: 12.9716, lon: 77.5946 },
    { name: "Kolkata", lat: 22.5726, lon: 88.3639 },
    { name: "Chennai", lat: 13.0827, lon: 80.2707 },
    { name: "Hyderabad", lat: 17.3850, lon: 78.4867 },
    { name: "Pune", lat: 18.5204, lon: 73.8567 },
    { name: "Ahmedabad", lat: 23.0225, lon: 72.5714 },
    { name: "Jaipur", lat: 26.9124, lon: 75.7873 },
    { name: "Surat", lat: 21.1702, lon: 72.8311 }
];
```

5. **Visual Indicators**:
   - Existing outbreaks shown as colored pins
   - Severity-based color coding
   - Cluster markers for dense areas
   - Heatmap layer (optional)

**Implementation**:
```tsx
import MapLibreGL from 'maplibre-gl';

const MapPicker = ({ onLocationSelect }) => {
    const [map, setMap] = useState(null);
    const [marker, setMarker] = useState(null);
    
    useEffect(() => {
        const mapInstance = new MapLibreGL.Map({
            container: 'map',
            style: 'https://api.maptiler.com/maps/basic/style.json',
            center: [78.9629, 20.5937], // India center
            zoom: 4
        });
        
        mapInstance.on('click', (e) => {
            const { lng, lat } = e.lngLat;
            onLocationSelect({ latitude: lat, longitude: lng });
            
            if (marker) marker.remove();
            const newMarker = new MapLibreGL.Marker()
                .setLngLat([lng, lat])
                .addTo(mapInstance);
            setMarker(newMarker);
        });
        
        setMap(mapInstance);
    }, []);
    
    return <div id="map" style={{ height: '400px' }} />;
};
```

---

### 3.4 Alert Management System

#### FR-3.4.1: Health Alert Creation
**Description**: System for creating and broadcasting health alerts

**Alert Types**:
1. **Critical** (Red) - Immediate action required
2. **Warning** (Orange) - Caution advised
3. **Info** (Blue) - General information

**Alert Fields**:
```typescript
interface HealthAlert {
    alert_type: 'critical' | 'warning' | 'info';
    title: string; // Max 100 chars
    message: string; // Max 500 chars
    affected_area: string; // City/region name
    latitude: number;
    longitude: number;
    radius_km: number; // Affected radius
    expiry_hours: number; // Auto-expire after X hours
    priority: 1 | 2 | 3; // 1=highest
    category: 'outbreak' | 'weather' | 'infrastructure' | 'other';
    contact_info: string; // Optional
    action_required: string; // What people should do
}
```

**Database Schema**:
```sql
CREATE TABLE doctor_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type VARCHAR(20) NOT NULL,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    affected_area VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    radius_km DECIMAL(6, 2),
    priority INTEGER CHECK(priority IN (1, 2, 3)),
    category VARCHAR(50),
    contact_info VARCHAR(255),
    action_required TEXT,
    expiry_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    views_count INTEGER DEFAULT 0
);
```

**Alert Display on Dashboard**:
- Prominent banner for critical alerts
- Notification badges
- Geofenced alerts (show based on user location)
- Email/SMS notifications (future enhancement)

---

### 3.5 Dashboard Integration

#### FR-3.5.1: Real-Time Data Display
**Description**: Main dashboard shows doctor submissions instantly

**Dashboard Components**:
1. **Recent Submissions Section**:
   - Last 10 outbreaks
   - Last 5 alerts
   - Auto-refresh every 30 seconds

2. **Statistics Cards**:
   - Total submissions today
   - Active alerts count
   - High-risk zones
   - Most affected regions

3. **Map Visualization**:
   - All outbreak locations
   - Alert zones (circles)
   - Severity-based coloring
   - Clickable markers with details

**API Endpoint**:
```python
@router.get("/api/v1/outbreaks/all")
async def get_all_outbreaks():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get recent outbreaks
    cursor.execute("""
        SELECT * FROM doctor_outbreaks 
        WHERE status = 'active'
        ORDER BY submitted_at DESC
        LIMIT 50
    """)
    outbreaks = cursor.fetchall()
    
    # Get active alerts
    cursor.execute("""
        SELECT * FROM doctor_alerts 
        WHERE status = 'active' 
        AND expiry_date > datetime('now')
        ORDER BY priority ASC, created_at DESC
    """)
    alerts = cursor.fetchall()
    
    return {
        "outbreaks": outbreaks,
        "alerts": alerts,
        "total_outbreaks": len(outbreaks),
        "total_alerts": len(alerts),
        "last_updated": datetime.now().isoformat()
    }
```

---

## 4. NON-FUNCTIONAL REQUIREMENTS

### 4.1 Performance
- Page load time < 2 seconds
- API response time < 500ms
- Map rendering time < 1 second
- Support 500 concurrent users
- Database query execution < 100ms

### 4.2 Security
- HTTPS/SSL encryption mandatory
- JWT token authentication
- SQL injection prevention (parameterized queries)
- XSS protection
- CORS properly configured
- Rate limiting (100 requests/minute per IP)
- Input validation and sanitization
- Password hashing (if multi-user in future)

###4.3 Scalability
- Database: SQLite for development, PostgreSQL for production
- Horizontal scaling capability
- CDN for static assets
- Database connection pooling
- Caching layer (Redis)

### 4.4 Availability
- 99.9% uptime SLA
- Automated backups every 6 hours
- Disaster recovery plan
- Health check endpoints
- Error logging and monitoring

### 4.5 Usability
- Mobile-responsive design
- Intuitive UI/UX
- Accessibility (WCAG 2.1 Level AA)
- Multi-language support (English, Hindi)
- Offline mode (Progressive Web App)

---

## 5. DEPLOYMENT REQUIREMENTS

### 5.1 Production Deployment

**Platform Options**:
1. **Render.com** (Recommended - Free Tier)
2. **Railway.app**
3. **Heroku**
4. **AWS/Google Cloud/Azure**
5. **Self-hosted VPS**

**Deployment Steps**:
```bash
# 1. Build Docker images
docker build -t symptomap-backend ./backend-python
docker build -t symptomap-frontend ./frontend

# 2. Push to container registry
docker push symptomap-backend
docker push symptomap-frontend

# 3. Deploy with docker-compose
docker-compose -f docker-compose.prod.yml up -d

# 4. Set environment variables
export DATABASE_URL="postgresql://..."
export SECRET_KEY="your-secret-key"
export FRONTEND_URL="https://symptomap.com"
```

**Environment Variables**:
```env
# Backend
DATABASE_URL=sqlite:///symptomap.db
SECRET_KEY=symptomap-doctor-secret-key-2025
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=["https://symptomap.com"]

# Frontend
VITE_API_URL=https://api.symptomap.com/api/v1
VITE_MAP_API_KEY=your-maptiler-key
```

**Shareable URL Configuration**:
- Primary: `https://symptomap.com/doctor`
- API: `https://api.symptomap.com`
- Staging: `https://staging.symptomap.com/doctor`

---

## 6. DATA MANAGEMENT

### 6.1 Manual Data Import Feature

**Python Script for Bulk Import**:
```python
# scripts/import_outbreaks.py
import sqlite3
import csv
from datetime import datetime

def import_outbreaks_from_csv(csv_file):
    """Import outbreak data from CSV file"""
    conn = sqlite3.connect('symptomap.db')
    cursor = conn.cursor()
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO doctor_outbreaks 
                (disease_type, patient_count, severity, latitude, longitude,
                 location_name, city, state, description, date_reported)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['disease_type'],
                int(row['patient_count']),
                row['severity'],
                float(row['latitude']),
                float(row['longitude']),
                row['location_name'],
                row['city'],
                row['state'],
                row['description'],
                row['date_reported']
            ))
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {reader.line_num} outbreaks")

# Usage
if __name__ == "__main__":
    import_outbreaks_from_csv('data/outbreaks.csv')
```

**CSV Template**:
```csv
disease_type,patient_count,severity,latitude,longitude,location_name,city,state,description,date_reported
Dengue,45,moderate,26.9124,75.7873,SMS Hospital,Jaipur,Rajasthan,Seasonal outbreak,2025-01-15
Malaria,23,moderate,28.7041,77.1025,AIIMS Delhi,Delhi,Delhi,Monsoon cases,2025-01-16
```

### 6.2 Database Backup Strategy

**Automated Backup Script**:
```python
# scripts/backup_database.py
import shutil
from datetime import datetime
import os

def backup_database():
    """Create timestamped database backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    source = 'symptomap.db'
    backup_dir = 'backups'
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_file = f'{backup_dir}/symptomap_backup_{timestamp}.db'
    shutil.copy2(source, backup_file)
    
    print(f"✅ Database backed up to {backup_file}")
    
    # Keep only last 30 backups
    cleanup_old_backups(backup_dir, keep=30)

# Schedule: Run every 6 hours via cron
# 0 */6 * * * python scripts/backup_database.py
```

---

## 7. ADDITIONAL FEATURES

### 7.1 Submission History & Analytics
- View all past submissions by doctor
- Export submissions as CSV/PDF
- Monthly statistics report
- Trending diseases dashboard

### 7.2 Multi-Doctor Support (Future)
```python
# Enhanced authentication for multiple doctors
class Doctor(BaseModel):
    id: int
    name: str
    email: str
    password_hash: str
    hospital: str
    license_number: str
    verified: bool

@router.post("/register")
async def register_doctor(doctor: DoctorRegistration):
    # Hash password
    password_hash = bcrypt.hashpw(
        doctor.password.encode(), 
        bcrypt.gensalt()
    )
    # Save to database
    # Send verification email
```

### 7.3 Notification System
- Email notifications for new alerts
- SMS alerts for critical outbreaks
- Push notifications (PWA)
- WebSocket real-time updates

### 7.4 Data Verification System
- Admin approval workflow
- Automated anomaly detection
- Duplicate detection
- Data quality scoring

---

## 8. TESTING REQUIREMENTS

### 8.1 Unit Tests
```python
# tests/test_outbreak_submission.py
def test_outbreak_submission():
    outbreak = {
        "disease_type": "Dengue",
        "patient_count": 45,
        "severity": "moderate",
        ...
    }
    response = client.post("/api/v1/doctor/outbreak", json=outbreak)
    assert response.status_code == 200
    assert response.json()["success"] == True
```

### 8.2 Integration Tests
- API endpoint testing
- Database operations
- Authentication flow
- Map functionality

### 8.3 User Acceptance Testing
- Doctor workflow testing
- Dashboard verification
- Mobile responsiveness
- Cross-browser compatibility

---

## 9. DOCUMENTATION REQUIREMENTS

### 9.1 User Guide
- Login instructions
- Submission tutorial
- Map usage guide
- Alert creation guide
- Troubleshooting FAQ

### 9.2 API Documentation
- Swagger/OpenAPI specification
- Endpoint descriptions
- Request/response examples
- Authentication guide

### 9.3 Deployment Guide
- Step-by-step deployment
- Environment configuration
- SSL setup
- Backup procedures

---

## 10. SUCCESS METRICS & KPIs

1. **Adoption Rate**: 80% of registered doctors actively using within 3 months
2. **Data Quality**: 95% of submissions complete and accurate
3. **Response Time**: 95% of API calls under 500ms
4. **Uptime**: 99.9% availability
5. **User Satisfaction**: Net Promoter Score (NPS) > 50
6. **Alert Effectiveness**: 90% of critical alerts actioned within 1 hour

---

## 11. IMPLEMENTATION PRIORITY

### Phase 1 (MVP - Week 1-2)
✅ Basic authentication
✅ Outbreak submission form
✅ Simple map picker
✅ Database storage
✅ Basic dashboard display

### Phase 2 (Week 3-4)
- Enhanced map features
- Alert management
- Real-time updates
- Data export
- Production deployment

### Phase 3 (Month 2)
- Multi-doctor support
- Advanced analytics
- Notification system
- Mobile app (PWA)

---

## 12. CONSTRAINTS & ASSUMPTIONS

### Constraints
- Budget: $0-100/month for hosting
- Timeline: 4-6 weeks for full deployment
- Team: 1-2 developers
- Single password for all doctors (Phase 1)

### Assumptions
- Doctors have internet access
- Modern web browsers available
- Basic technical literacy
- English language proficiency

---

## 13. RISK ASSESSMENT

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data loss | High | Low | Automated backups, version control |
| Security breach | High | Medium | Strong authentication, encryption |
| Server downtime | Medium | Low | Multiple hosting options, monitoring |
| Low adoption | Medium | Medium | Training, user-friendly UI |
| Data quality issues | Medium | Medium | Validation, verification workflow |

---

## USE THIS BRD TO CREATE:

1. **Complete Backend Implementation** (Python FastAPI)
   - All API endpoints
   - Database models
   - Authentication system
   - Data validation

2. **Complete Frontend Implementation** (React TypeScript)
   - Login page
   - Doctor dashboard
   - Outbreak form
   - Alert form
   - Map component
   - Submissions history

3. **Deployment Configuration**
   - Docker files
   - docker-compose.yml
   - Environment templates
   - Nginx configuration

4. **Scripts & Utilities**
   - Data import/export
   - Database backup
   - Sample data generation
   - Testing utilities

5. **Documentation**
   - User manual
   - API documentation
   - Deployment guide
   - Developer guide

---

**END OF BRD**

This comprehensive document should serve as a complete specification for building, deploying, and maintaining the Doctor Station application.
