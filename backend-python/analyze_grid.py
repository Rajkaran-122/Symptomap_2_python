import asyncio
from sqlalchemy import select, func, distinct
from app.core.database import AsyncSessionLocal
from app.models.outbreak import Outbreak, Hospital

async def analyze_grid():
    async with AsyncSessionLocal() as db:
        # Clusters (Unique Hospitals/Locations?)
        clusters = await db.scalar(select(func.count(distinct(Outbreak.hospital_id))))
        
        # Severity Counts
        severe = await db.scalar(select(func.count(Outbreak.id)).where(Outbreak.severity == 'severe'))
        moderate = await db.scalar(select(func.count(Outbreak.id)).where(Outbreak.severity == 'moderate'))
        mild = await db.scalar(select(func.count(Outbreak.id)).where(Outbreak.severity == 'mild'))
        
        # Maybe "Visual Clusters" = Cities?
        cities = await db.scalar(select(func.count(distinct(Hospital.city))))

        print(f"CLUSTERS (Unique Hospitals): {clusters}")
        print(f"CITIES (Unique Cities): {cities}")
        print(f"SEVERE Outbreaks: {severe}")
        print(f"MODERATE Outbreaks: {moderate}")
        print(f"MILD Outbreaks: {mild}")

if __name__ == "__main__":
    asyncio.run(analyze_grid())
