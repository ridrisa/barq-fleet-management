"""Export Utility Functions

Helper functions for exporting data to various formats (CSV, Excel, PDF).
"""

import csv
import io
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional


def prepare_export_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prepare data for export by converting complex types to strings

    Args:
        data: List of dictionaries to export

    Returns:
        Cleaned data ready for export
    """
    cleaned_data = []

    for row in data:
        cleaned_row = {}
        for key, value in row.items():
            if isinstance(value, (datetime,)):
                cleaned_row[key] = value.isoformat()
            elif isinstance(value, Decimal):
                cleaned_row[key] = float(value)
            elif isinstance(value, (dict, list)):
                cleaned_row[key] = str(value)
            elif value is None:
                cleaned_row[key] = ""
            else:
                cleaned_row[key] = value
        cleaned_data.append(cleaned_row)

    return cleaned_data


def export_to_csv(
    data: List[Dict[str, Any]], columns: Optional[List[str]] = None, filename: Optional[str] = None
) -> str:
    """
    Export data to CSV format

    Args:
        data: List of dictionaries to export
        columns: Optional list of column names (uses all keys if not provided)
        filename: Optional filename for the export

    Returns:
        CSV string
    """
    if not data:
        return ""

    # Prepare data
    cleaned_data = prepare_export_data(data)

    # Determine columns
    if not columns:
        columns = list(cleaned_data[0].keys()) if cleaned_data else []

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")

    writer.writeheader()
    for row in cleaned_data:
        writer.writerow(row)

    return output.getvalue()


def export_to_excel_dict(
    data: List[Dict[str, Any]], columns: Optional[List[str]] = None, sheet_name: str = "Data"
) -> Dict[str, Any]:
    """
    Prepare data for Excel export (returns dict for openpyxl)

    Args:
        data: List of dictionaries to export
        columns: Optional list of column names
        sheet_name: Name of the Excel sheet

    Returns:
        Dictionary with sheet configuration
    """
    if not data:
        return {"sheet_name": sheet_name, "headers": [], "rows": []}

    # Prepare data
    cleaned_data = prepare_export_data(data)

    # Determine columns
    if not columns:
        columns = list(cleaned_data[0].keys()) if cleaned_data else []

    # Extract rows
    rows = []
    for row in cleaned_data:
        rows.append([row.get(col, "") for col in columns])

    return {"sheet_name": sheet_name, "headers": columns, "rows": rows}


def export_to_json(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prepare data for JSON export

    Args:
        data: List of dictionaries to export

    Returns:
        Cleaned data ready for JSON serialization
    """
    return prepare_export_data(data)


def format_column_name(column: str) -> str:
    """
    Format column name for display

    Args:
        column: Column name (e.g., 'total_deliveries')

    Returns:
        Formatted name (e.g., 'Total Deliveries')
    """
    return column.replace("_", " ").title()


