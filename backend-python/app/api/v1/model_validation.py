"""
Model Validation and Comparison Module
Provides metrics, cross-validation, and model comparison for SEIR predictions
"""

import math
from typing import List, Dict, Tuple
from datetime import datetime, timezone, timedelta
from app.api.v1.training_data import HISTORICAL_OUTBREAKS, calculate_trained_parameters  # type: ignore


def calculate_rmse(actual: List[float], predicted: List[float]) -> float:
    """Calculate Root Mean Square Error"""
    if len(actual) != len(predicted) or len(actual) == 0:
        return 0.0
    
    squared_errors = [(a - p) ** 2 for a, p in zip(actual, predicted)]
    mse = sum(squared_errors) / len(squared_errors)
    return math.sqrt(mse)


def calculate_mae(actual: List[float], predicted: List[float]) -> float:
    """Calculate Mean Absolute Error"""
    if len(actual) != len(predicted) or len(actual) == 0:
        return 0.0
    
    absolute_errors = [abs(a - p) for a, p in zip(actual, predicted)]
    return sum(absolute_errors) / len(absolute_errors)


def calculate_mape(actual: List[float], predicted: List[float]) -> float:
    """Calculate Mean Absolute Percentage Error"""
    if len(actual) != len(predicted) or len(actual) == 0:
        return 0.0
    
    percentage_errors = []
    for a, p in zip(actual, predicted):
        if a != 0:
            percentage_errors.append(abs((a - p) / a) * 100)
    
    return sum(percentage_errors) / len(percentage_errors) if percentage_errors else 0.0


def calculate_r_squared(actual: List[float], predicted: List[float]) -> float:
    """Calculate R-squared (coefficient of determination)"""
    if len(actual) != len(predicted) or len(actual) == 0:
        return 0.0
    
    mean_actual = sum(actual) / len(actual)
    ss_tot = sum((a - mean_actual) ** 2 for a in actual)
    ss_res = sum((a - p) ** 2 for a, p in zip(actual, predicted))
    
    if ss_tot == 0:
        return 1.0 if ss_res == 0 else 0.0
    
    return 1 - (ss_res / ss_tot)


def run_seir_simulation(population: int, initial_infected: int, 
                        beta: float, sigma: float, gamma: float, 
                        days: int) -> List[Dict]:
    """Standalone SEIR simulation for validation"""
    N: float = float(population)
    I: float = float(initial_infected)
    E: float = float(I * 2.0)
    R: float = float(I * 0.3)
    S: float = float(N - I - E - R)
    
    results = []
    dt = 0.1
    steps_per_day = 10
    
    for day in range(days + 1):
        results.append({
            'day': day,
            'infected': int(float(I)),  # type: ignore
            'total_cases': int(float(I) + float(R))  # type: ignore
        })
        
        for _ in range(steps_per_day):
            dS = -beta * S * I / N  # type: ignore
            dE = beta * S * I / N - sigma * E  # type: ignore
            dI = sigma * E - gamma * I  # type: ignore
            dR = gamma * I  # type: ignore
            
            S = max(0.0, float(S) + float(dS) * dt)  # type: ignore
            E = max(0.0, float(E) + float(dE) * dt)  # type: ignore
            I = max(0.0, float(I) + float(dI) * dt)  # type: ignore
            R = min(float(N), float(R) + float(dR) * dt)  # type: ignore
    
    return results


def cross_validate_model(disease: str, k_folds: int = 5) -> Dict:
    """Perform k-fold cross-validation on historical data for a disease"""
    
    # Get historical data for disease
    disease_data = [d for d in HISTORICAL_OUTBREAKS if d['disease'] == disease]
    
    if len(disease_data) < k_folds:
        return {
            'disease': disease,
            'error': 'Insufficient data for cross-validation',
            'data_points': len(disease_data)
        }
    
    # Shuffle and split data
    import random
    shuffled: List[Dict] = disease_data.copy()
    random.seed(42)  # Reproducible
    random.shuffle(shuffled)
    
    fold_size = len(shuffled) // k_folds
    fold_results = []
    
    for fold in range(k_folds):
        # Split into train and test
        test_start = fold * fold_size
        test_end = test_start + fold_size
        
        test_data: List[Dict] = shuffled[test_start:test_end]  # type: ignore
        train_data: List[Dict] = shuffled[:test_start] + shuffled[test_end:]  # type: ignore
        
        if not test_data or not train_data:
            continue
        
        # Train: calculate parameters from training data
        avg_cases = sum(d['cases'] for d in train_data) / len(train_data)
        avg_duration = sum(d['duration'] for d in train_data) / len(train_data)
        
        gamma = 1 / (avg_duration / 3)
        growth_rate = (avg_cases / 100) ** (1 / avg_duration)
        beta = growth_rate * gamma * 1.5
        sigma = 0.2  # Standard incubation
        
        beta = max(0.1, min(0.9, beta))
        gamma = max(0.05, min(0.5, gamma))
        
        # Test: predict on test data
        actual_cases = [d['cases'] for d in test_data]
        predicted_cases = []
        
        for outbreak in test_data:
            # Simulate with initial 10% of final cases
            initial = max(10, int(outbreak['cases'] * 0.1))
            population = 10000000  # 10M
            
            forecast = run_seir_simulation(population, initial, beta, sigma, gamma, outbreak['duration'])
            peak_infected = max(f['infected'] for f in forecast)
            predicted_cases.append(peak_infected)
        
        # Calculate metrics
        rmse = calculate_rmse(actual_cases, predicted_cases)
        mae = calculate_mae(actual_cases, predicted_cases)
        mape = calculate_mape(actual_cases, predicted_cases)
        r2 = calculate_r_squared(actual_cases, predicted_cases)
        
        fold_results.append({
            'fold': fold + 1,
            'train_size': len(train_data),
            'test_size': len(test_data),
            'rmse': float(f"{rmse:.2f}"),
            'mae': float(f"{mae:.2f}"),
            'mape': float(f"{mape:.2f}"),
            'r_squared': float(f"{r2:.4f}")
        })
    
    # Average across folds
    if fold_results:
        avg_rmse = float(sum(f['rmse'] for f in fold_results)) / len(fold_results)
        avg_mae = float(sum(f['mae'] for f in fold_results)) / len(fold_results)
        avg_mape = float(sum(f['mape'] for f in fold_results)) / len(fold_results)
        avg_r2 = float(sum(f['r_squared'] for f in fold_results)) / len(fold_results)
    else:
        avg_rmse = avg_mae = avg_mape = avg_r2 = 0
    
    return {
        'disease': disease,
        'k_folds': k_folds,
        'data_points': len(disease_data),
        'fold_results': fold_results,
        'average_metrics': {
            'rmse': float(f"{avg_rmse:.2f}"),
            'mae': float(f"{avg_mae:.2f}"),
            'mape': float(f"{avg_mape:.2f}"),
            'r_squared': float(f"{avg_r2:.4f}")
        },
        'model_quality': 'Good' if avg_mape < 30 else 'Fair' if avg_mape < 50 else 'Needs Improvement'
    }


