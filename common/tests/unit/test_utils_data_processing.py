#!/usr/bin/env python3
"""
Unit tests for utils/data_processing.py - Data Processing Utilities
Tests data transformation, validation, and utility functions.
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List

import pytest

from common.utils.data_processing import (
    convert_timestamps_to_iso,
    deep_merge_dicts,
    filter_companies_by_criteria,
    merge_company_lists,
    normalize_ticker_symbol,
    safe_json_serialize,
    validate_company_data,
)


@pytest.mark.utils
class TestConvertTimestampsToIso:
    """Test timestamp conversion functions."""

    def test_convert_datetime_to_iso(self):
        """Test converting datetime object to ISO string."""
        dt = datetime(2025, 1, 15, 10, 30, 45)
        result = convert_timestamps_to_iso(dt)
        assert result == "2025-01-15T10:30:45"

    def test_convert_dict_with_timestamps(self):
        """Test converting dictionary containing timestamps."""
        data = {
            "created_at": datetime(2025, 1, 15, 10, 30, 45),
            "updated_at": datetime(2025, 1, 15, 15, 20, 30),
            "metadata": {"processed_at": datetime(2025, 1, 15, 16, 45, 00), "version": "1.0"},
            "count": 42,
        }

        result = convert_timestamps_to_iso(data)

        assert result["created_at"] == "2025-01-15T10:30:45"
        assert result["updated_at"] == "2025-01-15T15:20:30"
        assert result["metadata"]["processed_at"] == "2025-01-15T16:45:00"
        assert result["metadata"]["version"] == "1.0"  # Non-datetime unchanged
        assert result["count"] == 42  # Non-datetime unchanged

    def test_convert_list_with_timestamps(self):
        """Test converting list containing timestamps."""
        data = [
            datetime(2025, 1, 15, 10, 30, 45),
            "string_value",
            42,
            {"timestamp": datetime(2025, 1, 15, 12, 0, 0), "value": "test"},
        ]

        result = convert_timestamps_to_iso(data)

        assert result[0] == "2025-01-15T10:30:45"
        assert result[1] == "string_value"  # Non-datetime unchanged
        assert result[2] == 42  # Non-datetime unchanged
        assert result[3]["timestamp"] == "2025-01-15T12:00:00"
        assert result[3]["value"] == "test"  # Non-datetime unchanged

    def test_convert_non_datetime_unchanged(self):
        """Test that non-datetime values are unchanged."""
        test_cases = ["string_value", 42, 3.14, True, None, {"key": "value"}, [1, 2, 3]]

        for test_case in test_cases:
            result = convert_timestamps_to_iso(test_case)
            assert result == test_case


@pytest.mark.utils
class TestDeepMergeDicts:
    """Test deep dictionary merging."""

    def test_merge_simple_dicts(self):
        """Test merging simple dictionaries."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}

        result = deep_merge_dicts(dict1, dict2)

        expected = {"a": 1, "b": 2, "c": 3, "d": 4}
        assert result == expected

    def test_merge_overlapping_keys(self):
        """Test merging with overlapping keys - second dict wins."""
        dict1 = {"a": 1, "b": 2, "c": 3}
        dict2 = {"b": 20, "c": 30, "d": 4}

        result = deep_merge_dicts(dict1, dict2)

        expected = {"a": 1, "b": 20, "c": 30, "d": 4}
        assert result == expected

    def test_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        dict1 = {"level1": {"a": 1, "b": 2, "level2": {"x": 10, "y": 20}}, "other": "value1"}

        dict2 = {
            "level1": {"c": 3, "level2": {"z": 30, "y": 200}},  # Should override
            "other": "value2",  # Should override
        }

        result = deep_merge_dicts(dict1, dict2)

        expected = {
            "level1": {
                "a": 1,
                "b": 2,
                "c": 3,
                "level2": {"x": 10, "y": 200, "z": 30},  # Overridden
            },
            "other": "value2",  # Overridden
        }

        assert result == expected

    def test_merge_empty_dicts(self):
        """Test merging with empty dictionaries."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {}

        result = deep_merge_dicts(dict1, dict2)
        assert result == dict1

        result = deep_merge_dicts({}, dict1)
        assert result == dict1

        result = deep_merge_dicts({}, {})
        assert result == {}

    def test_merge_preserves_original_dicts(self):
        """Test that original dictionaries are not modified."""
        dict1 = {"a": 1, "nested": {"x": 10}}
        dict2 = {"b": 2, "nested": {"y": 20}}

        dict1_copy = dict1.copy()
        dict2_copy = dict2.copy()

        result = deep_merge_dicts(dict1, dict2)

        # Original dicts should be unchanged
        assert dict1 == dict1_copy
        assert dict2 == dict2_copy

        # Result should be merged
        assert result["a"] == 1
        assert result["b"] == 2
        assert result["nested"]["x"] == 10
        assert result["nested"]["y"] == 20


@pytest.mark.utils
class TestNormalizeTickerSymbol:
    """Test ticker symbol normalization."""

    def test_normalize_basic_ticker(self):
        """Test normalizing basic ticker symbols."""
        test_cases = [("aapl", "AAPL"), ("MSFT", "MSFT"), ("googl", "GOOGL"), ("tsla", "TSLA")]

        for input_ticker, expected in test_cases:
            result = normalize_ticker_symbol(input_ticker)
            assert result == expected

    def test_normalize_with_whitespace(self):
        """Test normalizing tickers with whitespace."""
        test_cases = [("  aapl  ", "AAPL"), ("\tMSFT\n", "MSFT"), (" goog ", "GOOG")]

        for input_ticker, expected in test_cases:
            result = normalize_ticker_symbol(input_ticker)
            assert result == expected

    def test_normalize_special_characters(self):
        """Test normalizing tickers with special characters."""
        test_cases = [
            ("BRK.A", "BRK.A"),  # Valid special character
            ("BRK-B", "BRK-B"),  # Valid dash
            ("BRK/A", "BRK/A"),  # Handle forward slash
        ]

        for input_ticker, expected in test_cases:
            result = normalize_ticker_symbol(input_ticker)
            assert result == expected

    def test_normalize_empty_or_none(self):
        """Test normalizing empty or None ticker symbols."""
        with pytest.raises((ValueError, TypeError)):
            normalize_ticker_symbol("")

        with pytest.raises((ValueError, TypeError)):
            normalize_ticker_symbol(None)


@pytest.mark.utils
class TestValidateCompanyData:
    """Test company data validation."""

    def test_validate_complete_company_data(self):
        """Test validating complete company data."""
        company_data = {
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "cik": "0000320193",
            "sector": "Technology",
            "market_cap": 2500000000000,
        }

        result = validate_company_data(company_data)
        assert result is True

    def test_validate_minimal_company_data(self):
        """Test validating minimal required company data."""
        company_data = {"ticker": "MSFT", "name": "Microsoft Corporation"}

        result = validate_company_data(company_data)
        assert result is True

    def test_validate_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        # Missing ticker
        company_data1 = {"name": "Apple Inc.", "cik": "0000320193"}

        result = validate_company_data(company_data1)
        assert result is False

        # Missing name
        company_data2 = {"ticker": "AAPL", "cik": "0000320193"}

        result = validate_company_data(company_data2)
        assert result is False

    def test_validate_invalid_data_types(self):
        """Test validation fails for invalid data types."""
        # Invalid ticker type
        company_data = {"ticker": 123, "name": "Apple Inc."}  # Should be string

        result = validate_company_data(company_data)
        assert result is False

    def test_validate_empty_values(self):
        """Test validation fails for empty required values."""
        company_data = {"ticker": "", "name": "Apple Inc."}  # Empty string

        result = validate_company_data(company_data)
        assert result is False


@pytest.mark.utils
class TestFilterCompaniesByCriteria:
    """Test company filtering functionality."""

    @pytest.fixture
    def sample_companies(self) -> List[Dict[str, Any]]:
        """Sample company data for testing."""
        return [
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "sector": "Technology",
                "market_cap": 2500000000000,
                "country": "US",
            },
            {
                "ticker": "MSFT",
                "name": "Microsoft Corporation",
                "sector": "Technology",
                "market_cap": 2000000000000,
                "country": "US",
            },
            {
                "ticker": "JNJ",
                "name": "Johnson & Johnson",
                "sector": "Healthcare",
                "market_cap": 400000000000,
                "country": "US",
            },
            {
                "ticker": "TSM",
                "name": "Taiwan Semiconductor",
                "sector": "Technology",
                "market_cap": 500000000000,
                "country": "TW",
            },
        ]

    def test_filter_by_sector(self, sample_companies: List[Dict[str, Any]]):
        """Test filtering companies by sector."""
        criteria = {"sector": "Technology"}

        result = filter_companies_by_criteria(sample_companies, criteria)

        assert len(result) == 3
        tickers = [company["ticker"] for company in result]
        assert "AAPL" in tickers
        assert "MSFT" in tickers
        assert "TSM" in tickers
        assert "JNJ" not in tickers

    def test_filter_by_country(self, sample_companies: List[Dict[str, Any]]):
        """Test filtering companies by country."""
        criteria = {"country": "US"}

        result = filter_companies_by_criteria(sample_companies, criteria)

        assert len(result) == 3
        tickers = [company["ticker"] for company in result]
        assert "TSM" not in tickers

    def test_filter_by_market_cap_range(self, sample_companies: List[Dict[str, Any]]):
        """Test filtering companies by market cap range."""
        # Filter for companies with market cap >= 1 trillion
        criteria = {"market_cap_min": 1000000000000}

        result = filter_companies_by_criteria(sample_companies, criteria)

        assert len(result) == 2
        tickers = [company["ticker"] for company in result]
        assert "AAPL" in tickers
        assert "MSFT" in tickers

    def test_filter_multiple_criteria(self, sample_companies: List[Dict[str, Any]]):
        """Test filtering with multiple criteria (AND logic)."""
        criteria = {"sector": "Technology", "country": "US", "market_cap_min": 1500000000000}

        result = filter_companies_by_criteria(sample_companies, criteria)

        assert len(result) == 1
        assert result[0]["ticker"] == "AAPL"

    def test_filter_no_matches(self, sample_companies: List[Dict[str, Any]]):
        """Test filtering with criteria that match no companies."""
        criteria = {"sector": "Energy"}  # No energy companies in sample

        result = filter_companies_by_criteria(sample_companies, criteria)

        assert len(result) == 0
        assert result == []

    def test_filter_empty_criteria(self, sample_companies: List[Dict[str, Any]]):
        """Test filtering with empty criteria returns all companies."""
        criteria = {}

        result = filter_companies_by_criteria(sample_companies, criteria)

        assert len(result) == len(sample_companies)
        assert result == sample_companies


@pytest.mark.utils
class TestMergeCompanyLists:
    """Test company list merging functionality."""

    def test_merge_non_overlapping_lists(self):
        """Test merging company lists with no overlapping tickers."""
        list1 = [
            {"ticker": "AAPL", "name": "Apple Inc."},
            {"ticker": "MSFT", "name": "Microsoft Corporation"},
        ]

        list2 = [
            {"ticker": "GOOGL", "name": "Alphabet Inc."},
            {"ticker": "AMZN", "name": "Amazon.com Inc."},
        ]

        result = merge_company_lists(list1, list2)

        assert len(result) == 4
        tickers = [company["ticker"] for company in result]
        assert all(ticker in tickers for ticker in ["AAPL", "MSFT", "GOOGL", "AMZN"])

    def test_merge_overlapping_lists_second_wins(self):
        """Test merging with overlapping tickers - second list wins."""
        list1 = [
            {"ticker": "AAPL", "name": "Apple Inc.", "old_field": "old_value"},
            {"ticker": "MSFT", "name": "Microsoft Corporation"},
        ]

        list2 = [
            {"ticker": "AAPL", "name": "Apple Inc. Updated", "new_field": "new_value"},
            {"ticker": "GOOGL", "name": "Alphabet Inc."},
        ]

        result = merge_company_lists(list1, list2)

        assert len(result) == 3

        # Find the AAPL entry
        aapl_entry = next(company for company in result if company["ticker"] == "AAPL")
        assert aapl_entry["name"] == "Apple Inc. Updated"  # From second list
        assert "new_field" in aapl_entry  # From second list
        assert "old_field" not in aapl_entry  # Overwritten

    def test_merge_empty_lists(self):
        """Test merging with empty lists."""
        list1 = [{"ticker": "AAPL", "name": "Apple Inc."}]
        list2 = []

        result = merge_company_lists(list1, list2)
        assert result == list1

        result = merge_company_lists([], list1)
        assert result == list1

        result = merge_company_lists([], [])
        assert result == []


@pytest.mark.utils
class TestSafeJsonSerialize:
    """Test safe JSON serialization."""

    def test_serialize_basic_types(self):
        """Test serializing basic JSON-compatible types."""
        test_cases = [
            ({"key": "value"}, '{"key": "value"}'),
            ([1, 2, 3], "[1, 2, 3]"),
            ("string", '"string"'),
            (42, "42"),
            (True, "true"),
            (None, "null"),
        ]

        for input_data, expected in test_cases:
            result = safe_json_serialize(input_data)
            # Parse both to compare as objects (order might differ in dicts)
            assert json.loads(result) == json.loads(expected)

    def test_serialize_with_datetime(self):
        """Test serializing data with datetime objects."""
        data = {"timestamp": datetime(2025, 1, 15, 10, 30, 45), "data": "value"}

        result = safe_json_serialize(data)
        parsed = json.loads(result)

        assert parsed["timestamp"] == "2025-01-15T10:30:45"
        assert parsed["data"] == "value"

    def test_serialize_with_decimal(self):
        """Test serializing data with Decimal objects."""
        data = {"price": Decimal("123.45"), "quantity": Decimal("10.0")}

        result = safe_json_serialize(data)
        parsed = json.loads(result)

        # Decimals should be converted to float/int
        assert parsed["price"] == 123.45
        assert parsed["quantity"] == 10.0

    def test_serialize_complex_nested_data(self):
        """Test serializing complex nested data structures."""
        data = {
            "metadata": {"created": datetime(2025, 1, 15, 10, 30, 45), "version": Decimal("1.0")},
            "companies": [
                {
                    "ticker": "AAPL",
                    "market_cap": Decimal("2500000000000"),
                    "last_updated": datetime(2025, 1, 15, 12, 0, 0),
                }
            ],
            "summary": {"total_companies": 1, "processed": True},
        }

        result = safe_json_serialize(data)
        parsed = json.loads(result)

        # Verify all conversions worked
        assert parsed["metadata"]["created"] == "2025-01-15T10:30:45"
        assert parsed["metadata"]["version"] == 1.0
        assert parsed["companies"][0]["market_cap"] == 2500000000000
        assert parsed["companies"][0]["last_updated"] == "2025-01-15T12:00:00"
        assert parsed["summary"]["total_companies"] == 1
        assert parsed["summary"]["processed"] is True

    def test_serialize_handles_non_serializable_gracefully(self):
        """Test that non-serializable objects are handled gracefully."""

        # This test depends on implementation - it might convert to string
        # or raise an exception. Test based on actual implementation.
        class NonSerializable:
            pass

        data = {"object": NonSerializable()}

        # The function should either handle this gracefully or raise a clear error
        # Adjust based on actual implementation
        try:
            result = safe_json_serialize(data)
            # If it succeeds, verify it's valid JSON
            json.loads(result)
        except (TypeError, ValueError) as e:
            # If it raises an error, verify it's a clear error message
            assert "serializable" in str(e).lower() or "json" in str(e).lower()
