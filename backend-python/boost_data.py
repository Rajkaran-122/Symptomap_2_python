import asyncio
import random
import uuid
import traceback
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.outbreak import Outbreak, Hospital
from app.models.user import User
from app.models.broadcast import Broadcast

# Targets
TARGET_OUTBREAKS = 4938
TARGET_CASES = 38448
TARGET_BROADCASTS = 12

async def boost_data():
    print("Starting Data Boost...")
    
    try:
        async with AsyncSessionLocal() as db:
            # 1. Get current counts
            outbreak_count = await db.scalar(select(func.count(Outbreak.id))) or 0
            case_count = await db.scalar(select(func.sum(Outbreak.patient_count))) or 0
            
            print(f"Current Status: {outbreak_count} Outbreaks, {case_count} Cases")
            
            outbreaks_needed = max(0, TARGET_OUTBREAKS - outbreak_count)
            cases_needed = max(0, TARGET_CASES - case_count)
            
            if outbreaks_needed == 0 and cases_needed == 0:
                print("Targets already met!")
                return
    
            print(f"Goal: +{outbreaks_needed} Outbreaks, +{cases_needed} Cases")
            
            # 2. Get Hospitals to assign to (with location)
            hospitals_result = await db.execute(select(Hospital))
            hospitals = hospitals_result.scalars().all()
            
            if not hospitals:
                print("No hospitals found. Cannot create outbreaks.")
                return
    
            # 3. Get an admin user for verification
            # If no admin, explicit None is fine (schema allows it)
            admin_result = await db.execute(select(User).where(User.role == 'admin').limit(1))
            admin = admin_result.scalar_one_or_none()
            admin_id = admin.id if admin else None
            
            # 4. Generate Data
            new_outbreaks = []
            diseases = ["Dengue", "Malaria", "Viral Fever", "Typhoid", "Cholera", "Influenza", "Chikungunya", "COVID-19"]
            severities = ["mild", "moderate", "severe"]
            
            if outbreaks_needed > 0:
                avg_cases = cases_needed / outbreaks_needed
                
                for i in range(outbreaks_needed):
                    hospital = random.choice(hospitals)
                    
                    if i == outbreaks_needed - 1:
                        # Calculate remaining needed to hit exact target
                        # Note: case_count is initial. We sum new ones.
                        current_new_sum = sum(o.patient_count for o in new_outbreaks)
                        remaining_needed = max(1, TARGET_CASES - (case_count + current_new_sum))
                        cases = remaining_needed
                    else:
                        cases = int(random.uniform(avg_cases * 0.5, avg_cases * 1.5))
                        cases = max(1, cases)
                    
                    days_ago = random.randint(0, 30)
                    date_reported = datetime.now(timezone.utc) - timedelta(days=days_ago)
                    
                    outbreak = Outbreak(
                        id=uuid.uuid4(),
                        hospital_id=hospital.id,
                        reported_by=admin_id, # Optional but good
                        disease_type=random.choice(diseases),
                        patient_count=cases,
                        date_started=date_reported,
                        date_reported=date_reported,
                        severity=random.choice(severities),
                        # Copy location from hospital
                        latitude=hospital.latitude,
                        longitude=hospital.longitude,
                        verified=True,
                        verified_by=admin_id,
                        verification_date=date_reported,
                        created_at=date_reported,
                        updated_at=date_reported
                    )
                    new_outbreaks.append(outbreak)
                    
                # Bulk insert
                print(f"Injecting {len(new_outbreaks)} outbreaks...")
                db.add_all(new_outbreaks)
                await db.commit()
                print(f"Injected {len(new_outbreaks)} outbreaks.")
            
            # 5. Boost Broadcasts
            current_broadcasts = await db.scalar(select(func.count(Broadcast.id)).where(Broadcast.is_active == True)) or 0
            print(f"Current Active Broadcasts: {current_broadcasts}")
            
            broadcasts_needed = max(0, TARGET_BROADCASTS - current_broadcasts)
            
            if broadcasts_needed > 0:
                print(f"Generating {broadcasts_needed} new broadcasts...")
                new_broadcasts = []
                alert_types = [
                    ("Health Alert: Viral Spike", "high", "High viral load detected in multiple zones."),
                    ("Advisory: Mosquito Control", "moderate", "Mosquito breeding sites identified. Take precautions."),
                    ("Emergency: ICU Capacity", "critical", "ICU capacity reaching limits in downtown sector."),
                    ("Update: Vaccination Drive", "info", "New vaccination centers opening this weekend.")
                ]
                
                for _ in range(broadcasts_needed):
                    title, severity, content = random.choice(alert_types)
                    b = Broadcast(
                        id=uuid.uuid4(),
                        title=title,
                        content=content,
                        severity=severity,
                        region="Universal",
                        channels=["in_app"],
                        created_by=admin_id,
                        is_active=True,
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc)
                    )
                    new_broadcasts.append(b)
                
                db.add_all(new_broadcasts)
                await db.commit()
                print(f"Injected {len(new_broadcasts)} broadcasts.")

            # Double check
            final_outbreaks = await db.scalar(select(func.count(Outbreak.id)))
            final_cases = await db.scalar(select(func.sum(Outbreak.patient_count)))
            final_broadcasts = await db.scalar(select(func.count(Broadcast.id)).where(Broadcast.is_active == True))
            print(f"Final Status: {final_outbreaks} Outbreaks, {final_cases} Cases, {final_broadcasts} Active Broadcasts")

    except Exception as e:
        print(f"Error during boost: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(boost_data())
