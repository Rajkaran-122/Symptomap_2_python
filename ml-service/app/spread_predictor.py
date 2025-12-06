"""
Geographic Spread Prediction Engine
Analyzes outbreak locations and predicts which nearby areas are at risk
"""

import math
from typing import List, Dict, Tuple
from pydantic import BaseModel


class OutbreakLocation(BaseModel):
    lat: float
    lng: float
    cases: int
    disease: str
    severity: float = 2.5  # Default medium severity


class RiskArea(BaseModel):
    name: str
    lat: float
    lng: float
    risk_score: float
    probability: float
    estimated_cases: int
    days_until_spread: int


class SpreadPredictionResult(BaseModel):
    high_risk_areas: List[RiskArea]
    medium_risk_areas: List[RiskArea]
    low_risk_areas: List[RiskArea]
    risk_grid: List[Dict]  # Grid of lat/lng with risk scores for heatmap


class SpreadPredictor:
    """
    Geographic spread prediction based on epidemiological principles:
    - Distance decay: Risk decreases with distance
    - Population density: Higher density = higher spread risk
    - Connectivity: Transport hubs increase risk
    - Seasonality: Some diseases spread more in certain seasons
    """
    
    # Disease-specific parameters
    DISEASE_PARAMS = {
        "Viral Fever": {"R0": 1.5, "range_km": 50, "speed_km_per_day": 5},
        "COVID-19": {"R0": 2.5, "range_km": 100, "speed_km_per_day": 10},
        "Dengue": {"R0": 1.3, "range_km": 20, "speed_km_per_day": 2},
        "Influenza": {"R0": 1.8, "range_km": 80, "speed_km_per_day": 8},
        "Malaria": {"R0": 1.2, "range_km": 15, "speed_km_per_day": 1},
    }
    
    def __init__(self):
        self.grid_resolution = 0.05  # ~5km grid cells
    
    def haversine_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def calculate_risk_score(
        self, 
        distance_km: float, 
        outbreak_cases: int,
        outbreak_severity: float,
        disease: str
    ) -> float:
        """
        Calculate risk score for a location based on distance from outbreak
        
        Risk = base_risk * distance_decay * severity_factor
        Score is 0-10 where:
        - 8-10: Critical (immediate intervention needed)
        - 6-7: High (enhanced monitoring)
        - 4-5: Medium (watch closely)
        - 1-3: Low (normal surveillance)
        """
        params = self.DISEASE_PARAMS.get(disease, self.DISEASE_PARAMS["Viral Fever"])
        max_range = params["range_km"]
        R0 = params["R0"]
        
        # Base risk from outbreak size
        base_risk = min(10, (outbreak_cases / 10) * (outbreak_severity / 2.5))
        
        # Distance decay (exponential falloff)
        if distance_km > max_range:
            return 0.0
        
        distance_decay = math.exp(-distance_km / (max_range / 3))
        
        # R0 factor (higher R0 = faster spread)
        r0_factor = R0 / 2.0
        
        # Final risk score
        risk = base_risk * distance_decay * r0_factor
        
        return min(10.0, max(0.0, risk))
    
    def estimate_spread_time(self, distance_km: float, disease: str) -> int:
        """Estimate days until disease reaches this location"""
        params = self.DISEASE_PARAMS.get(disease, self.DISEASE_PARAMS["Viral Fever"])
        speed = params["speed_km_per_day"]
        
        # Add some randomness for incubation period
        base_days = distance_km / speed
        incubation_days = 2  # Average incubation
        
        return int(base_days + incubation_days)
    
    def estimate_cases(self, risk_score: float, outbreak_cases: int) -> int:
        """Estimate potential cases in at-risk area"""
        # Simple proportional model
        case_factor = risk_score / 10.0
        estimated = int(outbreak_cases * case_factor * 0.3)  # 30% transmission rate
        return max(1, estimated)
    
    def generate_risk_grid(
        self,
        outbreaks: List[OutbreakLocation],
        bounds: Dict[str, float]
    ) -> List[Dict]:
        """
        Generate a grid of risk scores for heatmap visualization
        """
        grid = []
        
        # Create grid cells
        lat = bounds["south"]
        while lat <= bounds["north"]:
            lng = bounds["west"]
            while lng <= bounds["east"]:
                # Calculate cumulative risk from all outbreaks
                total_risk = 0.0
                
                for outbreak in outbreaks:
                    distance = self.haversine_distance(lat, lng, outbreak.lat, outbreak.lng)
                    risk = self.calculate_risk_score(
                        distance,
                        outbreak.cases,
                        outbreak.severity,
                        outbreak.disease
                    )
                    total_risk += risk
                
                # Cap at 10
                total_risk = min(10.0, total_risk)
                
                if total_risk > 0.5:  # Only include cells with meaningful risk
                    grid.append({
                        "lat": round(lat, 4),
                        "lng": round(lng, 4),
                        "risk": round(total_risk, 2)
                    })
                
                lng += self.grid_resolution
            lat += self.grid_resolution
        
        return grid
    
    def find_at_risk_areas(
        self,
        outbreaks: List[OutbreakLocation],
        bounds: Dict[str, float]
    ) -> SpreadPredictionResult:
        """
        Main prediction function: Find areas at risk from existing outbreaks
        """
        risk_areas = {}
        
        # Sample points in a grid to find high-risk areas
        lat_step = (bounds["north"] - bounds["south"]) / 20
        lng_step = (bounds["east"] - bounds["west"]) / 20
        
        for i in range(21):
            for j in range(21):
                lat = bounds["south"] + i * lat_step
                lng = bounds["west"] + j * lng_step
                
                max_risk = 0.0
                dominant_outbreak = None
                
                # Find maximum risk from all outbreaks
                for outbreak in outbreaks:
                    distance = self.haversine_distance(lat, lng, outbreak.lat, outbreak.lng)
                    
                    # Skip if too close to outbreak center (that's current, not spread)
                    if distance < 2:
                        continue
                    
                    risk = self.calculate_risk_score(
                        distance,
                        outbreak.cases,
                        outbreak.severity,
                        outbreak.disease
                    )
                    
                    if risk > max_risk:
                        max_risk = risk
                        dominant_outbreak = outbreak
                
                if max_risk >= 4.0 and dominant_outbreak:  # Only track medium+ risk
                    key = f"{round(lat, 2)}_{round(lng, 2)}"
                    
                    if key not in risk_areas or risk_areas[key].risk_score < max_risk:
                        risk_areas[key] = RiskArea(
                            name=f"Area_{round(lat, 2)}N_{round(lng, 2)}E",
                            lat=round(lat, 4),
                            lng=round(lng, 4),
                            risk_score=round(max_risk, 2),
                            probability=round(min(0.95, max_risk / 10.0), 2),
                            estimated_cases=self.estimate_cases(max_risk, dominant_outbreak.cases),
                            days_until_spread=self.estimate_spread_time(
                                self.haversine_distance(lat, lng, dominant_outbreak.lat, dominant_outbreak.lng),
                                dominant_outbreak.disease
                            )
                        )
        
        # Categorize by risk level
        high_risk = [area for area in risk_areas.values() if area.risk_score >= 7.0]
        medium_risk = [area for area in risk_areas.values() if 5.0 <= area.risk_score < 7.0]
        low_risk = [area for area in risk_areas.values() if 4.0 <= area.risk_score < 5.0]
        
        # Sort by risk score descending
        high_risk.sort(key=lambda x: x.risk_score, reverse=True)
        medium_risk.sort(key=lambda x: x.risk_score, reverse=True)
        low_risk.sort(key=lambda x: x.risk_score, reverse=True)
        
        # Generate risk grid for heatmap
        risk_grid = self.generate_risk_grid(outbreaks, bounds)
        
        return SpreadPredictionResult(
            high_risk_areas=high_risk[:10],  # Top 10
            medium_risk_areas=medium_risk[:15],
            low_risk_areas=low_risk[:10],
            risk_grid=risk_grid
        )
