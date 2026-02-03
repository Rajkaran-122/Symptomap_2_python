#!/usr/bin/env python3
"""
Production Data Seeder via API
Seeds 5000 outbreaks, 200 pending approval requests, and auto-generates alerts
on the deployed SymptoMap production site.

Usage:
    python seed_production_api.py

This script uses the API endpoints to seed data on the live production site.
"""

import requests
import random
import json
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# CONFIGURATION - Update this URL to match your production deployment
# ============================================================================
PRODUCTION_API_URL = "https://symptomap-2-python-1.onrender.com/api/v1"
# Alternative URLs if using different deployment:
# PRODUCTION_API_URL = "https://symptomap.up.railway.app/api/v1"
# PRODUCTION_API_URL = "http://localhost:8000/api/v1"

# Doctor credentials for authentication
DOCTOR_EMAIL = "doctor_demo@symptomap.com"
DOCTOR_PASSWORD = "Doctor@SymptoMap2025"

# Admin credentials for admin actions
ADMIN_EMAIL = "admin@symptomap.com"
ADMIN_PASSWORD = "admin123"

# ============================================================================
# DATA CONFIGURATION
# ============================================================================
TOTAL_OUTBREAKS = 5000
PENDING_APPROVALS = 200
ALERTS_TO_GENERATE = 100

# Batch sizes for API calls
OUTBREAK_BATCH_SIZE = 50
APPROVAL_BATCH_SIZE = 20

