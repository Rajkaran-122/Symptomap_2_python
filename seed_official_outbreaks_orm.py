import sys
import os
import asyncio
import uuid
import datetime
from sqlalchemy import select

# Add backend-python to path so we can import app modules
# We are in root, backend is in backend-python
sys.path.append(os.path.join(os.getcwd(), 'backend-python'))

# Add backend-python to path so we can import app modules
# We are in root, backend is in backend-python
sys.path.append(os.path.join(os.getcwd(), 'backend-python'))

# Load .env file explicitly
from dotenv import load_dotenv
dotenv_path = os.path.join(os.getcwd(), 'backend-python', '.env')
load_dotenv(dotenv_path)

# Verify critical env vars (Mock if missing to pass validation for seeding)
if not os.getenv("JWT_SECRET_KEY"):
    os.environ["JWT_SECRET_KEY"] = "supersecret"
if not os.getenv("REDIS_URL"):
    os.environ["REDIS_URL"] = "redis://localhost:6379"
if not os.getenv("DATABASE_URL"):
    # Default to sqlite relative to script? Or absolute?
    # Backend usually expects sqlite+aiosqlite:///./symptomap.db
    # If using AsyncSession, must be async driver
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./backend-python/symptomap.db"

from app.core.database import AsyncSessionLocal
from app.models.outbreak import Hospital, Outbreak
from geoalchemy2.elements import WKTElement

async def seed():
    print("Beginning seed of Official Outbreaks (public map)...")
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. Check existing hospitals to avoid duplicates (by name)
            # We'll use the ones created or create new ones
            hospitals_data = [
                {
                    "name": "AIIMS Delhi",
                    "address": "Ansari Nagar, New Delhi",
                    "lat": 28.5672,
                    "lng": 77.2100,
                    "city": "New Delhi",
                    "state": "Delhi"
                },
                {
                    "name": "KEM Hospital",
                    "address": "Parel, Mumbai",
                    "lat": 18.9930,
                    "lng": 72.8247,
                    "city": "Mumbai",
                    "state": "Maharashtra"
                },
                {
                    "name": "Doan Hospital",
                    "address": "Indiranagar, Bangalore",
                    "lat": 12.9716,
                    "lng": 77.5946,
                    "city": "Bangalore",
                    "state": "Karnataka"
                },
                {
                    "name": "Apollo Chennai",
                    "address": "Greams Road, Chennai",
                    "lat": 13.0827,
                    "lng": 80.2707,
                    "city": "Chennai",
                    "state": "Tamil Nadu"
                }
            ]
            
            hospitals_map = {} # Name -> ID

            for h_data in hospitals_data:
                # Check exist
                result = await session.execute(select(Hospital).where(Hospital.name == h_data['name']))
                existing_h = result.scalar_one_or_none()
                
                if existing_h:
                    print(f"Hospital {h_data['name']} exists.")
                    hospitals_map[h_data['name']] = existing_h.id
                else:
                    print(f"Creating hospital {h_data['name']}...")
                    # Construct Geometry
                    loc_geom = WKTElement(f"POINT({h_data['lng']} {h_data['lat']})", srid=4326)
                    
                    new_h = Hospital(
                        id=uuid.uuid4(),
                        name=h_data['name'],
                        address=h_data['address'],
                        latitude=h_data['lat'],
                        longitude=h_data['lng'],
                        location=loc_geom, # Providing Geometry!
                        city=h_data['city'],
                        state=h_data['state'],
                        total_beds=500,
                        available_beds=100,
                        hospital_type="Public"
                    )
                    session.add(new_h)
                    await session.flush() # Get ID? UUID is set manually
                    hospitals_map[h_data['name']] = new_h.id

            # 2. Insert Outbreaks
            # Delhi: High/Critical (1200)
            # Mumbai: Moderate (450) - Wait, previous logic said 450 is High. User wants data based.
            # I will put 450. My logic will label it Red. That is fine.
            # Bangalore: Mild (45)
            # Chennai: Severe (320)
            
            outbreaks_data = [
                {
                    "hospital": "AIIMS Delhi",
                    "disease": "Dengue",
                    "cases": 1200,
                    "severity": "Critical"
                },
                {
                    "hospital": "KEM Hospital",
                    "disease": "Malaria",
                    "cases": 450,
                    "severity": "Moderate" # Label says Mod, Cases says High. 
                },
                {
                    "hospital": "Doan Hospital",
                    "disease": "Flu",
                    "cases": 45,
                    "severity": "Mild"
                },
                {
                    "hospital": "Apollo Chennai",
                    "disease": "Cholera",
                    "cases": 320,
                    "severity": "High"
                }
            ]
            
            for o_data in outbreaks_data:
                h_id = hospitals_map.get(o_data['hospital'])
                if not h_id:
                    print(f"Skipping outbreak for {o_data['hospital']} (ID missing)")
                    continue
                
                # Check for existing recent outbreak to avoid duplication
                # Simple check: same hospital, same disease
                # Actually, simpler to just add new one, timestamp will be different
                
                h_info = next(h for h in hospitals_data if h['name'] == o_data['hospital'])
                loc_geom = WKTElement(f"POINT({h_info['lng']} {h_info['lat']})", srid=4326)

                outbreak = Outbreak(
                    id=uuid.uuid4(),
                    hospital_id=h_id,
                    disease_type=o_data['disease'],
                    patient_count=o_data['cases'],
                    severity=o_data['severity'],
                    date_started=datetime.datetime.now() - datetime.timedelta(days=5),
                    date_reported=datetime.datetime.now(),
                    latitude=h_info['lat'],
                    longitude=h_info['lng'],
                    location=loc_geom,
                    verified=True # Important for public visibility?
                )
                session.add(outbreak)
                print(f"Added outbreak: {o_data['disease']} at {o_data['hospital']}")

            await session.commit()
            print("✅ Seeding completed successfully!")

        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(seed())