def compare_models(disease: str, state: str = "Maharashtra") -> Dict:
    """Compare different model configurations"""
    
    params = calculate_trained_parameters(disease, state)
    base_beta = params.get('beta', 0.4)
    base_sigma = params.get('sigma', 0.2)
    base_gamma = params.get('gamma', 0.1)
    
    # Define model variants
    models = {
        'baseline': {'beta': 0.4, 'sigma': 0.2, 'gamma': 0.1, 'desc': 'Default SEIR parameters'},
        'trained': {'beta': base_beta, 'sigma': base_sigma, 'gamma': base_gamma, 'desc': 'Trained on historical data'},
        'optimistic': {'beta': base_beta * 0.7, 'sigma': base_sigma, 'gamma': base_gamma * 1.2, 'desc': 'With interventions'},
        'pessimistic': {'beta': base_beta * 1.3, 'sigma': base_sigma, 'gamma': base_gamma * 0.8, 'desc': 'No interventions'},
    }
    
    # Simulate each model
    population = 10000000  # 10M
    initial_infected = 100
    days = 60
    
    comparisons = []
    
    for name, config in models.items():
        forecast = run_seir_simulation(
            population, initial_infected,
            float(config['beta']), float(config['sigma']), float(config['gamma']),
            days
        )
        
        peak_point = max(forecast, key=lambda x: x['infected'])
        final_cases = forecast[-1]['total_cases']
        r0_val = float(config['beta']) / float(config['gamma'])
        r0 = float(f"{r0_val:.2f}")
        
        comparisons.append({
            'model': name,
            'description': config['desc'],
            'parameters': {
                'beta': float(f"{float(config['beta']):.4f}"),
                'sigma': float(f"{float(config['sigma']):.4f}"),
                'gamma': float(f"{float(config['gamma']):.4f}")
            },
            'r0': r0,
            'peak_day': peak_point['day'],
            'peak_cases': peak_point['infected'],
            'total_60d': final_cases
        })
    
    # Calculate relative differences
    trained_model = next(c for c in comparisons if c['model'] == 'trained')
    trained_peak: float = float(str(trained_model['peak_cases']))
    
    for c in comparisons:
        if trained_peak > 0:
            diff = (float(str(c['peak_cases'])) - trained_peak) / trained_peak * 100.0
            c['diff_from_trained'] = float(f"{diff:.1f}")
        else:
            c['diff_from_trained'] = 0
    
    return {
        'disease': disease,
        'state': state,
        'simulation_params': {
            'population': population,
            'initial_cases': initial_infected,
            'days': days
        },
        'models': comparisons,
        'recommendation': 'trained',
        'recommendation_reason': 'Trained model uses parameters optimized from historical outbreak data'
    }


def get_validation_report() -> Dict:
    """Generate comprehensive validation report for all diseases"""
    
    diseases = list(set(d['disease'] for d in HISTORICAL_OUTBREAKS))
    
    validation_results = []
    for disease in diseases:
        cv_result = cross_validate_model(disease, k_folds=3)
        validation_results.append({
            'disease': disease,
            'data_points': cv_result.get('data_points', 0),
            'avg_rmse': cv_result.get('average_metrics', {}).get('rmse', 0),
            'avg_mae': cv_result.get('average_metrics', {}).get('mae', 0),
            'avg_mape': cv_result.get('average_metrics', {}).get('mape', 0),
            'r_squared': cv_result.get('average_metrics', {}).get('r_squared', 0),
            'quality': cv_result.get('model_quality', 'Unknown')
        })
    
    # Sort by quality
    validation_results.sort(key=lambda x: x['avg_mape'])
    
    overall_mape = sum(v['avg_mape'] for v in validation_results) / len(validation_results) if validation_results else 0
    
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'total_diseases': len(diseases),
        'total_data_points': len(HISTORICAL_OUTBREAKS),
        'overall_accuracy': float(f"{100.0 - float(overall_mape):.1f}"),
        'validation_by_disease': validation_results,
        'best_performing': validation_results[0]['disease'] if validation_results else None,
        'model_status': 'Production Ready' if overall_mape < 30 else 'Beta'
    }
