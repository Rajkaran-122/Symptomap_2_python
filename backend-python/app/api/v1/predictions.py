"""
AI Prediction Engine - SEIR Model & Forecasting
Generates outbreak predictions with real data
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import math
import json

from app.core.database import get_db

router = APIRouter(prefix="/predictions", tags=["AI Predictions"])


class SEIRModel:
    """SEIR Epidemiological Model for disease spread prediction"""
    
    def __init__(self, population: int, initial_infected: int, beta: float = 0.5, 
                 sigma: float = 0.2, gamma: float = 0.1):
        """
        Initialize SEIR model
        :param population: Total population
        :param initial_infected: Initial infected count
        :param beta: Transmission rate
        :param sigma: Incubation rate (1/incubation period)
        :param gamma: Recovery rate (1/infectious period)
        """
        self.N = population
        self.beta = beta  # Contact rate * transmission probability
        self.sigma = sigma  # 1/5.2 days (average incubation)
        self.gamma = gamma  # 1/10 days (average recovery time)
        
        # Initial conditions
        self.I0 = initial_infected
        self.E0 = initial_infected * 2  # Estimated exposed
        self.R0_value = 0  # Initial recovered
        self.S0 = self.N - self.I0 - self.E0 - self.R0_value
    
    def calculate_R0(self) -> float:
        """Calculate basic reproduction number"""
        return self.beta / self.gamma
    
    def simulate(self, days: int) -> List[Dict]:
        """Run SEIR simulation for given days"""
        S, E, I, R = self.S0, self.E0, self.I0, self.R0_value
        results = []
        
        for day in range(days + 1):
            # Calculate new infections, exposures, recoveries
            new_exposed = (self.beta * S * I) / self.N
            new_infected = self.sigma * E
            new_recovered = self.gamma * I
            
            # Update compartments
            S = max(0, S - new_exposed)
            E = max(0, E + new_exposed - new_infected)
            I = max(0, I + new_infected - new_recovered)
            R = min(self.N, R + new_recovered)
            
            results.append({
                'day': day,
                'susceptible': int(S),
                'exposed': int(E),
                'infected': int(I),
                'recovered': int(R),
                'new_cases': int(new_infected),
                'total_cases': int(I + R)
            })
        
        return results


def calculate_confidence_interval(value: float, day: int, uncertainty: float = 0.15) -> Dict:
    """Calculate confidence intervals for predictions"""
    # Uncertainty increases with time
    uncertainty_factor = 1 + (uncertainty * day / 7)
    lower = int(value * (1 - uncertainty_factor * 0.5))
    upper = int(value * (1 + uncertainty_factor * 0.5))
    
    return {
        'value': int(value),
        'lower': max(0, lower),
        'upper': upper
    }


def calculate_risk_level(r0: float, active_cases: int, population: int) -> Dict:
    """Calculate risk assessment"""
    infection_rate = (active_cases / population) * 100000  # Per 100k
    
    if r0 > 2.5 or infection_rate > 500:
        level = 'CRITICAL'
        color = '#DC2626'
        score = 9
    elif r0 > 1.5 or infection_rate > 200:
        level = 'HIGH'
        color = '#F59E0B'
        score = 7
    elif r0 > 1.0 or infection_rate > 50:
        level = 'MODERATE'
        color = '#3B82F6'
        score = 5
    else:
        level = 'LOW'
        color = '#10B981'
        score = 3
    
    return {
        'level': level,
        'score': score,
        'color': color,
        'r0': round(r0, 2),
        'infection_rate': round(infection_rate, 1)
    }


@router.get("/forecast")
async def get_outbreak_forecast(
    days: int = 30,
    scenario: str = 'likely',  # best, likely, worst
    db: AsyncSession = Depends(get_db)
):
    """
    Generate comprehensive outbreak forecast with AI predictions
    """
    
    # Fetch current outbreak data
    outbreak_sql = """
        SELECT 
            disease_type,
            COUNT(*) as outbreak_count,
            SUM(patient_count) as total_patients,
            h.state,
            h.city,
            AVG(CASE 
                WHEN severity = 'severe' THEN 3
                WHEN severity = 'moderate' THEN 2
                ELSE 1
            END) as avg_severity
        FROM outbreaks o
        JOIN hospitals h ON o.hospital_id = h.id
        WHERE o.date_reported >= :start_date
        GROUP BY disease_type, h.state, h.city
        ORDER BY total_patients DESC
    """
    
    start_date = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
    result = await db.execute(text(outbreak_sql), {"start_date": start_date})
    outbreaks = result.fetchall()
    
    if not outbreaks:
        raise HTTPException(status_code=404, detail="No outbreak data found")
    
    # Get total current cases
    total_current = sum(row[2] for row in outbreaks)
    
    # Estimate population (can be enhanced with real data)
    population = 1000000  # Approximate affected population
    
    # Adjust parameters based on scenario
    if scenario == 'best':
        beta, sigma, gamma = 0.3, 0.25, 0.15  # With interventions
    elif scenario == 'worst':
        beta, sigma, gamma = 0.7, 0.15, 0.08  # No interventions
    else:  # likely
        beta, sigma, gamma = 0.5, 0.2, 0.1  # Current trajectory
    
    # Run SEIR model
    model = SEIRModel(
        population=population,
        initial_infected=total_current,
        beta=beta,
        sigma=sigma,
        gamma=gamma
    )
    
    forecast = model.simulate(days)
    r0 = model.calculate_R0()
    
    # Find peak
    peak_day = max(forecast, key=lambda x: x['infected'])
    peak_date = (datetime.now(timezone.utc) + timedelta(days=peak_day['day'])).date()
    
    # Calculate predictions with confidence intervals
    predictions = []
    for point in forecast[::3]:  # Every 3 days to reduce data
        predictions.append({
            'date': (datetime.now(timezone.utc) + timedelta(days=point['day'])).isoformat(),
            'day': point['day'],
            'infected': calculate_confidence_interval(point['infected'], point['day']),
            'exposed': calculate_confidence_interval(point['exposed'], point['day']),
            'recovered': calculate_confidence_interval(point['recovered'], point['day']),
            'new_cases': calculate_confidence_interval(point['new_cases'], point['day']),
            'total_cases': calculate_confidence_interval(point['total_cases'], point['day'])
        })
    
    # Risk assessment
    risk = calculate_risk_level(r0, total_current, population)
    
    # Hospital capacity prediction
    hospitalization_rate = 0.15  # 15% need hospitalization
    peak_hospitalized = int(peak_day['infected'] * hospitalization_rate)
    
    # Geographic spread prediction
    geographic_spread = []
    for outbreak in outbreaks[:5]:  # Top 5 affected areas
        spread_factor = 1 + (r0 - 1) * 0.3  # Growth based on R0
        geographic_spread.append({
            'location': f"{outbreak[4]}, {outbreak[3]}",
            'disease': outbreak[0],
            'current_cases': outbreak[2],
            'predicted_cases_7d': int(outbreak[2] * (spread_factor ** 7)),
            'predicted_cases_14d': int(outbreak[2] * (spread_factor ** 14)),
            'predicted_cases_30d': int(outbreak[2] * (spread_factor ** 30))
        })
    
    # Intervention recommendations
    recommendations = []
    if r0 > 1.5:
        recommendations.append({
            'priority': 'HIGH',
            'action': 'Implement social distancing measures',
            'impact': f'Could reduce R0 by 30-40%'
        })
    if peak_hospitalized > 100:
        recommendations.append({
            'priority': 'HIGH',
            'action': f'Prepare {peak_hospitalized} additional hospital beds',
            'impact': 'Critical for healthcare capacity'
        })
    if r0 > 1.0:
        recommendations.append({
            'priority': 'MEDIUM',
            'action': 'Increase testing and contact tracing',
            'impact': 'Early detection and isolation'
        })
    
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'scenario': scenario,
        'forecast_days': days,
        'summary': {
            'current_active_cases': total_current,
            'current_outbreaks': len(outbreaks),
            'reproduction_number': round(r0, 2),
            'peak_date': peak_date.isoformat(),
            'peak_cases': peak_day['infected'],
            'total_predicted_cases': forecast[-1]['total_cases'],
            'risk_assessment': risk
        },
        'time_series': predictions,
        'geographic_predictions': geographic_spread,
        'hospital_capacity': {
            'current_hospitalized': int(total_current * hospitalization_rate),
            'peak_hospitalized': peak_hospitalized,
            'beds_needed': max(0, peak_hospitalized - 50),  # Assuming 50 available
            'critical_date': peak_date.isoformat()
        },
        'recommendations': recommendations,
        'model_parameters': {
            'population': population,
            'transmission_rate': beta,
            'incubation_rate': sigma,
            'recovery_rate': gamma,
            'r0': round(r0, 2)
        }
    }


@router.get("/scenarios")
async def compare_scenarios(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Compare best/likely/worst case scenarios"""
    
    scenarios = {}
    for scenario in ['best', 'likely', 'worst']:
        try:
            result = await get_outbreak_forecast(days=days, scenario=scenario, db=db)
            scenarios[scenario] = result['summary']
        except HTTPException:
            continue
    
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'forecast_days': days,
        'scenarios': scenarios,
        'comparison': {
            'peak_difference': scenarios.get('worst', {}).get('peak_cases', 0) - 
                              scenarios.get('best', {}).get('peak_cases', 0),
            'intervention_impact': f"{((1 - scenarios.get('best', {}).get('reproduction_number', 1) / 
                                      scenarios.get('worst', {}).get('reproduction_number', 1)) * 100):.1f}% reduction in R0"
        }
    }
