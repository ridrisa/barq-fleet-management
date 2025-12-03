"""Analytics Utility Functions

Common analytics calculations and helper functions used across analytics endpoints.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session


def calculate_percentage_change(current: float, previous: float) -> float:
    """Calculate percentage change between two values"""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 2)


def calculate_growth_rate(values: List[float]) -> float:
    """Calculate average growth rate from a list of values"""
    if len(values) < 2:
        return 0.0

    changes = []
    for i in range(1, len(values)):
        if values[i - 1] != 0:
            change = ((values[i] - values[i - 1]) / values[i - 1]) * 100
            changes.append(change)

    return round(sum(changes) / len(changes), 2) if changes else 0.0


def get_date_range_comparison(
    start_date: date, end_date: date, comparison_type: str = "previous_period"
) -> Tuple[date, date]:
    """
    Get comparison date range based on comparison type

    Args:
        start_date: Start date of current period
        end_date: End date of current period
        comparison_type: Type of comparison ('previous_period', 'same_period_last_year')

    Returns:
        Tuple of (comparison_start_date, comparison_end_date)
    """
    delta = (end_date - start_date).days

    if comparison_type == "previous_period":
        comparison_end = start_date - timedelta(days=1)
        comparison_start = comparison_end - timedelta(days=delta)
    elif comparison_type == "same_period_last_year":
        comparison_start = start_date - timedelta(days=365)
        comparison_end = end_date - timedelta(days=365)
    else:
        raise ValueError(f"Invalid comparison type: {comparison_type}")

    return comparison_start, comparison_end


def calculate_moving_average(values: List[float], window: int = 7) -> List[float]:
    """Calculate moving average for a list of values"""
    if len(values) < window:
        return values

    result = []
    for i in range(len(values)):
        if i < window - 1:
            result.append(sum(values[: i + 1]) / (i + 1))
        else:
            result.append(sum(values[i - window + 1 : i + 1]) / window)

    return [round(v, 2) for v in result]


def calculate_percentile(values: List[float], percentile: int) -> float:
    """Calculate percentile value from a list"""
    if not values:
        return 0.0

    sorted_values = sorted(values)
    index = (len(sorted_values) - 1) * percentile / 100

    if index.is_integer():
        return sorted_values[int(index)]
    else:
        lower = sorted_values[int(index)]
        upper = sorted_values[int(index) + 1]
        return lower + (upper - lower) * (index - int(index))


def calculate_variance(values: List[float]) -> float:
    """Calculate variance of values"""
    if len(values) < 2:
        return 0.0

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return round(variance, 2)


def calculate_standard_deviation(values: List[float]) -> float:
    """Calculate standard deviation of values"""
    variance = calculate_variance(values)
    return round(variance**0.5, 2)


def categorize_performance(value: float, thresholds: Dict[str, float]) -> str:
    """
    Categorize performance based on thresholds

    Args:
        value: Value to categorize
        thresholds: Dict with keys 'excellent', 'good', 'average', 'poor'

    Returns:
        Performance category string
    """
    if value >= thresholds.get("excellent", 90):
        return "excellent"
    elif value >= thresholds.get("good", 75):
        return "good"
    elif value >= thresholds.get("average", 60):
        return "average"
    else:
        return "poor"


def calculate_efficiency_score(
    actual: float, target: float, higher_is_better: bool = True
) -> float:
    """
    Calculate efficiency score as percentage of target achieved

    Args:
        actual: Actual value achieved
        target: Target value
        higher_is_better: Whether higher values are better (default True)

    Returns:
        Efficiency score (0-100+)
    """
    if target == 0:
        return 100.0 if actual >= 0 else 0.0

    score = (actual / target) * 100

    if not higher_is_better:
        # For metrics where lower is better (e.g., costs, delays)
        score = (2 * 100) - score if score <= 200 else 0

    return round(max(0, score), 2)


def aggregate_by_period(
    data: List[Dict[str, Any]], date_field: str, value_field: str, period: str = "daily"
) -> List[Dict[str, Any]]:
    """
    Aggregate data by time period

    Args:
        data: List of data dictionaries
        date_field: Name of the date field
        value_field: Name of the value field to aggregate
        period: Period type ('daily', 'weekly', 'monthly', 'yearly')

    Returns:
        List of aggregated data
    """
    from collections import defaultdict

    aggregated = defaultdict(float)

    for item in data:
        date_value = item.get(date_field)
        if not date_value:
            continue

        if isinstance(date_value, str):
            date_value = datetime.fromisoformat(date_value).date()
        elif isinstance(date_value, datetime):
            date_value = date_value.date()

        if period == "daily":
            key = date_value.isoformat()
        elif period == "weekly":
            week_start = date_value - timedelta(days=date_value.weekday())
            key = week_start.isoformat()
        elif period == "monthly":
            key = date_value.strftime("%Y-%m")
        elif period == "yearly":
            key = str(date_value.year)
        else:
            key = date_value.isoformat()

        aggregated[key] += float(item.get(value_field, 0))

    return [{"period": key, "value": round(value, 2)} for key, value in sorted(aggregated.items())]


def calculate_retention_rate(total_start: int, total_end: int, new_count: int) -> float:
    """Calculate retention rate"""
    if total_start == 0:
        return 0.0

    retained = total_end - new_count
    return round((retained / total_start) * 100, 2)


def calculate_churn_rate(total_start: int, churned_count: int) -> float:
    """Calculate churn rate"""
    if total_start == 0:
        return 0.0

    return round((churned_count / total_start) * 100, 2)


def calculate_cumulative_sum(values: List[float]) -> List[float]:
    """Calculate cumulative sum of values"""
    cumulative = []
    total = 0.0

    for value in values:
        total += value
        cumulative.append(round(total, 2))

    return cumulative


def calculate_run_rate(value: float, days_elapsed: int, total_days: int = 365) -> float:
    """Calculate annual run rate based on current performance"""
    if days_elapsed == 0:
        return 0.0

    daily_average = value / days_elapsed
    return round(daily_average * total_days, 2)


def detect_anomalies(values: List[float], threshold_std: float = 2.0) -> List[int]:
    """
    Detect anomalies in data using standard deviation method

    Args:
        values: List of values to check
        threshold_std: Number of standard deviations for threshold

    Returns:
        List of indices where anomalies are detected
    """
    if len(values) < 3:
        return []

    mean = sum(values) / len(values)
    std = calculate_standard_deviation(values)

    if std == 0:
        return []

    anomalies = []
    for i, value in enumerate(values):
        z_score = abs((value - mean) / std)
        if z_score > threshold_std:
            anomalies.append(i)

    return anomalies


def calculate_forecast_simple(
    historical_values: List[float], periods_ahead: int = 7
) -> List[float]:
    """
    Simple forecasting using moving average and trend

    Args:
        historical_values: Historical data points
        periods_ahead: Number of periods to forecast

    Returns:
        List of forecasted values
    """
    if len(historical_values) < 2:
        return [historical_values[-1] if historical_values else 0.0] * periods_ahead

    # Calculate trend
    n = len(historical_values)
    x_mean = (n - 1) / 2
    y_mean = sum(historical_values) / n

    numerator = sum((i - x_mean) * (historical_values[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0
    intercept = y_mean - slope * x_mean

    # Generate forecasts
    forecasts = []
    for i in range(periods_ahead):
        forecast = intercept + slope * (n + i)
        forecasts.append(round(max(0, forecast), 2))

    return forecasts


def calculate_correlation(values1: List[float], values2: List[float]) -> float:
    """Calculate correlation coefficient between two series"""
    if len(values1) != len(values2) or len(values1) < 2:
        return 0.0

    n = len(values1)
    mean1 = sum(values1) / n
    mean2 = sum(values2) / n

    numerator = sum((values1[i] - mean1) * (values2[i] - mean2) for i in range(n))

    sum_sq1 = sum((x - mean1) ** 2 for x in values1)
    sum_sq2 = sum((x - mean2) ** 2 for x in values2)
    denominator = (sum_sq1 * sum_sq2) ** 0.5

    if denominator == 0:
        return 0.0

    return round(numerator / denominator, 4)


def format_currency(amount: float, currency: str = "SAR") -> str:
    """Format amount as currency string"""
    return f"{amount:,.2f} {currency}"


def format_percentage(value: float) -> str:
    """Format value as percentage string"""
    return f"{value:.2f}%"


def calculate_distribution(values: List[float], bins: int = 10) -> List[Dict[str, Any]]:
    """Calculate distribution of values into bins"""
    if not values:
        return []

    min_val = min(values)
    max_val = max(values)

    if min_val == max_val:
        return [{"range": f"{min_val}", "count": len(values), "percentage": 100.0}]

    bin_size = (max_val - min_val) / bins
    distribution = [0] * bins

    for value in values:
        bin_index = min(int((value - min_val) / bin_size), bins - 1)
        distribution[bin_index] += 1

    total = len(values)
    result = []

    for i in range(bins):
        range_start = min_val + i * bin_size
        range_end = range_start + bin_size
        result.append(
            {
                "range": f"{range_start:.2f} - {range_end:.2f}",
                "count": distribution[i],
                "percentage": round((distribution[i] / total) * 100, 2),
            }
        )

    return result


def calculate_seasonal_index(values: List[float], season_length: int = 12) -> List[float]:
    """Calculate seasonal indices for time series data"""
    if len(values) < season_length * 2:
        return [1.0] * season_length

    # Calculate average for each season
    season_sums = [0.0] * season_length
    season_counts = [0] * season_length

    for i, value in enumerate(values):
        season_idx = i % season_length
        season_sums[season_idx] += value
        season_counts[season_idx] += 1

    season_averages = [
        season_sums[i] / season_counts[i] if season_counts[i] > 0 else 0
        for i in range(season_length)
    ]

    overall_average = sum(season_averages) / season_length if season_length > 0 else 1

    if overall_average == 0:
        return [1.0] * season_length

    indices = [avg / overall_average for avg in season_averages]
    return [round(idx, 4) for idx in indices]
