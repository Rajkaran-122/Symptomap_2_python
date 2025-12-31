"""
Early Detection Algorithm - Statistical Analysis
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import numpy as np
from scipy import stats

from app.models.chatbot import AnonymousSymptomReport
from app.models.outbreak import Outbreak


class EarlyDetectionService:
    """Statistical early detection of disease outbreaks"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def detect_anomalies(
        self,
        location_city: str,
        lookback_days: int = 30
    ) -> Dict:
        """
        Detect unusual symptom patterns using statistical methods
        
        Args:
            location_city: City to analyze
            lookback_days: Days of historical data to analyze
        
        Returns:
            Dict with anomaly detection results
        """
        
        start_date = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        
        # Get symptom reports for the location
        result = await self.db.execute(
            select(AnonymousSymptomReport)
            .where(
                and_(
                    AnonymousSymptomReport.location_city == location_city,
                    AnonymousSymptomReport.created_at >= start_date
                )
            )
        )
        reports = result.scalars().all()
        
        if len(reports) < 10:
            return {
                "status": "insufficient_data",
                "message": f"Need at least 10 reports. Found {len(reports)}",
                "anomalies": []
            }
        
        # Analyze by symptom type
        symptom_clusters = self._cluster_by_symptoms(reports)
        anomalies = []
        
        for symptom, daily_counts in symptom_clusters.items():
            # Calculate baseline statistics
            mean_count = np.mean(daily_counts)
            std_count = np.std(daily_counts)
            
            # Recent count (last 3 days)
            recent_count = sum(daily_counts[-3:]) / 3
            
            # Z-score calculation
            if std_count > 0:
                z_score = (recent_count - mean_count) / std_count
                
                # Anomaly if z-score > 2 (95% confidence)
                if z_score > 2:
                    p_value = 1 - stats.norm.cdf(z_score)
                    
                    anomalies.append({
                        "symptom": symptom,
                        "baseline_mean": round(mean_count, 2),
                        "recent_count": round(recent_count, 2),
                        "z_score": round(z_score, 2),
                        "p_value": round(p_value, 4),
                        "significance": "high" if z_score > 3 else "moderate",
                        "increase_percentage": round(
                            ((recent_count - mean_count) / mean_count) * 100, 1
                        )
                    })
        
        # Sort by z-score
        anomalies.sort(key=lambda x: x['z_score'], reverse=True)
        
        return {
            "status": "completed",
            "location": location_city,
            "analysis_period_days": lookback_days,
            "total_reports": len(reports),
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies,
            "recommendation": self._generate_recommendation(anomalies)
        }
    
    def _cluster_by_symptoms(self, reports: List) -> Dict[str, List[float]]:
        """Group reports by symptom and count daily occurrences"""
        
        symptom_counts = {}
        
        for report in reports:
            symptoms = report.symptoms or []
            day = report.created_at.date()
            
            for symptom in symptoms:
                if symptom not in symptom_counts:
                    symptom_counts[symptom] = {}
                
                symptom_counts[symptom][day] = symptom_counts[symptom].get(day, 0) + 1
        
        # Convert to daily count lists
        result = {}
        for symptom, day_counts in symptom_counts.items():
            # Fill in missing days with 0
            all_days = sorted(day_counts.keys())
            if all_days:
                start = all_days[0]
                end = all_days[-1]
                daily_list = []
                
                current = start
                while current <= end:
                    daily_list.append(day_counts.get(current, 0))
                    current += timedelta(days=1)
                
                result[symptom] = daily_list
        
        return result
    
    def _generate_recommendation(self, anomalies: List[Dict]) -> str:
        """Generate recommendation based on anomalies"""
        
        if not anomalies:
            return "No unusual patterns detected. Continue routine monitoring."
        
        high_significance = [a for a in anomalies if a['significance'] == 'high']
        
        if high_significance:
            return (
                f"⚠️ HIGH ALERT: {len(high_significance)} symptom(s) showing "
                f"statistically significant increases. Recommend immediate "
                f"investigation and enhanced surveillance."
            )
        else:
            return (
                f"⚠️ MODERATE ALERT: {len(anomalies)} symptom(s) showing "
                f"moderate increases. Monitor closely for further developments."
            )
    
    async def check_location(self, city: str, country: str) -> Dict:
        """
        Quick check for outbreak potential in a location
        
        Returns risk level and recommendations
        """
        
        anomalies = await self.detect_anomalies(city, lookback_days=14)
        
        if anomalies['status'] == 'insufficient_data':
            return {
                "risk_level": "unknown",
                "message": "Insufficient data for analysis"
            }
        
        count = anomalies['anomalies_detected']
        
        if count == 0:
            return {"risk_level": "low", "message": "Normal patterns observed"}
        elif count <= 2:
            return {"risk_level": "moderate", "message": f"{count} unusual pattern(s) detected"}
        else:
            return {"risk_level": "high", "message": f"{count} significant anomalies detected"}
