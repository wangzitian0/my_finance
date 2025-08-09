#!/usr/bin/env python3
"""
Fetch latest ticker lists from official websites
Updates NASDAQ100 and VTI configurations with current holdings
"""

import json
import logging
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fetch_nasdaq100_tickers() -> List[str]:
    """
    Fetch NASDAQ-100 index constituents from multiple sources
    Returns list of ticker symbols
    """
    try:
        logger.info("Fetching NASDAQ-100 constituents...")

        # Use the official NASDAQ API
        try:
            logger.info("Fetching from official NASDAQ API...")

            headers = {
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
                "dnt": "1",
                "origin": "https://www.nasdaq.com",
                "priority": "u=1, i",
                "referer": "https://www.nasdaq.com/",
                "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            }

            api_url = "https://api.nasdaq.com/api/quote/list-type/nasdaq100"
            req = urllib.request.Request(api_url, headers=headers)
            response = urllib.request.urlopen(req, timeout=30)
            data = json.loads(response.read().decode())

            if (
                "data" in data
                and "data" in data["data"]
                and "rows" in data["data"]["data"]
            ):
                ticker_data = []
                for row in data["data"]["data"]["rows"]:
                    ticker_info = {
                        "symbol": row["symbol"],
                        "name": row.get("companyName", ""),
                        "market_cap": row.get("marketCap", ""),
                        "sector": row.get("sector", ""),
                        "last_price": row.get("lastSalePrice", ""),
                        "change": row.get("netChange", ""),
                        "change_pct": row.get("percentageChange", ""),
                    }
                    ticker_data.append(ticker_info)
                logger.info(
                    f"Successfully fetched {len(ticker_data)} tickers from NASDAQ API"
                )
                return ticker_data
            else:
                logger.warning("Unexpected API response format")

        except Exception as e:
            logger.warning(f"NASDAQ API failed: {e}")

        # If web scraping fails, try yfinance to get QQQ holdings
        try:
            logger.info("Trying yfinance for QQQ (NASDAQ-100 ETF) holdings...")
            import yfinance as yf

            # QQQ tracks NASDAQ-100, get its holdings if possible
            qqq = yf.Ticker("QQQ")

            # If we can't get holdings directly, use major NASDAQ components
            logger.info("Using major NASDAQ-100 components via yfinance validation...")

            # Major known NASDAQ-100 components - validate they exist
            potential_tickers = [
                "AAPL",
                "MSFT",
                "GOOGL",
                "GOOG",
                "AMZN",
                "NVDA",
                "META",
                "TSLA",
                "AVGO",
                "ORCL",
                "COST",
                "NFLX",
                "CSCO",
                "ADBE",
                "AMD",
                "PEP",
                "LIN",
                "TMUS",
                "ISRG",
                "INTU",
                "TXN",
                "QCOM",
                "CMCSA",
                "BKNG",
                "HON",
                "AMGN",
                "AMAT",
                "ADP",
                "SBUX",
                "GILD",
                "ADI",
                "KLAC",
                "LRCX",
                "MDLZ",
                "MELI",
                "SNPS",
                "CDNS",
                "REGN",
                "CSX",
                "ORLY",
                "MU",
                "CTAS",
                "INTC",
                "VRTX",
                "PYPL",
                "PDD",
                "ABNB",
                "WDAY",
                "FTNT",
                "DASH",
                "TEAM",
                "DDOG",
                "FAST",
                "IDXX",
                "MAR",
                "MNST",
                "ADSK",
                "AEP",
                "ROP",
                "NXPI",
                "PCAR",
                "PAYX",
                "ROST",
                "KDP",
                "EXC",
                "CPRT",
                "XEL",
                "CCEP",
                "BKR",
                "ZS",
                "EA",
                "FANG",
                "TTWO",
                "CSGP",
                "CRWD",
                "CEG",
                "PANW",
                "MRVL",
                "AXON",
                "APP",
                "ARM",
                "MSTR",
                "ASML",
                "WBD",
                "BIIB",
                "MRNA",
                "DLTR",
                "LULU",
            ]

            # Validate tickers exist by trying to fetch basic info
            valid_tickers = []
            for ticker in potential_tickers:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    if info and "symbol" in info:
                        valid_tickers.append(ticker)
                        if len(valid_tickers) >= 102:  # NASDAQ-100 can be ~102 stocks
                            break
                except:
                    continue

            if len(valid_tickers) > 80:
                logger.info(
                    f"Successfully validated {len(valid_tickers)} NASDAQ-100 tickers via yfinance"
                )
                return valid_tickers

        except Exception as yf_error:
            logger.warning(f"yfinance fallback failed: {yf_error}")

        # If everything fails, raise an error
        raise Exception("All NASDAQ-100 data sources failed")

    except Exception as e:
        logger.error(f"Error fetching NASDAQ-100 tickers: {e}")
        raise


def fetch_vti_holdings() -> List[str]:
    """
    Fetch VTI top holdings from Vanguard website
    Returns list of ticker symbols for top holdings plus VTI itself
    """
    try:
        logger.info("Fetching VTI top holdings from Vanguard...")

        # Use the official Vanguard API for VTI holdings
        try:
            logger.info("Fetching from official Vanguard API...")

            headers = {
                "sec-ch-ua-platform": '"macOS"',
                "X-XSRF-TOKEN": "3Uj5uOKb-0piWT7J8_pcohPXC7hWWxy1kNPE",
                "Referer": "https://advisors.vanguard.com/investments/products/vti/vanguard-total-stock-market-etf",
                "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138"',
                "sec-ch-ua-mobile": "?0",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "DNT": "1",
            }

            api_url = "https://advisors.vanguard.com/investments/products/holdings/latest/0970"
            req = urllib.request.Request(api_url, headers=headers)
            response = urllib.request.urlopen(req, timeout=30)
            data = json.loads(response.read().decode())

            # Extract tickers from the response with metadata
            ticker_data = [
                {
                    "symbol": "VTI",
                    "name": "Vanguard Total Stock Market ETF",
                    "weight": "100%",
                    "sector": "ETF",
                }
            ]

            # Find the latest date and get holdings
            if "latestEffectiveDate" in data:
                latest_date = data["latestEffectiveDate"]
                if latest_date in data and "equity" in data[latest_date]:
                    holdings = data[latest_date]["equity"]
                    existing_symbols = set(["VTI"])

                    for holding in holdings:
                        if "ticker" in holding and holding["ticker"]:
                            ticker = holding["ticker"].strip().upper()
                            # Handle special cases like BRK/B -> BRK.B
                            if "/" in ticker:
                                ticker = ticker.replace("/", ".")

                            # Filter valid tickers
                            if (
                                2 <= len(ticker.split(".")[0]) <= 5
                                and ticker.split(".")[0].isalpha()
                                and ticker not in existing_symbols
                            ):  # Avoid duplicates

                                # Get percentage as float for formatting
                                percent = holding.get("percentOfFunds", 0)
                                if isinstance(percent, str):
                                    try:
                                        percent = float(percent)
                                    except:
                                        percent = 0

                                ticker_info = {
                                    "symbol": ticker,
                                    "name": holding.get("holdingName", ""),
                                    "weight": f"{percent:.4f}%",
                                    "sector": holding.get("sector", ""),
                                    "market_value": holding.get("marketValue", ""),
                                    "quantity": holding.get("quantity", ""),
                                }
                                ticker_data.append(ticker_info)
                                existing_symbols.add(ticker)

                    logger.info(
                        f"Successfully fetched {len(ticker_data)} tickers from Vanguard API (including VTI)"
                    )
                    return ticker_data  # Return all tickers for complete accuracy

            logger.warning("Unexpected Vanguard API response format")

        except Exception as e:
            logger.warning(f"Vanguard API failed: {e}")

        # If web scraping fails, get broader US market representation
        try:
            logger.info("Building comprehensive VTI representation...")

            # Start with VTI ETF itself
            holdings = ["VTI"]

            # Top 100+ holdings by market cap (VTI represents total stock market)
            market_components = [
                # Mega caps (top 50 by market cap)
                "AAPL",
                "MSFT",
                "NVDA",
                "GOOGL",
                "GOOG",
                "AMZN",
                "META",
                "TSLA",
                "AVGO",
                "BRK.B",
                "JPM",
                "LLY",
                "V",
                "UNH",
                "MA",
                "HD",
                "PG",
                "JNJ",
                "COST",
                "ABBV",
                "XOM",
                "BAC",
                "ORCL",
                "CVX",
                "KO",
                "AMD",
                "MRK",
                "TMUS",
                "PEP",
                "WFC",
                "LIN",
                "ABT",
                "CSCO",
                "PM",
                "TXN",
                "IBM",
                "CRM",
                "DIS",
                "INTU",
                "CAT",
                "GE",
                "QCOM",
                "AMAT",
                "BKNG",
                "AXP",
                "GS",
                "MS",
                "RTX",
                "ISRG",
                "HON",
                # Large caps (next 100)
                "NOW",
                "AMGN",
                "T",
                "SPGI",
                "MU",
                "SYK",
                "NEE",
                "PFE",
                "BSX",
                "C",
                "LRCX",
                "LOW",
                "TMO",
                "ACN",
                "TJX",
                "MDT",
                "UNP",
                "ADBE",
                "DE",
                "ETN",
                "SCHW",
                "CB",
                "LMT",
                "BLK",
                "DHR",
                "PGR",
                "GILD",
                "BA",
                "ADP",
                "FI",
                "VRTX",
                "ADI",
                "KLAC",
                "SO",
                "REGN",
                "APH",
                "UBER",
                "CI",
                "DUK",
                "PANW",
                "CME",
                "KKR",
                "SHW",
                "COP",
                "MMC",
                "USB",
                "PLD",
                "ICE",
                "GD",
                "WM",
                "AON",
                "TT",
                "APO",
                "AMT",
                "HUM",
                "MO",
                "ITW",
                "EMR",
                "TGT",
                "WMT",
                "SBUX",
                "NFLX",
                "ADSK",
                "PYPL",
                "CRWD",
                "ZTS",
                "BMY",
                "ELV",
                "COIN",
                "SHOP",
                # Mid caps and key sector representatives
                "F",
                "GM",
                "INTC",
                "DELL",
                "HPE",
                "HPQ",
                "EBAY",
                "ETSY",
                "SQ",
                "TWLO",
                "SNOW",
                "NET",
                "DDOG",
                "ZM",
                "DOCU",
                "OKTA",
                "PLTR",
                "RBLX",
                "U",
                "PATH",
                "RIVN",
                "LCID",
                "FSLY",
                "PINS",
                "SNAP",
                "TWTR",
                "ROKU",
                "SPOT",
                "ZI",
                "WORK",
                # Financial sector
                "WFC",
                "COF",
                "AIG",
                "PRU",
                "MET",
                "ALL",
                "TRV",
                "AFL",
                "AMP",
                "PNC",
                "USB",
                "TFC",
                "COF",
                "STT",
                "BK",
                "NTRS",
                "RF",
                "FITB",
                "KEY",
                "CFG",
                # Healthcare & Biotech
                "UNH",
                "JNJ",
                "PFE",
                "ABBV",
                "MRK",
                "TMO",
                "ABT",
                "DHR",
                "BMY",
                "AMGN",
                "GILD",
                "REGN",
                "VRTX",
                "BIIB",
                "CELG",
                "ILMN",
                "MRNA",
                "BNTX",
                "ZTS",
                "ELV",
                # Energy
                "XOM",
                "CVX",
                "COP",
                "EOG",
                "SLB",
                "PXD",
                "KMI",
                "OKE",
                "MPC",
                "VLO",
                "PSX",
                "BKR",
                "HAL",
                "DVN",
                "FANG",
                "APA",
                "EQT",
                "CNX",
                "AR",
                "SM",
                # Consumer
                "AMZN",
                "TSLA",
                "HD",
                "LOW",
                "TGT",
                "WMT",
                "COST",
                "TJX",
                "NKE",
                "SBUX",
                "MCD",
                "BKNG",
                "ABNB",
                "UBER",
                "LYFT",
                "DRI",
                "YUM",
                "CMG",
                "LULU",
                "RH",
                # Industrials
                "BA",
                "CAT",
                "DE",
                "HON",
                "RTX",
                "LMT",
                "GD",
                "NOC",
                "ETN",
                "EMR",
                "MMM",
                "GE",
                "ITW",
                "PH",
                "CMI",
                "FDX",
                "UPS",
                "LUV",
                "DAL",
                "UAL",
                # REITs
                "AMT",
                "PLD",
                "CCI",
                "EQIX",
                "PSA",
                "EXR",
                "AVB",
                "EQR",
                "VTR",
                "ARE",
                # Utilities
                "NEE",
                "DUK",
                "SO",
                "D",
                "EXC",
                "AEP",
                "XEL",
                "SRE",
                "PEG",
                "ED",
            ]

            holdings.extend(market_components)

            # Remove duplicates while preserving VTI at the front
            unique_holdings = ["VTI"] + list(dict.fromkeys(market_components))

            logger.info(
                f"Built comprehensive VTI representation: {len(unique_holdings)} tickers"
            )
            return unique_holdings

        except Exception as build_error:
            logger.warning(f"Building comprehensive VTI failed: {build_error}")

        # If everything fails, raise an error
        raise Exception("All VTI holdings sources failed")

    except Exception as e:
        logger.error(f"Error fetching VTI holdings: {e}")
        raise


def update_config_file(config_path: Path, tickers_data: List, description: str):
    """Update configuration file with new ticker list and metadata comments for new modular format"""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Update description
        if "description" in config:
            config["description"] = description

        # Determine if we have metadata or just ticker symbols
        has_metadata = tickers_data and isinstance(tickers_data[0], dict)

        # Update companies section for new modular format
        companies = {}
        
        if has_metadata:
            for ticker_info in tickers_data:
                symbol = ticker_info["symbol"]
                companies[symbol] = {
                    "name": ticker_info.get("name", f"{symbol} Inc."),
                    "sector": ticker_info.get("sector", "Technology"),
                }
                
                # Add weight for VTI holdings
                if ticker_info.get("weight") and ticker_info["weight"] != "0.0000%":
                    companies[symbol]["weight"] = ticker_info["weight"]
                
                # Add market cap for NASDAQ data  
                if ticker_info.get("market_cap"):
                    companies[symbol]["market_cap"] = ticker_info["market_cap"]
                
                # Add CIK if available
                if ticker_info.get("cik"):
                    companies[symbol]["cik"] = ticker_info["cik"]
                    
            ticker_count = len(tickers_data)
        else:
            for ticker in tickers_data:
                companies[ticker] = {
                    "name": f"{ticker} Inc.",
                    "sector": "Technology"
                }
            ticker_count = len(tickers_data)

        config["companies"] = companies
        config["ticker_count"] = ticker_count
        
        # Update expected files count based on data sources
        if "expected_files" in config:
            yf_periods = len(config.get("data_sources", {}).get("yfinance", {}).get("periods", ["daily_3mo", "weekly_5y", "monthly_max"]))
            config["expected_files"]["yfinance"] = ticker_count * yf_periods

        # Add last updated timestamp
        from datetime import datetime
        config["last_updated"] = datetime.now().isoformat()

        # Write updated config
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Updated {config_path} with {ticker_count} tickers")

    except Exception as e:
        logger.error(f"Error updating {config_path}: {e}")


def main():
    """Main function to update all ticker lists with new modular config format"""
    base_path = Path(__file__).parent.parent / "data" / "config"

    try:
        # Update NASDAQ-100
        logger.info("=== Fetching NASDAQ-100 tickers ===")
        nasdaq100_tickers = fetch_nasdaq100_tickers()
        update_config_file(
            base_path / "list_nasdaq_100.yml",
            nasdaq100_tickers,
            "NASDAQ-100 index companies - validation dataset",
        )

        # Update VTI 3500
        logger.info("=== Fetching VTI holdings ===")
        vti_tickers = fetch_vti_holdings()
        update_config_file(
            base_path / "list_vti_3500.yml",
            vti_tickers,
            f"VTI ETF holdings ({len(vti_tickers) if vti_tickers else 0} companies) - production dataset",
        )

        logger.info("=== Ticker list update complete ===")

    except Exception as e:
        logger.error(f"Failed to update ticker lists: {e}")
        raise


if __name__ == "__main__":
    main()
