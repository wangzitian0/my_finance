#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data processing utilities for transformation and manipulation.

This module provides utilities for common data processing operations
used throughout the application.

Issue #184: Utility consolidation - Data processing utilities
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

# Import pandas if available for enhanced data processing
try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def normalize_ticker_symbol(ticker: str) -> str:
    """
    Normalize ticker symbol to standard format.

    Args:
        ticker: Raw ticker symbol

    Returns:
        Normalized ticker symbol (uppercase, stripped)

    Raises:
        ValueError: If ticker is empty or whitespace-only
        TypeError: If ticker is None
    """
    if ticker is None:
        raise TypeError("Ticker symbol cannot be None")
    if not ticker or not ticker.strip():
        raise ValueError("Ticker symbol cannot be empty")
    return ticker.strip().upper()


def validate_company_data(company_data: Dict[str, Any]) -> bool:
    """
    Validate company data structure.

    Args:
        company_data: Company data dictionary

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(company_data, dict):
        return False

    required_fields = ["ticker", "name"]

    # Check that all required fields are present
    for field in required_fields:
        if field not in company_data:
            return False
        value = company_data[field]
        # Check that field has a value and is a string
        if not value or not isinstance(value, str):
            return False

    return True


def merge_company_lists(*company_lists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge multiple company lists, removing duplicates by ticker.
    Later lists take precedence for overlapping tickers.

    Args:
        *company_lists: Variable number of company list arguments

    Returns:
        Merged company list with unique tickers
    """
    ticker_to_company = {}

    for company_list in company_lists:
        for company in company_list:
            ticker = normalize_ticker_symbol(company.get("ticker", ""))
            if ticker:
                # Later entries overwrite earlier ones
                ticker_to_company[ticker] = company

    return list(ticker_to_company.values())


def filter_companies_by_criteria(
    companies: List[Dict[str, Any]], criteria: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Filter companies based on specified criteria.

    Args:
        companies: List of company dictionaries
        criteria: Filtering criteria

    Returns:
        Filtered company list
    """
    filtered_companies = []

    for company in companies:
        match = True

        for key, value in criteria.items():
            # Handle special criteria keys
            if key == "market_cap_min":
                if "market_cap" not in company or company["market_cap"] < value:
                    match = False
                    break
            elif key == "market_cap_max":
                if "market_cap" not in company or company["market_cap"] > value:
                    match = False
                    break
            elif key not in company:
                match = False
                break
            elif isinstance(value, str):
                if value.lower() not in company[key].lower():
                    match = False
                    break
            elif company[key] != value:
                match = False
                break

        if match:
            filtered_companies.append(company)

    return filtered_companies


def extract_unique_values(data_list: List[Dict[str, Any]], field: str) -> List[Any]:
    """
    Extract unique values from a specific field across a list of dictionaries.

    Args:
        data_list: List of dictionaries
        field: Field name to extract values from

    Returns:
        List of unique values
    """
    unique_values = set()

    for item in data_list:
        if field in item and item[field] is not None:
            unique_values.add(item[field])

    return sorted(list(unique_values))


def group_by_field(data_list: List[Dict[str, Any]], field: str) -> Dict[Any, List[Dict[str, Any]]]:
    """
    Group data by a specific field value.

    Args:
        data_list: List of dictionaries to group
        field: Field name to group by

    Returns:
        Dictionary with field values as keys and lists of matching items as values
    """
    grouped_data = {}

    for item in data_list:
        if field in item:
            key = item[field]
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append(item)

    return grouped_data


def convert_timestamps_to_iso(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert datetime and timestamp objects to ISO format strings.

    Args:
        data: Dictionary that may contain timestamp objects

    Returns:
        Dictionary with timestamps converted to ISO strings
    """
    if isinstance(data, dict):
        converted_data = {}
        for key, value in data.items():
            converted_data[key] = convert_timestamps_to_iso(value)
        return converted_data

    elif isinstance(data, list):
        return [convert_timestamps_to_iso(item) for item in data]

    elif isinstance(data, datetime):
        return data.isoformat()

    elif PANDAS_AVAILABLE and isinstance(data, pd.Timestamp):
        return data.isoformat()

    else:
        return data


def safe_json_serialize(data: Any) -> str:
    """
    Safely serialize data to JSON, handling non-serializable objects.

    Args:
        data: Data to serialize

    Returns:
        JSON string representation
    """

    def json_serializer(obj):
        """Custom JSON serializer for non-serializable objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            # Convert Decimal to float for JSON serialization
            return float(obj)
        elif PANDAS_AVAILABLE and isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        else:
            return str(obj)

    try:
        return json.dumps(data, default=json_serializer, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Serialization failed: {str(e)}"})


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, with dict2 values taking precedence.

    Args:
        dict1: Base dictionary
        dict2: Dictionary to merge (takes precedence)

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value

    return result
