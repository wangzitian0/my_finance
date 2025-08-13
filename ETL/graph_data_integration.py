#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL Graph Data Integration Module

Handles the integration of financial data into Neo4j graph database.
This module is responsible for:
- Creating graph nodes from financial data
- Establishing relationships between entities
- Managing Neo4j schema and constraints
- Data validation and consistency checks

Part of Stage 3 (Load) in the ETL pipeline.
"""

import json
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from neomodel import config, db
from neomodel.exceptions import DoesNotExist, MultipleNodesReturned

from common.graph_rag_schema import (MAGNIFICENT_7_CIKS, DCFValuationNode,
                                     DocumentChunkNode, DocumentType,
                                     ETLStageOutput, FinancialMetricsNode,
                                     GraphRelationship, NewsEventNode,
                                     RelationshipType, SECFilingNode,
                                     StockNode)

logger = logging.getLogger(__name__)


class GraphDataIntegrator:
    """
    Integrates financial data into Neo4j graph database.

    This class handles the transformation of structured financial data
    into graph nodes and relationships for the Graph RAG system.
    """

    def __init__(
        self,
        neo4j_url: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "password",
    ):
        """
        Initialize the graph data integrator.

        Args:
            neo4j_url: Neo4j database URL
            username: Database username
            password: Database password
        """
        self.neo4j_url = neo4j_url
        self.username = username
        self.password = password
        self.setup_connection()

    def setup_connection(self):
        """Setup Neo4j connection and constraints."""
        try:
            config.DATABASE_URL = f"{self.neo4j_url}"
            db.set_connection(url=self.neo4j_url, username=self.username, password=self.password)

            # Test connection
            db.cypher_query("RETURN 1 as test")
            logger.info("Neo4j connection established successfully")

            # Setup constraints and indexes
            self._setup_schema_constraints()

        except Exception as e:
            logger.error(f"Failed to setup Neo4j connection: {e}")
            raise

    def _setup_schema_constraints(self):
        """Setup database constraints and indexes for performance."""
        constraints = [
            # Unique constraints
            "CREATE CONSTRAINT stock_ticker IF NOT EXISTS FOR (s:Stock) REQUIRE s.ticker IS UNIQUE",
            "CREATE CONSTRAINT sec_filing_accession IF NOT EXISTS FOR (f:SECFiling) REQUIRE f.accession_number IS UNIQUE",
            "CREATE CONSTRAINT document_chunk_id IF NOT EXISTS FOR (c:DocumentChunk) REQUIRE c.node_id IS UNIQUE",
            "CREATE CONSTRAINT dcf_valuation_id IF NOT EXISTS FOR (d:DCFValuation) REQUIRE d.node_id IS UNIQUE",
            "CREATE CONSTRAINT news_event_id IF NOT EXISTS FOR (n:NewsEvent) REQUIRE n.node_id IS UNIQUE",
            # Indexes for performance
            "CREATE INDEX stock_cik IF NOT EXISTS FOR (s:Stock) ON (s.cik)",
            "CREATE INDEX filing_date IF NOT EXISTS FOR (f:SECFiling) ON (f.filing_date)",
            "CREATE INDEX filing_type IF NOT EXISTS FOR (f:SECFiling) ON (f.filing_type)",
            "CREATE INDEX valuation_date IF NOT EXISTS FOR (d:DCFValuation) ON (d.valuation_date)",
            "CREATE INDEX news_publication_date IF NOT EXISTS FOR (n:NewsEvent) ON (n.publication_date)",
            "CREATE INDEX metrics_report_date IF NOT EXISTS FOR (m:FinancialMetrics) ON (m.report_date)",
        ]

        for constraint in constraints:
            try:
                db.cypher_query(constraint)
                logger.debug(f"Applied constraint: {constraint}")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    logger.warning(f"Failed to apply constraint: {constraint}, error: {e}")

    def integrate_m7_data(self, data_dir: Path) -> ETLStageOutput.GraphNodesOutput:
        """
        Integrate Magnificent 7 companies data into graph database.

        Args:
            data_dir: Directory containing processed data

        Returns:
            GraphNodesOutput with integration statistics
        """
        logger.info("Starting M7 data integration into graph database")

        stats = {"nodes_created": 0, "relationships_created": 0, "node_types": {}}

        try:
            # Process each M7 company
            for ticker in MAGNIFICENT_7_CIKS.keys():
                logger.info(f"Processing {ticker} data integration")

                # Create stock node
                stock_stats = self._create_stock_node(ticker)
                self._update_stats(stats, stock_stats)

                # Process SEC filings
                sec_stats = self._integrate_sec_filings(ticker, data_dir)
                self._update_stats(stats, sec_stats)

                # Process Yahoo Finance data
                yf_stats = self._integrate_yfinance_data(ticker, data_dir)
                self._update_stats(stats, yf_stats)

                # Process DCF results if available
                dcf_stats = self._integrate_dcf_results(ticker, data_dir)
                self._update_stats(stats, dcf_stats)

                logger.info(f"Completed {ticker} integration")

            # Create cross-company relationships
            relation_stats = self._create_industry_relationships()
            self._update_stats(stats, relation_stats)

            logger.info(
                f"Graph data integration completed. Total nodes: {stats['nodes_created']}, "
                f"relationships: {stats['relationships_created']}"
            )

            return ETLStageOutput.GraphNodesOutput(
                nodes_created=stats["nodes_created"],
                relationships_created=stats["relationships_created"],
                node_types=stats["node_types"],
                output_path=str(data_dir / "graph_nodes"),
            )

        except Exception as e:
            logger.error(f"Failed to integrate M7 data: {e}")
            raise

    def _create_stock_node(self, ticker: str) -> Dict[str, int]:
        """Create or update stock node for a ticker."""
        cik = MAGNIFICENT_7_CIKS[ticker]

        # Company metadata (simplified for demo)
        company_info = {
            "AAPL": {
                "name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
            },
            "MSFT": {
                "name": "Microsoft Corporation",
                "sector": "Technology",
                "industry": "Software",
            },
            "AMZN": {
                "name": "Amazon.com Inc.",
                "sector": "Consumer Discretionary",
                "industry": "E-commerce",
            },
            "GOOGL": {
                "name": "Alphabet Inc.",
                "sector": "Technology",
                "industry": "Internet Services",
            },
            "META": {
                "name": "Meta Platforms Inc.",
                "sector": "Technology",
                "industry": "Social Media",
            },
            "TSLA": {
                "name": "Tesla Inc.",
                "sector": "Consumer Discretionary",
                "industry": "Electric Vehicles",
            },
            "NFLX": {
                "name": "Netflix Inc.",
                "sector": "Communication Services",
                "industry": "Streaming",
            },
        }

        info = company_info.get(
            ticker, {"name": f"{ticker} Inc.", "sector": "Unknown", "industry": "Unknown"}
        )

        stock_node = StockNode(
            node_id=f"stock_{ticker}",
            ticker=ticker,
            company_name=info["name"],
            cik=cik,
            sector=info["sector"],
            industry=info["industry"],
            created_at=datetime.now(),
        )

        # Create node in Neo4j
        cypher = """
        MERGE (s:Stock {ticker: $ticker})
        SET s.node_id = $node_id,
            s.company_name = $company_name,
            s.cik = $cik,
            s.sector = $sector,
            s.industry = $industry,
            s.created_at = $created_at,
            s.updated_at = $updated_at
        """

        db.cypher_query(
            cypher,
            {
                "ticker": stock_node.ticker,
                "node_id": stock_node.node_id,
                "company_name": stock_node.company_name,
                "cik": stock_node.cik,
                "sector": stock_node.sector,
                "industry": stock_node.industry,
                "created_at": stock_node.created_at.isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
        )

        logger.debug(f"Created/updated stock node for {ticker}")
        return {"nodes_created": 1, "node_types": {"Stock": 1}}

    def _integrate_sec_filings(self, ticker: str, data_dir: Path) -> Dict[str, int]:
        """Integrate SEC filings for a ticker."""
        stats = {"nodes_created": 0, "relationships_created": 0, "node_types": {}}

        sec_dir = data_dir / "stage_01_extract" / "sec_edgar"
        if not sec_dir.exists():
            logger.warning(f"SEC data directory not found: {sec_dir}")
            return stats

        # Find latest SEC data partition
        partitions = [d for d in sec_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        if not partitions:
            logger.warning(f"No SEC data partitions found in {sec_dir}")
            return stats

        latest_partition = max(partitions, key=lambda x: x.name)
        ticker_dir = latest_partition / ticker

        if not ticker_dir.exists():
            logger.warning(f"No SEC data for {ticker} in {ticker_dir}")
            return stats

        # Process SEC files
        sec_files = list(ticker_dir.glob(f"{ticker}_sec_edgar_*.txt"))
        logger.info(f"Found {len(sec_files)} SEC files for {ticker}")

        for sec_file in sec_files:
            try:
                # Parse filename to extract metadata
                filename_parts = sec_file.stem.split("_")
                if len(filename_parts) >= 5:
                    filing_type = filename_parts[3]  # 10k, 10q, 8k
                    accession_number = (
                        filename_parts[5] if len(filename_parts) > 5 else filename_parts[4]
                    )

                    # Create SEC filing node
                    filing_node = SECFilingNode(
                        node_id=f"sec_{ticker}_{accession_number}",
                        accession_number=accession_number,
                        filing_type=DocumentType(filing_type.upper()),
                        filing_date=datetime.now(),  # Would parse from file content in real implementation
                        company_cik=MAGNIFICENT_7_CIKS[ticker],
                        created_at=datetime.now(),
                    )

                    # Create filing node and relationship
                    self._create_sec_filing_node(filing_node, ticker)
                    stats["nodes_created"] += 1
                    stats["relationships_created"] += 1
                    stats["node_types"]["SECFiling"] = stats["node_types"].get("SECFiling", 0) + 1

            except Exception as e:
                logger.error(f"Failed to process SEC file {sec_file}: {e}")
                continue

        return stats

    def _create_sec_filing_node(self, filing_node: SECFilingNode, ticker: str):
        """Create SEC filing node and relationships."""
        cypher = """
        MERGE (f:SECFiling {accession_number: $accession_number})
        SET f.node_id = $node_id,
            f.filing_type = $filing_type,
            f.filing_date = $filing_date,
            f.company_cik = $company_cik,
            f.created_at = $created_at
        WITH f
        MATCH (s:Stock {ticker: $ticker})
        MERGE (s)-[:HAS_FILING]->(f)
        """

        db.cypher_query(
            cypher,
            {
                "accession_number": filing_node.accession_number,
                "node_id": filing_node.node_id,
                "filing_type": filing_node.filing_type.value,
                "filing_date": filing_node.filing_date.isoformat(),
                "company_cik": filing_node.company_cik,
                "created_at": filing_node.created_at.isoformat(),
                "ticker": ticker,
            },
        )

    def _integrate_yfinance_data(self, ticker: str, data_dir: Path) -> Dict[str, int]:
        """Integrate Yahoo Finance data for financial metrics."""
        stats = {"nodes_created": 0, "relationships_created": 0, "node_types": {}}

        # Find YFinance data files
        yf_dir = data_dir / "stage_01_extract" / "yfinance"
        if not yf_dir.exists():
            logger.warning(f"YFinance data directory not found: {yf_dir}")
            return stats

        # Find latest partition with ticker data
        for partition_dir in sorted(yf_dir.iterdir(), reverse=True):
            if not partition_dir.is_dir() or not partition_dir.name.isdigit():
                continue

            ticker_dir = partition_dir / ticker
            if not ticker_dir.exists():
                continue

            yf_files = list(ticker_dir.glob(f"{ticker}_yfinance_*.json"))
            if not yf_files:
                continue

            # Process most recent file (simplified)
            latest_file = max(yf_files, key=lambda x: x.stat().st_mtime)

            try:
                with open(latest_file, "r") as f:
                    data = json.load(f)

                # Create financial metrics node (simplified)
                metrics_node = FinancialMetricsNode(
                    node_id=f"metrics_{ticker}_{partition_dir.name}",
                    ticker=ticker,
                    report_date=datetime.now(),
                    created_at=datetime.now(),
                )

                self._create_financial_metrics_node(metrics_node, ticker)
                stats["nodes_created"] += 1
                stats["relationships_created"] += 1
                stats["node_types"]["FinancialMetrics"] = (
                    stats["node_types"].get("FinancialMetrics", 0) + 1
                )

                break

            except Exception as e:
                logger.error(f"Failed to process YFinance file {latest_file}: {e}")
                continue

        return stats

    def _create_financial_metrics_node(self, metrics_node: FinancialMetricsNode, ticker: str):
        """Create financial metrics node and relationships."""
        cypher = """
        MERGE (m:FinancialMetrics {node_id: $node_id})
        SET m.ticker = $ticker,
            m.report_date = $report_date,
            m.created_at = $created_at
        WITH m
        MATCH (s:Stock {ticker: $ticker})
        MERGE (s)-[:HAS_METRIC]->(m)
        """

        db.cypher_query(
            cypher,
            {
                "node_id": metrics_node.node_id,
                "ticker": metrics_node.ticker,
                "report_date": metrics_node.report_date.isoformat(),
                "created_at": metrics_node.created_at.isoformat(),
            },
        )

    def _integrate_dcf_results(self, ticker: str, data_dir: Path) -> Dict[str, int]:
        """Integrate DCF valuation results if available."""
        stats = {"nodes_created": 0, "relationships_created": 0, "node_types": {}}

        # Check for DCF results in stage_03_load
        dcf_dir = data_dir / "stage_03_load"
        if not dcf_dir.exists():
            return stats

        # Look for DCF result files (simplified implementation)
        dcf_files = list(dcf_dir.glob("**/dcf_results*.json"))
        if not dcf_files:
            return stats

        # Process DCF results (simplified)
        for dcf_file in dcf_files:
            try:
                with open(dcf_file, "r") as f:
                    dcf_data = json.load(f)

                if ticker in dcf_data:
                    dcf_node = DCFValuationNode(
                        node_id=f"dcf_{ticker}_{datetime.now().strftime('%Y%m%d')}",
                        ticker=ticker,
                        valuation_date=datetime.now(),
                        intrinsic_value=100.0,  # Placeholder
                        discount_rate=0.1,
                        terminal_growth_rate=0.03,
                        created_at=datetime.now(),
                    )

                    self._create_dcf_valuation_node(dcf_node, ticker)
                    stats["nodes_created"] += 1
                    stats["relationships_created"] += 1
                    stats["node_types"]["DCFValuation"] = (
                        stats["node_types"].get("DCFValuation", 0) + 1
                    )

            except Exception as e:
                logger.error(f"Failed to process DCF file {dcf_file}: {e}")
                continue

        return stats

    def _create_dcf_valuation_node(self, dcf_node: DCFValuationNode, ticker: str):
        """Create DCF valuation node and relationships."""
        cypher = """
        MERGE (d:DCFValuation {node_id: $node_id})
        SET d.ticker = $ticker,
            d.valuation_date = $valuation_date,
            d.intrinsic_value = $intrinsic_value,
            d.discount_rate = $discount_rate,
            d.terminal_growth_rate = $terminal_growth_rate,
            d.created_at = $created_at
        WITH d
        MATCH (s:Stock {ticker: $ticker})
        MERGE (s)-[:HAS_VALUATION]->(d)
        """

        db.cypher_query(
            cypher,
            {
                "node_id": dcf_node.node_id,
                "ticker": dcf_node.ticker,
                "valuation_date": dcf_node.valuation_date.isoformat(),
                "intrinsic_value": dcf_node.intrinsic_value,
                "discount_rate": dcf_node.discount_rate,
                "terminal_growth_rate": dcf_node.terminal_growth_rate,
                "created_at": dcf_node.created_at.isoformat(),
            },
        )

    def _create_industry_relationships(self) -> Dict[str, int]:
        """Create relationships between companies in the same industry."""
        cypher = """
        MATCH (s1:Stock), (s2:Stock)
        WHERE s1.industry = s2.industry AND s1.ticker <> s2.ticker
        MERGE (s1)-[r:SAME_INDUSTRY]->(s2)
        RETURN count(r) as relationships_created
        """

        result, _ = db.cypher_query(cypher)
        relationships_created = result[0][0] if result else 0

        return {"relationships_created": relationships_created}

    def _update_stats(self, main_stats: Dict[str, int], new_stats: Dict[str, int]):
        """Update main statistics with new statistics."""
        for key, value in new_stats.items():
            if key == "node_types":
                if "node_types" not in main_stats:
                    main_stats["node_types"] = {}
                for node_type, count in value.items():
                    main_stats["node_types"][node_type] = (
                        main_stats["node_types"].get(node_type, 0) + count
                    )
            else:
                main_stats[key] = main_stats.get(key, 0) + value

    def get_integration_stats(self) -> Dict[str, Any]:
        """Get current integration statistics."""
        cypher = """
        MATCH (n)
        RETURN labels(n)[0] as node_type, count(n) as count
        """

        result, _ = db.cypher_query(cypher)
        node_stats = {row[0]: row[1] for row in result}

        cypher_rels = """
        MATCH ()-[r]->()
        RETURN type(r) as relationship_type, count(r) as count
        """

        result_rels, _ = db.cypher_query(cypher_rels)
        relationship_stats = {row[0]: row[1] for row in result_rels}

        return {
            "nodes": node_stats,
            "relationships": relationship_stats,
            "total_nodes": sum(node_stats.values()),
            "total_relationships": sum(relationship_stats.values()),
        }