# India cities with coordinates (50+ cities)
CITIES = [
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777},
    {"city": "Delhi", "state": "Delhi", "lat": 28.7041, "lng": 77.1025},
    {"city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946},
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707},
    {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lng": 88.3639},
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lng": 78.4867},
    {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567},
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lng": 72.5714},
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873},
    {"city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462},
    {"city": "Patna", "state": "Bihar", "lat": 25.5941, "lng": 85.1376},
    {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lng": 77.4126},
    {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577},
    {"city": "Nagpur", "state": "Maharashtra", "lat": 21.1458, "lng": 79.0882},
    {"city": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lng": 83.2185},
    {"city": "Kanpur", "state": "Uttar Pradesh", "lat": 26.4499, "lng": 80.3319},
    {"city": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3176, "lng": 82.9739},
    {"city": "Surat", "state": "Gujarat", "lat": 21.1702, "lng": 72.8311},
    {"city": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lng": 76.9558},
    {"city": "Kochi", "state": "Kerala", "lat": 9.9312, "lng": 76.2673},
    {"city": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lng": 76.9366},
    {"city": "Guwahati", "state": "Assam", "lat": 26.1445, "lng": 91.7362},
    {"city": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lng": 85.3096},
    {"city": "Raipur", "state": "Chhattisgarh", "lat": 21.2514, "lng": 81.6296},
    {"city": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lng": 85.8245},
    {"city": "Chandigarh", "state": "Punjab", "lat": 30.7333, "lng": 76.7794},
    {"city": "Dehradun", "state": "Uttarakhand", "lat": 30.3165, "lng": 78.0322},
    {"city": "Shimla", "state": "Himachal Pradesh", "lat": 31.1048, "lng": 77.1734},
    {"city": "Srinagar", "state": "J&K", "lat": 34.0837, "lng": 74.7973},
    {"city": "Jammu", "state": "J&K", "lat": 32.7266, "lng": 74.8570},
    {"city": "Amritsar", "state": "Punjab", "lat": 31.6340, "lng": 74.8723},
    {"city": "Ludhiana", "state": "Punjab", "lat": 30.9010, "lng": 75.8573},
    {"city": "Agra", "state": "Uttar Pradesh", "lat": 27.1767, "lng": 78.0081},
    {"city": "Meerut", "state": "Uttar Pradesh", "lat": 28.9845, "lng": 77.7064},
    {"city": "Nashik", "state": "Maharashtra", "lat": 19.9975, "lng": 73.7898},
    {"city": "Aurangabad", "state": "Maharashtra", "lat": 19.8762, "lng": 75.3433},
    {"city": "Rajkot", "state": "Gujarat", "lat": 22.3039, "lng": 70.8022},
    {"city": "Vadodara", "state": "Gujarat", "lat": 22.3072, "lng": 73.1812},
    {"city": "Mangalore", "state": "Karnataka", "lat": 12.9141, "lng": 74.8560},
    {"city": "Mysore", "state": "Karnataka", "lat": 12.2958, "lng": 76.6394},
    {"city": "Hubli", "state": "Karnataka", "lat": 15.3647, "lng": 75.1240},
    {"city": "Salem", "state": "Tamil Nadu", "lat": 11.6643, "lng": 78.1460},
    {"city": "Madurai", "state": "Tamil Nadu", "lat": 9.9252, "lng": 78.1198},
    {"city": "Tiruchirappalli", "state": "Tamil Nadu", "lat": 10.7905, "lng": 78.7047},
    {"city": "Vijayawada", "state": "Andhra Pradesh", "lat": 16.5062, "lng": 80.6480},
    {"city": "Warangal", "state": "Telangana", "lat": 17.9784, "lng": 79.5941},
    {"city": "Guntur", "state": "Andhra Pradesh", "lat": 16.3067, "lng": 80.4365},
    {"city": "Cuttack", "state": "Odisha", "lat": 20.4625, "lng": 85.8830},
    {"city": "Jodhpur", "state": "Rajasthan", "lat": 26.2389, "lng": 73.0243},
    {"city": "Udaipur", "state": "Rajasthan", "lat": 24.5854, "lng": 73.7125},
]

DISEASES = [
    "Dengue", "Malaria", "Typhoid", "Cholera", "COVID-19", 
    "Viral Fever", "Chikungunya", "Flu", "Hepatitis A", "Tuberculosis",
    "Japanese Encephalitis", "Leptospirosis", "Measles", "Mumps", "Rubella",
    "Diphtheria", "Pertussis", "Meningitis", "Gastroenteritis", "Pneumonia"
]

SEVERITIES = ["mild", "moderate", "severe", "critical"]
SEVERITY_WEIGHTS = [0.35, 0.35, 0.2, 0.1]

HOSPITALS = [
    "City Hospital", "District Medical Center", "Apollo Hospital", "AIIMS",
    "Government Hospital", "Max Healthcare", "Fortis Hospital", "Medanta",
    "KIMS Hospital", "Care Hospital", "Manipal Hospital", "Narayana Health",
    "Columbia Asia", "Aster Hospital", "Yashoda Hospital", "Global Hospital",
    "Ruby Hall Clinic", "Kokilaben Hospital", "Lilavati Hospital", "Breach Candy Hospital"
]

SYMPTOMS_MAP = {
    "Dengue": ["High fever", "Severe headache", "Pain behind eyes", "Joint pain", "Rash", "Bleeding gums"],
    "Malaria": ["Fever with chills", "Sweating", "Headache", "Nausea", "Vomiting", "Body aches"],
    "Typhoid": ["Prolonged fever", "Weakness", "Abdominal pain", "Headache", "Loss of appetite", "Diarrhea"],
    "Cholera": ["Severe watery diarrhea", "Dehydration", "Vomiting", "Leg cramps", "Rapid heart rate"],
    "COVID-19": ["Fever", "Cough", "Difficulty breathing", "Loss of taste/smell", "Fatigue", "Body aches"],
    "Viral Fever": ["High fever", "Body aches", "Headache", "Fatigue", "Chills", "Sore throat"],
    "Chikungunya": ["High fever", "Severe joint pain", "Muscle pain", "Headache", "Rash", "Fatigue"],
    "Flu": ["Fever", "Cough", "Sore throat", "Runny nose", "Body aches", "Fatigue"],
    "Hepatitis A": ["Fatigue", "Nausea", "Abdominal pain", "Loss of appetite", "Jaundice", "Dark urine"],
    "Tuberculosis": ["Persistent cough", "Coughing blood", "Night sweats", "Weight loss", "Fatigue", "Fever"],
}


class ProductionSeeder:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
        self.stats = {
            "outbreaks_created": 0,
            "approvals_created": 0,
            "alerts_generated": 0,
            "errors": []
        }
    
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate and get JWT token"""
        print(f"🔐 Authenticating as {email}...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                data={"username": email, "password": password},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers["Authorization"] = f"Bearer {self.token}"
                print(f"   ✅ Authenticated successfully")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                print(f"      Response: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def check_api_health(self) -> bool:
        """Check if API is accessible"""
        print(f"\n🏥 Checking API health at {self.base_url}...")
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                print("   ✅ API is healthy and reachable")
                return True
            else:
                # Try alternative health endpoints
                response = self.session.get(f"{self.base_url.replace('/api/v1', '')}/health", timeout=10)
                if response.status_code == 200:
                    print("   ✅ API is healthy and reachable")
                    return True
        except Exception as e:
            print(f"   ⚠️ Health check failed: {e}")
        
        print("   ⚠️ Health endpoint not available, proceeding anyway...")
        return True
    
    def generate_outbreak_data(self) -> dict:
        """Generate random outbreak data"""
        city_data = random.choice(CITIES)
        disease = random.choice(DISEASES)
        severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0]
        
        # Patient count based on severity
        if severity == "critical":
            patient_count = random.randint(100, 500)
        elif severity == "severe":
            patient_count = random.randint(50, 150)
        elif severity == "moderate":
            patient_count = random.randint(20, 80)
        else:
            patient_count = random.randint(5, 30)
        
        # Add randomness to coordinates
        lat = city_data["lat"] + random.uniform(-0.15, 0.15)
        lng = city_data["lng"] + random.uniform(-0.15, 0.15)
        
        # Get symptoms for this disease
        symptoms = SYMPTOMS_MAP.get(disease, ["Fever", "Fatigue", "Headache"])
        selected_symptoms = random.sample(symptoms, min(len(symptoms), random.randint(2, 4)))
        
        # Random date in last 2 years for training data
        days_ago = random.randint(0, 730)
        date_started = datetime.now() - timedelta(days=days_ago)
        
        return {
            "disease_type": disease,
            "patient_count": patient_count,
            "date_started": date_started.isoformat(),
            "severity": severity,
            "age_distribution": {
                "0-18": random.randint(10, 30),
                "19-45": random.randint(30, 50),
                "46+": random.randint(20, 40)
            },
            "gender_distribution": {
                "male": random.randint(40, 60),
                "female": 100 - random.randint(40, 60)
            },
            "symptoms": selected_symptoms,
            "notes": f"Outbreak of {disease} reported in {city_data['city']}. {patient_count} cases confirmed.",
            "hospital_name": f"{city_data['city']} {random.choice(HOSPITALS)}",
            "location": {
                "lat": lat,
                "lng": lng,
                "city": city_data["city"],
                "state": city_data["state"]
            }
        }
    
    def generate_approval_request_data(self) -> dict:
        """Generate pending approval request data"""
        city_data = random.choice(CITIES)
        disease = random.choice(DISEASES)
        severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0]
        
        lat = city_data["lat"] + random.uniform(-0.1, 0.1)
        lng = city_data["lng"] + random.uniform(-0.1, 0.1)
        
        patient_count = random.randint(10, 150)
        
        # Recent dates for pending approvals (Force recent for visibility)
        days_ago = 0 # random.randint(0, 14)
        date_reported = datetime.now() - timedelta(hours=random.randint(0, 23))
        
        return {
            "disease_type": disease,
            "patient_count": patient_count,
            "severity": severity,
            "latitude": lat,
            "longitude": lng,
            "location_name": f"{city_data['city']} {random.choice(HOSPITALS)}",
            "city": city_data["city"],
            "state": city_data["state"],
            "description": f"Suspected {disease} outbreak. {patient_count} patients showing symptoms including fever and fatigue. Requesting verification and resources.",
            "date_reported": date_reported.isoformat()
        }
    
    def create_outbreak(self, outbreak_data: dict) -> bool:
        """Create a single outbreak via API"""
        try:
            response = self.session.post(
                f"{self.base_url}/outbreaks/",
                json=outbreak_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                self.stats["outbreaks_created"] += 1
                return True
            else:
                self.stats["errors"].append(f"Outbreak creation failed: {response.status_code}")
                return False
        except Exception as e:
            self.stats["errors"].append(f"Outbreak error: {str(e)}")
            return False
    
    def submit_doctor_outbreak(self, data: dict) -> bool:
        """Submit outbreak report via doctor station (creates pending approval)"""
        try:
            response = self.session.post(
                f"{self.base_url}/doctor/outbreak",
                json=data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                self.stats["approvals_created"] += 1
                return True
            else:
                self.stats["errors"].append(f"Approval request failed: {response.status_code}")
                return False
        except Exception as e:
            self.stats["errors"].append(f"Approval error: {str(e)}")
            return False
    
    def generate_auto_alerts(self) -> int:
        """Trigger auto-alert generation"""
        print("\n🔔 Generating auto alerts...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/alerts/generate",
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get("alerts", {}).get("total_generated", 0)
                self.stats["alerts_generated"] += count
                print(f"   ✅ Auto-generated {count} alerts")
                return count
            else:
                print(f"   ⚠️ Auto-alert generation returned: {response.status_code}")
                return 0
        except Exception as e:
            print(f"   ❌ Auto-alert error: {e}")
            return 0
    
    def seed_outbreaks(self, count: int = 5000):
        """Seed outbreak records in parallel"""
        print(f"\n📊 Seeding {count} outbreak records (Parallel)...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(count):
                data = self.generate_outbreak_data()
                futures.append(executor.submit(self.create_outbreak, data))
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 100 == 0:
                    print(f"   📍 Progress: {completed}/{count} ({completed/count*100:.1f}%)")
        
        print(f"   ✅ Created {self.stats['outbreaks_created']} outbreaks")
    
    def seed_pending_approvals(self, count: int = 200):
        """Seed pending approval requests"""
        print(f"\n📋 Seeding {count} pending approval requests...")
        
        for i in range(count):
            data = self.generate_approval_request_data()
            self.submit_doctor_outbreak(data)
            
            if (i + 1) % 20 == 0:
                progress = ((i + 1) / count) * 100
                print(f"   📝 Progress: {i + 1}/{count} ({progress:.1f}%)")
                time.sleep(0.3)
        
        print(f"   ✅ Created {self.stats['approvals_created']} pending approvals")
    
    def seed_manual_alerts(self, count: int = 50):
        """Create manual alert submissions via doctor station"""
        print(f"\n⚠️ Creating {count} manual alert submissions...")
        
        alert_types = ["outbreak", "cluster", "capacity", "spread", "seasonal"]
        
        created = 0
        for i in range(count):
            city_data = random.choice(CITIES)
            disease = random.choice(DISEASES)
            
            alert_data = {
                "alert_type": random.choice(alert_types),
                "title": f"🚨 {disease} Alert - {city_data['city']}",
                "message": f"Alert: {disease} activity detected in {city_data['city']}, {city_data['state']}. "
                          f"Increased surveillance recommended. Healthcare facilities advised to stock supplies.",
                "latitude": city_data["lat"] + random.uniform(-0.1, 0.1),
                "longitude": city_data["lng"] + random.uniform(-0.1, 0.1),
                "affected_area": f"{city_data['city']}, {city_data['state']}",
                "expiry_hours": random.choice([24, 48, 72, 168])
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/doctor/alert",
                    json=alert_data,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    created += 1
            except Exception as e:
                self.stats["errors"].append(f"Manual alert error: {str(e)}")
            
            if (i + 1) % 10 == 0:
                print(f"   🔔 Progress: {i + 1}/{count}")
                time.sleep(0.2)
        
        print(f"   ✅ Created {created} manual alerts")
        self.stats["alerts_generated"] += created
    
    def print_summary(self):
        """Print seeding summary"""
        print("\n" + "=" * 60)
        print("📊 SEEDING SUMMARY")
        print("=" * 60)
        print(f"   ✅ Outbreaks created: {self.stats['outbreaks_created']}")
        print(f"   ✅ Pending approvals: {self.stats['approvals_created']}")
        print(f"   ✅ Alerts generated:  {self.stats['alerts_generated']}")
        
        if self.stats["errors"]:
            print(f"\n   ⚠️ Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats["errors"][:5]:
                print(f"      - {error}")
            if len(self.stats["errors"]) > 5:
                print(f"      ... and {len(self.stats['errors']) - 5} more")
        
        print("\n" + "=" * 60)
        print("✨ Production data seeding complete!")
        print("=" * 60)


def main():
    print("=" * 70)
    print("🚀 SymptoMap Production Data Seeder")
    print("=" * 70)
    print(f"Target API: {PRODUCTION_API_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("-" * 70)
    print(f"Configuration:")
    print(f"   - Outbreaks to create: {TOTAL_OUTBREAKS}")
    print(f"   - Pending approvals:   {PENDING_APPROVALS}")
    print(f"   - Alerts to generate:  {ALERTS_TO_GENERATE}")
    print("-" * 70)
    
    # Initialize seeder
    seeder = ProductionSeeder(PRODUCTION_API_URL)
    
    # Check API health
    seeder.check_api_health()
    
    # Authenticate - try admin first, then doctor
    auth_success = seeder.authenticate(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not auth_success:
        print("   ⚠️ Admin auth failed, trying doctor credentials...")
        auth_success = seeder.authenticate(DOCTOR_EMAIL, DOCTOR_PASSWORD)
    
    if not auth_success:
        print("\n❌ Authentication failed! Please check credentials.")
        print("   You may need to register users first or check the API status.")
        print("\n💡 Tips:")
        print("   1. Make sure the production API is running")
        print("   2. Verify credentials in the script configuration")
        print("   3. Check if users exist in the production database")
        return
    
    # Run seeding operations
    try:
        # Seed pending approval requests (200 for approval queue)
        seeder.seed_pending_approvals(PENDING_APPROVALS)

        # Seed outbreaks (5000 records for AI training)
        seeder.seed_outbreaks(TOTAL_OUTBREAKS)
        
        # Generate auto-alerts based on outbreak data
        seeder.generate_auto_alerts()
        
        # Create manual alert submissions (50 additional)
        seeder.seed_manual_alerts(50)
        
        # Print summary
        seeder.print_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Seeding interrupted by user")
        seeder.print_summary()
    except Exception as e:
        print(f"\n❌ Seeding error: {e}")
        import traceback
        traceback.print_exc()
        seeder.print_summary()


if __name__ == "__main__":
    main()
