#!/usr/bin/env python3
"""
Test data fixtures for all dataset tiers.
Provides sample data for unit tests and integration tests.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import pytest

class TestDataFixtures:
    """Test data fixtures for different scenarios"""
    
    @staticmethod
    def sample_yfinance_data() -> Dict[str, Any]:
        """Sample yfinance API response data"""
        return {
            "chart": {
                "result": [{
                    "meta": {
                        "currency": "USD",
                        "symbol": "AAPL",
                        "exchangeName": "NMS",
                        "instrumentType": "EQUITY",
                        "firstTradeDate": 345479400,
                        "regularMarketTime": 1702670400,
                        "gmtoffset": -18000,
                        "timezone": "EST",
                        "exchangeTimezoneName": "America/New_York",
                        "regularMarketPrice": 193.6,
                        "chartPreviousClose": 194.83,
                        "priceHint": 2,
                        "currentTradingPeriod": {
                            "pre": {
                                "timezone": "EST",
                                "start": 1702641600,
                                "end": 1702656000,
                                "gmtoffset": -18000
                            },
                            "regular": {
                                "timezone": "EST", 
                                "start": 1702656000,
                                "end": 1702679400,
                                "gmtoffset": -18000
                            },
                            "post": {
                                "timezone": "EST",
                                "start": 1702679400,
                                "end": 1702695000,
                                "gmtoffset": -18000
                            }
                        },
                        "dataGranularity": "1d",
                        "range": "1y",
                        "validRanges": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
                    },
                    "timestamp": [1640995200, 1641081600, 1641168000, 1641254400, 1641340800],
                    "indicators": {
                        "quote": [{
                            "open": [177.830, 178.090, 176.120, 172.700, 172.000],
                            "high": [182.880, 179.700, 177.470, 175.300, 175.180],
                            "low": [177.710, 173.790, 174.520, 171.090, 171.020],
                            "close": [182.010, 174.920, 175.080, 172.190, 172.170],
                            "volume": [59773000, 80023000, 63814000, 61177000, 57758000]
                        }],
                        "adjclose": [{
                            "adjclose": [181.50, 174.47, 174.64, 171.75, 171.73]
                        }]
                    }
                }],
                "error": None
            }
        }
    
    @staticmethod
    def sample_sec_filing_text() -> str:
        """Sample SEC filing text content"""
        return """<DOCUMENT>
<TYPE>10-K
<SEQUENCE>1
<FILENAME>aapl-20230930.htm
<DESCRIPTION>10-K
<TEXT>
<html>
<head>
<title>Apple Inc. - Form 10-K</title>
</head>
<body>
<div class="main">
<h1>UNITED STATES</h1>
<h1>SECURITIES AND EXCHANGE COMMISSION</h1>
<h1>Washington, D.C. 20549</h1>

<h2>FORM 10-K</h2>

<h2>ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934</h2>

<p>For the fiscal year ended September 30, 2023</p>

<h3>Commission File Number: 001-36743</h3>

<h2>Apple Inc.</h2>
<p>(Exact name of registrant as specified in its charter)</p>

<table>
<tr>
<td>California</td>
<td>94-2404110</td>
</tr>
<tr>
<td>(State or other jurisdiction of incorporation or organization)</td>
<td>(I.R.S. Employer Identification No.)</td>
</tr>
</table>

<p>One Apple Park Way<br/>
Cupertino, California 95014<br/>
(408) 996-1010</p>

<h3>Securities registered pursuant to Section 12(b) of the Act:</h3>

<table>
<tr>
<th>Title of each class</th>
<th>Trading Symbol(s)</th>
<th>Name of each exchange on which registered</th>
</tr>
<tr>
<td>Common Stock, $0.00001 par value per share</td>
<td>AAPL</td>
<td>The Nasdaq Global Select Market</td>
</tr>
</table>

<h3>PART I</h3>

<h4>Item 1. Business</h4>

<p>Company Overview</p>

<p>The Company designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories, and sells a variety of related services. The Company's fiscal year is the 52- or 53-week period that ends on the last Saturday of September.</p>

<p>Products</p>