def apply_column_formatting(
    data: List[Dict[str, Any]], format_config: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Apply formatting to specific columns

    Args:
        data: Data to format
        format_config: Dict mapping column names to format types
                      ('currency', 'percentage', 'date', 'number')

    Returns:
        Formatted data
    """
    formatted_data = []

    for row in data:
        formatted_row = {}
        for key, value in row.items():
            format_type = format_config.get(key)

            if format_type == "currency":
                formatted_row[key] = f"{float(value):,.2f}" if value else "0.00"
            elif format_type == "percentage":
                formatted_row[key] = f"{float(value):.2f}%" if value else "0.00%"
            elif format_type == "date":
                if isinstance(value, datetime):
                    formatted_row[key] = value.strftime("%Y-%m-%d")
                else:
                    formatted_row[key] = value
            elif format_type == "number":
                formatted_row[key] = f"{int(value):,}" if value else "0"
            else:
                formatted_row[key] = value

        formatted_data.append(formatted_row)

    return formatted_data


def chunk_data_for_export(
    data: List[Dict[str, Any]], chunk_size: int = 1000
) -> List[List[Dict[str, Any]]]:
    """
    Split large datasets into chunks for streaming export

    Args:
        data: Data to chunk
        chunk_size: Size of each chunk

    Returns:
        List of data chunks
    """
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunks.append(data[i : i + chunk_size])
    return chunks


def generate_export_filename(base_name: str, extension: str, include_timestamp: bool = True) -> str:
    """
    Generate filename for export

    Args:
        base_name: Base name for the file
        extension: File extension (without dot)
        include_timestamp: Whether to include timestamp

    Returns:
        Generated filename
    """
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.{extension}"
    return f"{base_name}.{extension}"


def create_summary_row(
    data: List[Dict[str, Any]], numeric_columns: List[str], summary_type: str = "sum"
) -> Dict[str, Any]:
    """
    Create a summary row for numeric columns

    Args:
        data: Data to summarize
        numeric_columns: Columns to include in summary
        summary_type: Type of summary ('sum', 'avg', 'min', 'max')

    Returns:
        Summary row dictionary
    """
    summary = {"label": summary_type.upper()}

    for col in numeric_columns:
        values = [float(row.get(col, 0)) for row in data if row.get(col) is not None]

        if not values:
            summary[col] = 0
            continue

        if summary_type == "sum":
            summary[col] = sum(values)
        elif summary_type == "avg":
            summary[col] = sum(values) / len(values)
        elif summary_type == "min":
            summary[col] = min(values)
        elif summary_type == "max":
            summary[col] = max(values)
        else:
            summary[col] = 0

    return summary


def validate_export_data(
    data: List[Dict[str, Any]], max_rows: int = 100000
) -> tuple[bool, Optional[str]]:
    """
    Validate data before export

    Args:
        data: Data to validate
        max_rows: Maximum number of rows allowed

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data:
        return False, "No data to export"

    if len(data) > max_rows:
        return False, f"Too many rows ({len(data)}). Maximum allowed: {max_rows}"

    return True, None


def filter_columns(
    data: List[Dict[str, Any]],
    include_columns: Optional[List[str]] = None,
    exclude_columns: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Filter columns from data

    Args:
        data: Data to filter
        include_columns: Columns to include (if provided, only these are kept)
        exclude_columns: Columns to exclude

    Returns:
        Filtered data
    """
    if not data:
        return data

    filtered_data = []

    for row in data:
        if include_columns:
            filtered_row = {k: v for k, v in row.items() if k in include_columns}
        elif exclude_columns:
            filtered_row = {k: v for k, v in row.items() if k not in exclude_columns}
        else:
            filtered_row = row.copy()

        filtered_data.append(filtered_row)

    return filtered_data


def sort_data(
    data: List[Dict[str, Any]], sort_by: str, descending: bool = False
) -> List[Dict[str, Any]]:
    """
    Sort data by a specific column

    Args:
        data: Data to sort
        sort_by: Column name to sort by
        descending: Sort in descending order

    Returns:
        Sorted data
    """
    try:
        return sorted(data, key=lambda x: x.get(sort_by, 0), reverse=descending)
    except (TypeError, KeyError):
        return data


def add_row_numbers(data: List[Dict[str, Any]], start: int = 1) -> List[Dict[str, Any]]:
    """
    Add row numbers to data

    Args:
        data: Data to add row numbers to
        start: Starting number

    Returns:
        Data with row numbers
    """
    numbered_data = []

    for i, row in enumerate(data, start=start):
        numbered_row = {"row_number": i, **row}
        numbered_data.append(numbered_row)

    return numbered_data


def transpose_data(data: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
    """
    Transpose data from row-based to column-based format

    Args:
        data: Row-based data

    Returns:
        Column-based data dictionary
    """
    if not data:
        return {}

    transposed = {key: [] for key in data[0].keys()}

    for row in data:
        for key, value in row.items():
            transposed[key].append(value)

    return transposed


def calculate_export_size(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Estimate export file size

    Args:
        data: Data to export

    Returns:
        Dictionary with size estimates
    """
    import sys

    if not data:
        return {"rows": 0, "columns": 0, "estimated_bytes": 0, "estimated_mb": 0.0}

    # Calculate approximate size
    sample_size = sys.getsizeof(str(data[0])) if data else 0
    total_size = sample_size * len(data)

    return {
        "rows": len(data),
        "columns": len(data[0].keys()) if data else 0,
        "estimated_bytes": total_size,
        "estimated_mb": round(total_size / (1024 * 1024), 2),
    }
