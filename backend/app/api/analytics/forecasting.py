"""Forecasting API

Demand forecasting, resource forecasting, and predictive analytics.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.utils.analytics import (
    calculate_forecast_simple,
    calculate_seasonal_index,
    calculate_moving_average
)


router = APIRouter()


@router.get("/demand", response_model=dict)
def forecast_demand(
    db: Session = Depends(get_db),
    forecast_days: int = Query(30, ge=7, le=90),
    zone_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Forecast delivery demand"""
    # Get historical data (last 90 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    # This is a template - implement actual historical data query
    historical_values = [100.0 + i for i in range(90)]  # Sample data

    # Generate forecast
    forecasted_values = calculate_forecast_simple(historical_values, forecast_days)

    # Calculate moving average for smoothing
    smoothed_forecast = calculate_moving_average(forecasted_values, window=7)

    return {
        "forecast_period": {
            "start_date": (end_date + timedelta(days=1)).isoformat(),
            "end_date": (end_date + timedelta(days=forecast_days)).isoformat(),
            "days": forecast_days
        },
        "historical_average": sum(historical_values) / len(historical_values),
        "forecast": [
            {
                "date": (end_date + timedelta(days=i+1)).isoformat(),
                "forecasted_deliveries": int(forecasted_values[i]),
                "smoothed_forecast": int(smoothed_forecast[i]),
                "confidence_lower": int(forecasted_values[i] * 0.85),
                "confidence_upper": int(forecasted_values[i] * 1.15)
            }
            for i in range(len(forecasted_values))
        ],
        "total_forecasted": int(sum(forecasted_values)),
        "peak_day": {
            "date": (end_date + timedelta(days=forecasted_values.index(max(forecasted_values)) + 1)).isoformat(),
            "expected_deliveries": int(max(forecasted_values))
        }
    }


@router.get("/resource-needs", response_model=dict)
def forecast_resource_needs(
    db: Session = Depends(get_db),
    forecast_days: int = Query(30, ge=7, le=90),
    resource_type: str = Query("courier", regex="^(courier|vehicle|warehouse)$"),
    current_user: User = Depends(get_current_user),
):
    """Forecast resource requirements"""
    end_date = date.today()

    # Template response
    return {
        "forecast_period": {
            "start_date": (end_date + timedelta(days=1)).isoformat(),
            "end_date": (end_date + timedelta(days=forecast_days)).isoformat()
        },
        "resource_type": resource_type,
        "current_capacity": 100,
        "forecasted_needs": [
            {
                "date": (end_date + timedelta(days=i+1)).isoformat(),
                "required_count": 100 + i,
                "current_capacity": 100,
                "surplus_deficit": -(i)
            }
            for i in range(min(forecast_days, 7))
        ],
        "recommendations": [
            {
                "type": "hiring",
                "priority": "high",
                "description": f"Consider hiring 10 additional {resource_type}s by next week"
            }
        ]
    }


@router.get("/revenue", response_model=dict)
def forecast_revenue(
    db: Session = Depends(get_db),
    forecast_days: int = Query(30, ge=7, le=365),
    include_scenarios: bool = Query(False),
    current_user: User = Depends(get_current_user),
):
    """Forecast revenue"""
    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    # Get historical revenue data
    historical_values = [10000.0 + (i * 100) for i in range(90)]  # Sample data

    # Generate forecast
    forecasted_values = calculate_forecast_simple(historical_values, forecast_days)

    result = {
        "forecast_period": {
            "start_date": (end_date + timedelta(days=1)).isoformat(),
            "end_date": (end_date + timedelta(days=forecast_days)).isoformat()
        },
        "historical_average_daily": sum(historical_values) / len(historical_values),
        "forecast": [
            {
                "date": (end_date + timedelta(days=i+1)).isoformat(),
                "forecasted_revenue": round(forecasted_values[i], 2),
                "confidence_lower": round(forecasted_values[i] * 0.90, 2),
                "confidence_upper": round(forecasted_values[i] * 1.10, 2)
            }
            for i in range(len(forecasted_values))
        ],
        "total_forecasted": round(sum(forecasted_values), 2)
    }

    if include_scenarios:
        result["scenarios"] = {
            "conservative": round(sum(forecasted_values) * 0.85, 2),
            "baseline": round(sum(forecasted_values), 2),
            "optimistic": round(sum(forecasted_values) * 1.15, 2)
        }

    return result


