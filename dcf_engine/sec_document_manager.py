#!/usr/bin/env python3
"""
SEC Document Manager for DCF Analysis
Manages SEC filings, builds embeddings, and provides document search capabilities
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class SECDocumentManager:
    def __init__(self, base_path: str = None):
        if base_path is None:
            # Use project root relative path
            project_root = Path(__file__).parent.parent
            base_path = project_root / "data"

        # Use SSOT DirectoryManager for consistent path management
        from common.core.directory_manager import DirectoryManager, DataLayer

        dm = DirectoryManager()
        
        # SEC documents go to raw data layer
        raw_data_path = dm.get_data_layer_path(DataLayer.RAW_DATA)
        self.base_path = raw_data_path
        self.sec_docs_path = raw_data_path / "sec-edgar"  # Use stage_00_raw/sec-edgar
        
        # Embeddings go to daily index layer
        daily_index_path = dm.get_data_layer_path(DataLayer.DAILY_INDEX)
        self.embeddings_path = daily_index_path / "embeddings"

        # Create directories
        self.sec_docs_path.mkdir(parents=True, exist_ok=True)
        self.embeddings_path.mkdir(parents=True, exist_ok=True)

        # SEC API settings
        self.sec_base_url = "https://data.sec.gov"
        self.headers = {
            "User-Agent": "my-finance-dcf-analysis research@example.com",
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov",
        }

        # Rate limiting (SEC allows 10 requests per second)
        self.request_delay = 0.1
        self.last_request_time = 0

    def _rate_limit(self):
        """Enforce SEC API rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()

    def get_company_cik(self, ticker: str) -> Optional[str]:
        """Get CIK (Central Index Key) for a company ticker"""
        # Hardcoded M7 CIKs for demo (in production, would fetch from SEC API)
        m7_ciks = {
            "AAPL": "0000320193",
            "MSFT": "0000789019",
            "GOOGL": "0001652044",
            "AMZN": "0001018724",
            "TSLA": "0001318605",
            "META": "0001326801",
            "NVDA": "0001045810",
        }

        cik = m7_ciks.get(ticker.upper())
        if cik:
            logger.info(f"Found CIK for {ticker}: {cik}")
            return cik
        else:
            logger.warning(f"CIK not found for ticker: {ticker}")
            return None

    def fetch_recent_filings(
        self, ticker: str, filing_types: List[str] = None, limit: int = 10
    ) -> List[Dict]:
        """Fetch recent SEC filings for a company"""
        if filing_types is None:
            filing_types = ["10-K", "10-Q", "8-K"]

        cik = self.get_company_cik(ticker)
        if not cik:
            return []

        try:
            self._rate_limit()

            # Get recent filings
            url = f"{self.sec_base_url}/submissions/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            filings = data.get("filings", {}).get("recent", {})

            if not filings:
                return []

            # Process filings
            recent_filings = []
            forms = filings.get("form", [])
            filing_dates = filings.get("filingDate", [])
            accession_numbers = filings.get("accessionNumber", [])

            for i, form in enumerate(forms[: limit * 3]):  # Get more to filter
                if form in filing_types and len(recent_filings) < limit:
                    filing_info = {
                        "ticker": ticker,
                        "cik": cik,
                        "form": form,
                        "filing_date": filing_dates[i] if i < len(filing_dates) else None,
                        "accession_number": (
                            accession_numbers[i] if i < len(accession_numbers) else None
                        ),
                    }
                    recent_filings.append(filing_info)

            return recent_filings

        except Exception as e:
            logger.error(f"Error fetching filings for {ticker}: {e}")
            return []

    def download_filing(self, filing_info: Dict) -> Optional[str]:
        """Download a specific filing document"""
        try:
            ticker = filing_info["ticker"]
            accession = filing_info["accession_number"].replace("-", "")
            form = filing_info["form"]
            filing_date = filing_info["filing_date"]

            # Create filing directory
            filing_dir = self.sec_docs_path / ticker / form / filing_date
            filing_dir.mkdir(parents=True, exist_ok=True)

            # Download primary document
            self._rate_limit()

            # Construct document URL
            doc_url = f"{self.sec_base_url}/Archives/edgar/data/{filing_info['cik']}/{accession}/{accession}.txt"

            response = requests.get(doc_url, headers=self.headers)
            response.raise_for_status()

            # Save document
            doc_path = filing_dir / f"{form}_{filing_date}.txt"
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(response.text)

            # Save metadata
            metadata_path = filing_dir / "metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(filing_info, f, indent=2)

            logger.info(f"Downloaded {form} for {ticker} ({filing_date})")
            return str(doc_path)

        except Exception as e:
            logger.error(f"Error downloading filing: {e}")
            return None

    def build_sec_library(self, tickers: List[str]) -> Dict[str, Any]:
        """Build SEC document library for DCF analysis"""
        logger.info(f"Building SEC library for {len(tickers)} companies...")

        library_stats = {
            "companies": len(tickers),
            "total_filings": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "by_ticker": {},
        }

        for ticker in tickers:
            print(f"📄 Processing SEC filings for {ticker}...")

            ticker_stats = {"filings_found": 0, "downloads_successful": 0, "downloads_failed": 0}

            # Get recent filings
            filings = self.fetch_recent_filings(ticker, limit=5)  # Get last 5 filings
            ticker_stats["filings_found"] = len(filings)
            library_stats["total_filings"] += len(filings)

            # Download filings
            for filing in filings:
                doc_path = self.download_filing(filing)
                if doc_path:
                    ticker_stats["downloads_successful"] += 1
                    library_stats["successful_downloads"] += 1
                else:
                    ticker_stats["downloads_failed"] += 1
                    library_stats["failed_downloads"] += 1

                # Rate limiting between downloads
                time.sleep(0.2)

            library_stats["by_ticker"][ticker] = ticker_stats
            print(f"   ✅ {ticker}: {ticker_stats['downloads_successful']} filings downloaded")

            # Delay between companies
            time.sleep(1)

        return library_stats

    def generate_embeddings(self, use_ollama: bool = True) -> Dict[str, Any]:
        """Generate embeddings for SEC documents using Ollama or fallback"""
        logger.info("Generating embeddings for SEC documents...")

        if use_ollama:
            return self._generate_ollama_embeddings()
        else:
            return self._generate_simple_embeddings()

    def _generate_ollama_embeddings(self) -> Dict[str, Any]:
        """Generate embeddings using Ollama nomic-embed-text model"""
        try:
            import requests

            # Check if Ollama is running
            ollama_url = "http://localhost:11434"

            try:
                response = requests.get(f"{ollama_url}/api/tags", timeout=5)
                if response.status_code != 200:
                    raise ConnectionError("Ollama not responding")
            except:
                logger.warning("Ollama not available, falling back to simple embeddings")
                return self._generate_simple_embeddings()

            embedding_stats = {
                "documents_processed": 0,
                "embeddings_created": 0,
                "errors": 0,
                "model": "nomic-embed-text",
            }

            # Process all SEC documents
            for ticker_dir in self.sec_docs_path.iterdir():
                if not ticker_dir.is_dir():
                    continue

                ticker = ticker_dir.name
                print(f"🔍 Generating embeddings for {ticker}...")

                for doc_file in ticker_dir.rglob("*.txt"):
                    try:
                        # Read document content
                        with open(doc_file, "r", encoding="utf-8") as f:
                            content = f.read()

                        # Truncate if too long (Ollama has limits)
                        content = content[:8000]  # ~8k chars

                        # Generate embedding
                        embed_request = {"model": "nomic-embed-text", "prompt": content}

                        response = requests.post(
                            f"{ollama_url}/api/embeddings", json=embed_request, timeout=30
                        )

                        if response.status_code == 200:
                            embedding_data = response.json()

                            # Save embedding
                            embed_file = self.embeddings_path / f"{ticker}_{doc_file.stem}.json"
                            with open(embed_file, "w") as f:
                                json.dump(
                                    {
                                        "document": str(doc_file),
                                        "ticker": ticker,
                                        "embedding": embedding_data.get("embedding", []),
                                        "created_at": datetime.now().isoformat(),
                                        "model": "nomic-embed-text",
                                    },
                                    f,
                                )

                            embedding_stats["embeddings_created"] += 1

                        embedding_stats["documents_processed"] += 1

                    except Exception as e:
                        logger.error(f"Error processing {doc_file}: {e}")
                        embedding_stats["errors"] += 1

                    # Rate limiting
                    time.sleep(0.5)

            return embedding_stats

        except Exception as e:
            logger.error(f"Error in Ollama embeddings: {e}")
            return self._generate_simple_embeddings()

    def _generate_simple_embeddings(self) -> Dict[str, Any]:
        """Generate simple text-based embeddings as fallback"""
        logger.info("Generating simple embeddings (fallback)...")

        embedding_stats = {
            "documents_processed": 0,
            "embeddings_created": 0,
            "errors": 0,
            "model": "simple-text-hash",
        }

        # Simple hash-based embeddings for testing
        for ticker_dir in self.sec_docs_path.iterdir():
            if not ticker_dir.is_dir():
                continue

            ticker = ticker_dir.name

            for doc_file in ticker_dir.rglob("*.txt"):
                try:
                    # Read and hash content
                    with open(doc_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Simple embedding based on content hash and length
                    simple_embedding = [
                        hash(content) % 1000,
                        len(content) % 1000,
                        content.count("revenue") % 100,
                        content.count("profit") % 100,
                        content.count("cash") % 100,
                    ]

                    # Save simple embedding
                    embed_file = self.embeddings_path / f"{ticker}_{doc_file.stem}_simple.json"
                    with open(embed_file, "w") as f:
                        json.dump(
                            {
                                "document": str(doc_file),
                                "ticker": ticker,
                                "embedding": simple_embedding,
                                "created_at": datetime.now().isoformat(),
                                "model": "simple-text-hash",
                            },
                            f,
                        )

                    embedding_stats["embeddings_created"] += 1
                    embedding_stats["documents_processed"] += 1

                except Exception as e:
                    logger.error(f"Error in simple embedding for {doc_file}: {e}")
                    embedding_stats["errors"] += 1

        return embedding_stats


def main():
    """Main function for testing SEC document manager"""
    manager = SECDocumentManager()

    # Test with M7 companies
    m7_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]

    print("🏢 Building SEC Document Library for M7 companies...")
    library_stats = manager.build_sec_library(m7_tickers)

    print(f"\n📊 Library Statistics:")
    print(f"   Companies processed: {library_stats['companies']}")
    print(f"   Total filings found: {library_stats['total_filings']}")
    print(f"   Successful downloads: {library_stats['successful_downloads']}")
    print(f"   Failed downloads: {library_stats['failed_downloads']}")

    print(f"\n🔍 Generating embeddings...")
    embed_stats = manager.generate_embeddings()

    print(f"📈 Embedding Statistics:")
    print(f"   Documents processed: {embed_stats['documents_processed']}")
    print(f"   Embeddings created: {embed_stats['embeddings_created']}")
    print(f"   Model used: {embed_stats['model']}")
    print(f"   Errors: {embed_stats['errors']}")


if __name__ == "__main__":
    main()