<p>iPhone</p>
<p>iPhone is the Company's line of smartphones based on its iOS operating system. The iPhone line includes iPhone 15 Pro, iPhone 15 Pro Max, iPhone 15, iPhone 15 Plus, iPhone 14, iPhone 14 Plus, iPhone 13 and iPhone SE.</p>

<p>Revenue and Profit Information</p>
<p>Net sales for fiscal 2023 were $383.3 billion compared to $394.3 billion for fiscal 2022.</p>
<p>Net income for fiscal 2023 was $97.0 billion compared to $99.8 billion for fiscal 2022.</p>

</div>
</body>
</html>
</TEXT>
</DOCUMENT>"""
    
    @staticmethod
    def sample_build_manifest() -> Dict[str, Any]:
        """Sample build manifest structure"""
        return {
            "build_info": {
                "build_id": "20250810_120000",
                "start_time": "2025-08-10T12:00:00",
                "end_time": "2025-08-10T12:30:00",
                "status": "completed",
                "configuration": "test",
                "command": "pixi run build-test"
            },
            "stages": {
                "stage_01_extract": {
                    "status": "completed",
                    "start_time": "2025-08-10T12:00:00",
                    "end_time": "2025-08-10T12:10:00",
                    "artifacts": ["yfinance_extract.json"]
                },
                "stage_02_transform": {
                    "status": "completed", 
                    "start_time": "2025-08-10T12:10:00",
                    "end_time": "2025-08-10T12:20:00",
                    "artifacts": ["transformed_data.json"]
                },
                "stage_03_load": {
                    "status": "completed",
                    "start_time": "2025-08-10T12:20:00", 
                    "end_time": "2025-08-10T12:30:00",
                    "artifacts": ["graph_nodes.json", "dcf_results.json"]
                }
            },
            "data_partitions": {
                "extract_partition": "20250810",
                "transform_partition": "20250810",
                "load_partition": "20250810"
            },
            "statistics": {
                "files_processed": 1,
                "errors": [],
                "warnings": []
            }
        }
    
    @staticmethod
    def get_m7_tickers() -> List[str]:
        """Magnificent 7 tickers for testing"""
        return ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA", "META", "NFLX"]
    
    @staticmethod
    def get_sample_nasdaq100_tickers() -> List[str]:
        """Sample NASDAQ100 tickers for testing"""
        return [
            "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "COST", "NFLX",
            "AMD", "QCOM", "INTC", "CMCSA", "PEP", "ADBE", "CSCO", "TXN", "HON", "INTU"
        ]
    
    @staticmethod
    def create_sample_config_file(tier: str, output_path: Path) -> None:
        """Create a sample configuration file for testing"""
        config = {
            "data_source": "yfinance",
            "tier": tier,
            "tickers": TestDataFixtures.get_m7_tickers() if tier == "m7" else ["AAPL"],
            "timeframes": {
                "daily": {"period": "3mo", "interval": "1d"},
                "weekly": {"period": "1y", "interval": "1wk"}, 
                "monthly": {"period": "5y", "interval": "1mo"}
            },
            "output_settings": {
                "format": "json",
                "partition_by_date": True,
                "create_symlinks": True
            },
            "validation": {
                "required_fields": ["Open", "High", "Low", "Close", "Volume"],
                "min_data_points": 10
            }
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)

@pytest.fixture
def yfinance_sample_data():
    """Pytest fixture for yfinance data"""
    return TestDataFixtures.sample_yfinance_data()

@pytest.fixture  
def sec_filing_sample():
    """Pytest fixture for SEC filing data"""
    return TestDataFixtures.sample_sec_filing_text()

@pytest.fixture
def build_manifest_sample():
    """Pytest fixture for build manifest"""
    return TestDataFixtures.sample_build_manifest()

@pytest.fixture
def m7_tickers():
    """Pytest fixture for M7 tickers"""
    return TestDataFixtures.get_m7_tickers()

@pytest.fixture
def test_config_paths(tmp_path):
    """Pytest fixture for test configuration paths"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create sample config files
    TestDataFixtures.create_sample_config_file("test", config_dir / "test_config.json")
    TestDataFixtures.create_sample_config_file("m7", config_dir / "m7_config.json")
    
    return {
        "base_path": tmp_path,
        "config_dir": config_dir,
        "test_config": config_dir / "test_config.json",
        "m7_config": config_dir / "m7_config.json"
    }