@router.get("/cost", response_model=dict)
def forecast_costs(
    db: Session = Depends(get_db),
    forecast_days: int = Query(30, ge=7, le=365),
    cost_category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Forecast operational costs"""
    end_date = date.today()

    # Template forecast
    daily_forecast = 5000.0

    return {
        "forecast_period": {
            "start_date": (end_date + timedelta(days=1)).isoformat(),
            "end_date": (end_date + timedelta(days=forecast_days)).isoformat()
        },
        "cost_category": cost_category or "all",
        "forecast": [
            {
                "date": (end_date + timedelta(days=i+1)).isoformat(),
                "forecasted_cost": daily_forecast * (1 + (i * 0.001)),
                "breakdown": {
                    "operational": daily_forecast * 0.6,
                    "personnel": daily_forecast * 0.3,
                    "other": daily_forecast * 0.1
                }
            }
            for i in range(min(forecast_days, 7))
        ],
        "total_forecasted": daily_forecast * forecast_days,
        "cost_drivers": [
            {"driver": "Fuel prices", "impact": "medium", "trend": "increasing"},
            {"driver": "Labor costs", "impact": "high", "trend": "stable"}
        ]
    }


@router.get("/seasonal-patterns", response_model=dict)
def analyze_seasonal_patterns(
    db: Session = Depends(get_db),
    metric: str = Query("deliveries", description="Metric to analyze"),
    current_user: User = Depends(get_current_user),
):
    """Analyze seasonal patterns in data"""
    # Get historical data for at least 2 years
    # Calculate seasonal indices

    # Sample data
    monthly_data = [100 + (i * 10) for i in range(24)]  # 24 months

    seasonal_indices = calculate_seasonal_index(monthly_data, season_length=12)

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    return {
        "metric": metric,
        "analysis_period": "Last 24 months",
        "seasonal_indices": [
            {
                "month": months[i],
                "index": seasonal_indices[i],
                "interpretation": "above average" if seasonal_indices[i] > 1.1 else "below average" if seasonal_indices[i] < 0.9 else "average"
            }
            for i in range(12)
        ],
        "peak_season": {
            "month": months[seasonal_indices.index(max(seasonal_indices))],
            "index": max(seasonal_indices)
        },
        "low_season": {
            "month": months[seasonal_indices.index(min(seasonal_indices))],
            "index": min(seasonal_indices)
        }
    }


@router.get("/capacity-planning", response_model=dict)
def forecast_capacity_needs(
    db: Session = Depends(get_db),
    forecast_months: int = Query(6, ge=1, le=24),
    current_user: User = Depends(get_current_user),
):
    """Forecast capacity planning needs"""
    return {
        "forecast_period": f"Next {forecast_months} months",
        "current_capacity": {
            "couriers": 100,
            "vehicles": 80,
            "warehouse_space_sqm": 5000
        },
        "forecasted_needs": [
            {
                "month": f"Month {i+1}",
                "couriers_needed": 100 + (i * 5),
                "vehicles_needed": 80 + (i * 4),
                "warehouse_space_needed": 5000 + (i * 200)
            }
            for i in range(forecast_months)
        ],
        "investment_requirements": {
            "hiring_costs": 50000.0,
            "vehicle_acquisition": 200000.0,
            "warehouse_expansion": 100000.0,
            "total": 350000.0
        },
        "recommendations": [
            "Start hiring process for 10 couriers in next 2 months",
            "Consider leasing additional vehicles",
            "Evaluate warehouse expansion options"
        ]
    }


@router.get("/growth-projection", response_model=dict)
def project_growth(
    db: Session = Depends(get_db),
    projection_months: int = Query(12, ge=3, le=36),
    growth_rate: Optional[float] = Query(None, description="Override growth rate (%)"),
    current_user: User = Depends(get_current_user),
):
    """Project business growth"""
    # Calculate historical growth rate if not provided
    if not growth_rate:
        growth_rate = 5.0  # Default 5% monthly growth

    current_metrics = {
        "monthly_deliveries": 10000,
        "monthly_revenue": 300000.0,
        "active_couriers": 100
    }

    projections = []
    for month in range(1, projection_months + 1):
        multiplier = (1 + (growth_rate / 100)) ** month
        projections.append({
            "month": month,
            "deliveries": int(current_metrics["monthly_deliveries"] * multiplier),
            "revenue": round(current_metrics["monthly_revenue"] * multiplier, 2),
            "couriers_needed": int(current_metrics["active_couriers"] * multiplier)
        })

    return {
        "projection_period": f"{projection_months} months",
        "assumed_growth_rate": growth_rate,
        "current_state": current_metrics,
        "projections": projections,
        "summary": {
            "final_month_deliveries": projections[-1]["deliveries"],
            "final_month_revenue": projections[-1]["revenue"],
            "total_growth_percentage": round(((projections[-1]["deliveries"] / current_metrics["monthly_deliveries"]) - 1) * 100, 2)
        }
    }


@router.get("/risk-assessment", response_model=dict)
def assess_forecast_risks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Assess risks in forecasts"""
    return {
        "risk_factors": [
            {
                "factor": "Seasonal Demand Variance",
                "impact": "high",
                "probability": "medium",
                "mitigation": "Maintain flexible workforce capacity"
            },
            {
                "factor": "Fuel Price Volatility",
                "impact": "medium",
                "probability": "high",
                "mitigation": "Implement fuel surcharge mechanism"
            },
            {
                "factor": "Competition",
                "impact": "medium",
                "probability": "medium",
                "mitigation": "Focus on service quality and customer retention"
            }
        ],
        "confidence_level": 75,
        "recommendation": "Forecasts are reliable with medium confidence. Monitor key risk factors monthly."
    }
