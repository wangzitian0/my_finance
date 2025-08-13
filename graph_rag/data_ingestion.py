#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Ingestion Pipeline for Graph RAG System

This module handles ingesting M7 data into the Neo4j graph database
with semantic embeddings and proper relationship modeling.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ETL.models import (DCFValuation, DocumentChunk, FastInfo,
                        FinancialMetrics, Info, NewsEvent, PriceData,
                        Recommendations, SECFiling, Stock, Sustainability)

from .semantic_embedding import SemanticEmbedding

logger = logging.getLogger(__name__)


class GraphRAGDataIngestion:
    """
    Handles ingestion of M7 financial data into Neo4j graph database
    with semantic embeddings and relationship creation.
    """

    def __init__(self, semantic_embedding: SemanticEmbedding, data_root: str = "data"):
        """
        Initialize the data ingestion pipeline.

        Args:
            semantic_embedding: SemanticEmbedding instance for generating embeddings
            data_root: Root directory for data files
        """
        self.semantic_embedding = semantic_embedding
        self.data_root = Path(data_root)
        self.original_data_dir = self.data_root / "original"

        # M7 company information
        self.m7_companies = {
            "AAPL": {"name": "Apple Inc.", "cik": "0000320193"},
            "MSFT": {"name": "Microsoft Corporation", "cik": "0000789019"},
            "AMZN": {"name": "Amazon.com Inc.", "cik": "0001018724"},
            "GOOGL": {"name": "Alphabet Inc.", "cik": "0001652044"},
            "META": {"name": "Meta Platforms Inc.", "cik": "0001326801"},
            "TSLA": {"name": "Tesla Inc.", "cik": "0001318605"},
            "NFLX": {"name": "Netflix Inc.", "cik": "0001065280"},
        }

    def ingest_m7_data(self) -> Dict[str, Any]:
        """
        Ingest all M7 company data into the graph database.

        Returns:
            Dictionary with ingestion results and statistics
        """
        logger.info("Starting M7 data ingestion into Graph RAG system")

        ingestion_stats = {
            "companies_processed": 0,
            "stocks_created": 0,
            "filings_processed": 0,
            "embeddings_generated": 0,
            "errors": [],
            "start_time": datetime.now().isoformat(),
        }

        for ticker, company_info in self.m7_companies.items():
            try:
                logger.info(f"Processing {ticker} - {company_info['name']}")

                # Process Yahoo Finance data
                yfinance_stats = self.ingest_yfinance_data(ticker)

                # Process SEC filing data
                sec_stats = self.ingest_sec_data(ticker, company_info["cik"])

                # Update statistics
                ingestion_stats["companies_processed"] += 1
                ingestion_stats["stocks_created"] += yfinance_stats.get("stocks_created", 0)
                ingestion_stats["filings_processed"] += sec_stats.get("filings_processed", 0)
                ingestion_stats["embeddings_generated"] += sec_stats.get("embeddings_generated", 0)

                logger.info(f"Completed processing {ticker}")

            except Exception as e:
                error_msg = f"Error processing {ticker}: {str(e)}"
                logger.error(error_msg)
                ingestion_stats["errors"].append(error_msg)

        ingestion_stats["end_time"] = datetime.now().isoformat()
        logger.info(
            f"M7 data ingestion completed. Processed {ingestion_stats['companies_processed']} companies"
        )

        return ingestion_stats

    def ingest_yfinance_data(self, ticker: str) -> Dict[str, Any]:
        """
        Ingest Yahoo Finance data for a specific ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with ingestion statistics
        """
        stats = {"stocks_created": 0, "records_processed": 0}

        yfinance_dir = self.original_data_dir / "yfinance" / ticker
        if not yfinance_dir.exists():
            logger.warning(f"Yahoo Finance data directory not found for {ticker}: {yfinance_dir}")
            return stats

        try:
            # Find and load the main data file
            data_files = list(yfinance_dir.glob("*.json"))
            if not data_files:
                logger.warning(f"No JSON data files found for {ticker}")
                return stats

            # Use the most recent file
            latest_file = max(data_files, key=lambda x: x.stat().st_mtime)

            with open(latest_file, "r") as f:
                yfinance_data = json.load(f)

            # Create or update Stock node
            stock = self._create_or_update_stock(ticker, yfinance_data)
            if stock:
                stats["stocks_created"] = 1

            # Process company info
            if "info" in yfinance_data:
                self._process_company_info(stock, yfinance_data["info"])
                stats["records_processed"] += 1

            # Process fast info (current market data)
            if "fast_info" in yfinance_data:
                self._process_fast_info(stock, yfinance_data["fast_info"])
                stats["records_processed"] += 1

            # Process historical price data
            if "history" in yfinance_data:
                price_count = self._process_price_data(stock, yfinance_data["history"])
                stats["records_processed"] += price_count

            # Process recommendations
            if "recommendations" in yfinance_data:
                self._process_recommendations(stock, yfinance_data["recommendations"])
                stats["records_processed"] += 1

            # Process sustainability data
            if "sustainability" in yfinance_data:
                self._process_sustainability(stock, yfinance_data["sustainability"])
                stats["records_processed"] += 1

            logger.info(f"Processed {stats['records_processed']} records for {ticker}")

        except Exception as e:
            logger.error(f"Error processing Yahoo Finance data for {ticker}: {e}")
            raise

        return stats

    def ingest_sec_data(self, ticker: str, cik: str) -> Dict[str, Any]:
        """
        Ingest SEC filing data for a specific ticker.

        Args:
            ticker: Stock ticker symbol
            cik: SEC CIK number

        Returns:
            Dictionary with ingestion statistics
        """
        stats = {"filings_processed": 0, "embeddings_generated": 0}

        sec_dir = self.original_data_dir / "sec" / ticker
        if not sec_dir.exists():
            logger.warning(f"SEC data directory not found for {ticker}: {sec_dir}")
            return stats

        try:
            # Find all SEC filing files
            filing_files = list(sec_dir.glob("*.json")) + list(sec_dir.glob("*.txt"))

            for filing_file in filing_files:
                try:
                    filing_stats = self._process_sec_filing(ticker, cik, filing_file)
                    stats["filings_processed"] += filing_stats.get("filings_processed", 0)
                    stats["embeddings_generated"] += filing_stats.get("embeddings_generated", 0)

                except Exception as e:
                    logger.error(f"Error processing SEC filing {filing_file}: {e}")
                    continue

            logger.info(f"Processed {stats['filings_processed']} SEC filings for {ticker}")

        except Exception as e:
            logger.error(f"Error processing SEC data for {ticker}: {e}")
            raise

        return stats

    def _create_or_update_stock(
        self, ticker: str, yfinance_data: Dict[str, Any]
    ) -> Optional[Stock]:
        """Create or update Stock node."""
        try:
            # Try to find existing stock
            stock = Stock.nodes.get_or_none(ticker=ticker)

            if stock is None:
                # Create new stock
                stock = Stock(
                    ticker=ticker,
                    period=yfinance_data.get("period", "1y"),
                    interval=yfinance_data.get("interval", "1d"),
                    fetched_at=datetime.now(),
                )
                stock.save()
                logger.debug(f"Created new Stock node for {ticker}")
            else:
                # Update existing stock
                stock.fetched_at = datetime.now()
                stock.save()
                logger.debug(f"Updated existing Stock node for {ticker}")

            return stock

        except Exception as e:
            logger.error(f"Error creating/updating Stock node for {ticker}: {e}")
            return None

    def _process_company_info(self, stock: Stock, info_data: Dict[str, Any]):
        """Process and store company information."""
        try:
            # Create or update Info node
            info = Info(
                address1=info_data.get("address1"),
                city=info_data.get("city"),
                state=info_data.get("state"),
                zip=info_data.get("zip"),
                country=info_data.get("country"),
                phone=info_data.get("phone"),
                website=info_data.get("website"),
                industry=info_data.get("industry"),
                industryKey=info_data.get("industryKey"),
                industryDisp=info_data.get("industryDisp"),
                sector=info_data.get("sector"),
                sectorKey=info_data.get("sectorKey"),
                sectorDisp=info_data.get("sectorDisp"),
                longBusinessSummary=info_data.get("longBusinessSummary"),
                fullTimeEmployees=info_data.get("fullTimeEmployees"),
                companyOfficers=info_data.get("companyOfficers", []),
            )
            info.save()

            # Create relationship
            stock.info.connect(info)

            logger.debug(f"Processed company info for {stock.ticker}")

        except Exception as e:
            logger.error(f"Error processing company info for {stock.ticker}: {e}")

    def _process_fast_info(self, stock: Stock, fast_info_data: Dict[str, Any]):
        """Process and store fast info (current market data)."""
        try:
            fast_info = FastInfo(
                currency=fast_info_data.get("currency"),
                dayHigh=fast_info_data.get("dayHigh"),
                dayLow=fast_info_data.get("dayLow"),
                exchange=fast_info_data.get("exchange"),
                fiftyDayAverage=fast_info_data.get("fiftyDayAverage"),
                lastPrice=fast_info_data.get("lastPrice"),
                lastVolume=fast_info_data.get("lastVolume"),
            )
            fast_info.save()

            stock.fast_info.connect(fast_info)

            logger.debug(f"Processed fast info for {stock.ticker}")

        except Exception as e:
            logger.error(f"Error processing fast info for {stock.ticker}: {e}")

    def _process_price_data(self, stock: Stock, history_data: Dict[str, Any]) -> int:
        """Process and store historical price data."""
        processed_count = 0

        try:
            # History data typically contains dates as keys with OHLCV data
            for date_str, price_info in history_data.items():
                try:
                    price_date = datetime.strptime(date_str, "%Y-%m-%d")

                    price_data = PriceData(
                        date=price_date,
                        open=price_info.get("Open"),
                        high=price_info.get("High"),
                        low=price_info.get("Low"),
                        close=price_info.get("Close"),
                        volume=price_info.get("Volume"),
                    )
                    price_data.save()

                    stock.prices.connect(price_data)
                    processed_count += 1

                except Exception as e:
                    logger.warning(
                        f"Error processing price data for {stock.ticker} on {date_str}: {e}"
                    )
                    continue

            logger.debug(f"Processed {processed_count} price records for {stock.ticker}")

        except Exception as e:
            logger.error(f"Error processing price history for {stock.ticker}: {e}")

        return processed_count

    def _process_recommendations(self, stock: Stock, recommendations_data: Dict[str, Any]):
        """Process and store analyst recommendations."""
        try:
            recommendations = Recommendations(
                period=recommendations_data.get("period", {}),
                strongBuy=recommendations_data.get("strongBuy", {}),
                buy=recommendations_data.get("buy", {}),
                hold=recommendations_data.get("hold", {}),
                sell=recommendations_data.get("sell", {}),
                strongSell=recommendations_data.get("strongSell", {}),
            )
            recommendations.save()

            stock.recommendations.connect(recommendations)

            logger.debug(f"Processed recommendations for {stock.ticker}")

        except Exception as e:
            logger.error(f"Error processing recommendations for {stock.ticker}: {e}")

    def _process_sustainability(self, stock: Stock, sustainability_data: Dict[str, Any]):
        """Process and store ESG/sustainability data."""
        try:
            sustainability = Sustainability(esgScores=sustainability_data)
            sustainability.save()

            stock.sustainability.connect(sustainability)

            logger.debug(f"Processed sustainability data for {stock.ticker}")

        except Exception as e:
            logger.error(f"Error processing sustainability data for {stock.ticker}: {e}")

    def _process_sec_filing(self, ticker: str, cik: str, filing_file: Path) -> Dict[str, Any]:
        """Process a single SEC filing file."""
        stats = {"filings_processed": 0, "embeddings_generated": 0}

        try:
            # Determine filing type from filename
            filing_type = self._extract_filing_type(filing_file.name)

            # Load and parse filing content
            if filing_file.suffix == ".json":
                with open(filing_file, "r") as f:
                    filing_data = json.load(f)
            else:
                with open(filing_file, "r", encoding="utf-8") as f:
                    filing_content = f.read()
                    filing_data = {"raw_content": filing_content}

            # Create SEC filing node
            sec_filing = self._create_sec_filing_node(
                ticker, cik, filing_type, filing_data, filing_file
            )

            if sec_filing:
                stats["filings_processed"] = 1

                # Generate semantic embeddings for sections
                embedding_count = self._generate_filing_embeddings(sec_filing, filing_data)
                stats["embeddings_generated"] = embedding_count

                # Connect to stock
                stock = Stock.nodes.get_or_none(ticker=ticker)
                if stock:
                    stock.filings.connect(sec_filing)

        except Exception as e:
            logger.error(f"Error processing SEC filing {filing_file}: {e}")
            raise

        return stats

    def _extract_filing_type(self, filename: str) -> str:
        """Extract filing type from filename."""
        filename_lower = filename.lower()

        if "10-k" in filename_lower:
            return "10-K"
        elif "10-q" in filename_lower:
            return "10-Q"
        elif "8-k" in filename_lower:
            return "8-K"
        else:
            return "Unknown"

    def _create_sec_filing_node(
        self,
        ticker: str,
        cik: str,
        filing_type: str,
        filing_data: Dict[str, Any],
        filing_file: Path,
    ) -> Optional[SECFiling]:
        """Create SEC filing node in the graph."""
        try:
            # Extract filing metadata
            filing_date = filing_data.get("filing_date")
            if filing_date and isinstance(filing_date, str):
                filing_date = datetime.strptime(filing_date, "%Y-%m-%d")
            else:
                # Use file modification time as fallback
                filing_date = datetime.fromtimestamp(filing_file.stat().st_mtime)

            # Generate unique accession number
            accession_number = filing_data.get(
                "accession_number",
                f"{cik}-{filing_type}-{filing_date.strftime('%Y%m%d')}",
            )

            # Create SEC filing node
            sec_filing = SECFiling(
                filing_type=filing_type,
                filing_date=filing_date,
                cik=cik,
                accession_number=accession_number,
                document_url=filing_data.get("document_url"),
                business_overview=filing_data.get("business_overview", ""),
                risk_factors=filing_data.get("risk_factors", ""),
                financial_statements=filing_data.get("financial_statements", ""),
                md_and_a=filing_data.get("md_and_a", ""),
                raw_content=filing_data.get("raw_content", ""),
                processed_at=datetime.now(),
                parsing_success=bool(
                    filing_data.get("business_overview") or filing_data.get("raw_content")
                ),
            )

            sec_filing.save()

            logger.debug(f"Created SEC filing {filing_type} for {ticker}")
            return sec_filing

        except Exception as e:
            logger.error(f"Error creating SEC filing node for {ticker}: {e}")
            return None

    def _generate_filing_embeddings(
        self, sec_filing: SECFiling, filing_data: Dict[str, Any]
    ) -> int:
        """Generate semantic embeddings for SEC filing sections."""
        embeddings_generated = 0

        if not self.semantic_embedding.model:
            logger.warning("Semantic embedding model not available")
            return 0

        try:
            # Generate embeddings for each section
            sections = {
                "business_overview": sec_filing.business_overview,
                "risk_factors": sec_filing.risk_factors,
                "financial_statements": sec_filing.financial_statements,
                "md_and_a": sec_filing.md_and_a,
            }

            for section_name, content in sections.items():
                if content and content.strip():
                    embedding = self.semantic_embedding.embed_text(content)
                    if embedding:
                        # Store embedding in the appropriate field
                        embedding_field = f"{section_name}_embedding"
                        setattr(sec_filing, embedding_field, embedding)
                        embeddings_generated += 1

            # Save updated embeddings
            sec_filing.save()

            logger.debug(
                f"Generated {embeddings_generated} embeddings for SEC filing {sec_filing.accession_number}"
            )

        except Exception as e:
            logger.error(f"Error generating embeddings for SEC filing: {e}")

        return embeddings_generated

    def create_sample_dcf_valuations(self) -> Dict[str, Any]:
        """Create sample DCF valuation data for M7 companies."""
        stats = {"valuations_created": 0}

        # Sample DCF data for demonstration
        sample_dcf_data = {
            "AAPL": {
                "intrinsic_value": 185.50,
                "current_price": 175.25,
                "wacc": 8.5,
                "terminal_growth_rate": 2.5,
                "bankruptcy_probability": 0.1,
            },
            "MSFT": {
                "intrinsic_value": 420.00,
                "current_price": 410.15,
                "wacc": 7.8,
                "terminal_growth_rate": 2.8,
                "bankruptcy_probability": 0.05,
            },
            "GOOGL": {
                "intrinsic_value": 145.20,
                "current_price": 138.75,
                "wacc": 9.1,
                "terminal_growth_rate": 3.0,
                "bankruptcy_probability": 0.08,
            },
        }

        for ticker, dcf_data in sample_dcf_data.items():
            try:
                stock = Stock.nodes.get_or_none(ticker=ticker)
                if stock:
                    upside_downside = (
                        dcf_data["intrinsic_value"] - dcf_data["current_price"]
                    ) / dcf_data["current_price"]

                    dcf_valuation = DCFValuation(
                        valuation_date=datetime.now(),
                        intrinsic_value=dcf_data["intrinsic_value"],
                        current_price=dcf_data["current_price"],
                        upside_downside=upside_downside,
                        wacc=dcf_data["wacc"],
                        terminal_growth_rate=dcf_data["terminal_growth_rate"],
                        bankruptcy_probability=dcf_data["bankruptcy_probability"],
                        confidence_score=0.75,
                        data_quality_score=0.8,
                    )
                    dcf_valuation.save()

                    stock.valuations.connect(dcf_valuation)
                    stats["valuations_created"] += 1

                    logger.debug(f"Created DCF valuation for {ticker}")

            except Exception as e:
                logger.error(f"Error creating DCF valuation for {ticker}: {e}")

        return stats
