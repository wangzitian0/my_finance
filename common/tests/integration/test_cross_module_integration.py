#!/usr/bin/env python3
"""
Integration tests for cross-module functionality in the common package.
Tests interactions between core modules, storage, configuration, and build systems.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from common.agents.agent_task_tracker import AgentTaskTracker
from common.build.build_tracker import BuildTracker
from common.core.config_manager import ConfigManager
from common.core.directory_manager import DataLayer, DirectoryManager, StorageBackend
from common.core.storage_manager import LocalFilesystemBackend, StorageManager
from common.monitoring.execution_monitor import ExecutionMonitor, ExecutionResult
from common.schemas.graph_rag_schema import (
    MAGNIFICENT_7_TICKERS,
    DocumentType,
    SECFilingNode,
    StockNode,
)


@pytest.mark.integration
class TestCoreModuleIntegration:
    """Test integration between core modules (directory_manager, config_manager, storage_manager)."""

    def test_directory_manager_storage_manager_integration(self):
        """Test DirectoryManager and StorageManager work together."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup DirectoryManager
            config = {
                "storage": {"backend": "local_filesystem", "root_path": str(temp_dir)},
                "data_layers": {"stage_00_raw": "stage_00_raw"},
            }

            with patch("common.core.directory_manager.DEFAULT_CONFIG_PATH") as mock_config:
                # Create mock config file
                config_file = Path(temp_dir) / "config.yml"
                with open(config_file, "w") as f:
                    import yaml

                    yaml.dump(config, f)
                mock_config.return_value = config_file

                # Initialize DirectoryManager
                dm = DirectoryManager()

                # Get storage manager from DirectoryManager
                storage_manager = dm.get_storage_manager()

                # Test file operations through storage manager
                test_data = {"test": "integration_data"}
                test_path = Path("test_integration.json")

                # Write data
                storage_manager.write_json(test_path, test_data)

                # Verify file exists in correct location
                expected_path = Path(temp_dir) / "test_integration.json"
                assert expected_path.exists()

                # Read data back
                loaded_data = storage_manager.read_json(test_path)
                assert loaded_data == test_data

                # Test layer path integration
                layer_path = dm.get_layer_path(DataLayer.RAW_DATA)
                assert layer_path.parent.name == Path(temp_dir).name

    def test_config_manager_directory_manager_integration(self):
        """Test ConfigManager and DirectoryManager integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config file
            config_data = {
                "storage": {"backend": "local_filesystem", "root_path": str(temp_dir)},
                "layers": {"stage_00_raw": "Raw Data Layer"},
            }

            config_file = Path(temp_dir) / "test_config.yml"
            with open(config_file, "w") as f:
                import yaml

                yaml.dump(config_data, f)

            # Initialize ConfigManager
            config_manager = ConfigManager(config_file)

            # Verify configuration is loaded
            loaded_config = config_manager.get_config()
            assert loaded_config["storage"]["backend"] == "local_filesystem"
            assert loaded_config["storage"]["root_path"] == str(temp_dir)

            # Test DirectoryManager uses the configuration
            with patch("common.core.directory_manager.DEFAULT_CONFIG_PATH", config_file):
                dm = DirectoryManager()

                # Verify DirectoryManager uses the same configuration
                assert str(dm.get_data_root()) == str(temp_dir)


@pytest.mark.integration
class TestBuildSystemIntegration:
    """Test build system integration with core modules."""

    def test_build_tracker_directory_manager_integration(self):
        """Test BuildTracker integrates with DirectoryManager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock DirectoryManager
            with patch.object(DirectoryManager, "get_data_root", return_value=Path(temp_dir)):
                # Initialize BuildTracker (should use DirectoryManager)
                tracker = BuildTracker()

                # Verify build path is under data root
                assert tracker.base_path == Path(temp_dir)
                assert "stage_04_query_results" in str(tracker.build_base_path)

                # Test build workflow
                build_id = tracker.start_build("integration_test", "pytest integration")

                # Verify build directory created
                assert tracker.build_path.exists()
                assert (tracker.build_path / "stage_logs").exists()
                assert (tracker.build_path / "artifacts").exists()

                # Test stage operations
                tracker.start_stage("stage_01_extract")
                tracker.save_artifact("stage_01_extract", "test_artifact.json", {"test": "data"})
                tracker.complete_stage("stage_01_extract", partition="20250101", file_count=5)

                # Complete build
                tracker.complete_build("completed")

                # Verify manifest and report created
                assert (tracker.build_path / "BUILD_MANIFEST.json").exists()
                assert (tracker.build_path / "BUILD_MANIFEST.md").exists()

                # Test build status
                status = tracker.get_build_status()
                assert status["build_id"] == build_id
                assert status["stages_completed"] == 1

    def test_build_tracker_storage_manager_integration(self):
        """Test BuildTracker with StorageManager for artifact storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup storage manager
            storage_manager = StorageManager(LocalFilesystemBackend(root_path=temp_dir))

            # Initialize BuildTracker
            tracker = BuildTracker(base_path=str(Path(temp_dir) / "build"))

            # Start build
            tracker.start_build("storage_test", "pytest storage")

            # Test artifact storage using storage patterns
            artifact_data = {
                "processed_files": ["file1.json", "file2.json"],
                "statistics": {"count": 2, "size_mb": 1.5},
            }

            # Save artifact through BuildTracker
            artifact_path = tracker.save_artifact(
                "stage_02_transform", "results.json", artifact_data
            )

            # Verify artifact can be read through StorageManager
            # (Note: artifact is relative to build path, not storage root)
            artifact_file = Path(artifact_path)
            assert artifact_file.exists()

            # Read artifact data
            with open(artifact_file, "r") as f:
                loaded_data = json.load(f)
            assert loaded_data == artifact_data

            # Test build completion
            tracker.complete_build("completed")

            # Verify build manifest exists
            manifest_path = tracker.build_path / "BUILD_MANIFEST.json"
            assert manifest_path.exists()


@pytest.mark.integration
class TestMonitoringSystemIntegration:
    """Test monitoring system integration with other modules."""

    def test_execution_monitor_directory_manager_integration(self):
        """Test ExecutionMonitor integrates with DirectoryManager for log storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock directory manager logs path
            logs_path = Path(temp_dir) / "logs"

            with patch("common.monitoring.execution_monitor.directory_manager") as mock_dm:
                mock_dm.get_logs_path.return_value = logs_path

                # Initialize ExecutionMonitor
                monitor = ExecutionMonitor()

                # Verify log directory setup
                assert monitor.log_directory == logs_path
                assert logs_path.exists()

                # Test execution logging
                monitor.start_execution("integration_test", "Test integration")
                log_entry = monitor.log_execution(ExecutionResult.SUCCESS)

                # Verify log file created in correct location
                log_date = datetime.now().strftime("%Y-%m-%d")
                log_file = logs_path / f"execution_logs_{log_date}.json"
                assert log_file.exists()

                # Verify log content
                with open(log_file, "r") as f:
                    logs = json.load(f)
                assert len(logs) == 1
                assert logs[0]["agent_type"] == "integration_test"

    def test_agent_task_tracker_build_tracker_integration(self):
        """Test AgentTaskTracker integrates with build processes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize both trackers
            task_tracker = AgentTaskTracker(db_path=Path(temp_dir) / "tasks.db")
            build_tracker = BuildTracker(base_path=str(Path(temp_dir) / "build"))

            # Start build
            build_id = build_tracker.start_build("agent_integration", "pytest agent integration")

            # Create agent tasks for build stages
            extract_task_id = task_tracker.create_task(
                agent_type="data-engineer-agent",
                task_description=f"Execute extract stage for build {build_id}",
                command="extract --config integration",
            )

            transform_task_id = task_tracker.create_task(
                agent_type="data-engineer-agent",
                task_description=f"Execute transform stage for build {build_id}",
                command="transform --config integration",
            )

            # Execute build stages with task tracking
            build_tracker.start_stage("stage_01_extract")
            task_tracker.complete_task(
                extract_task_id, ExecutionResult.SUCCESS, environment_state={"build_id": build_id}
            )
            build_tracker.complete_stage("stage_01_extract", file_count=10)

            build_tracker.start_stage("stage_02_transform")
            task_tracker.complete_task(
                transform_task_id, ExecutionResult.SUCCESS, environment_state={"build_id": build_id}
            )
            build_tracker.complete_stage("stage_02_transform", file_count=8)

            # Complete build
            build_tracker.complete_build("completed")

            # Verify task tracking
            extract_task = task_tracker.get_task(extract_task_id)
            transform_task = task_tracker.get_task(transform_task_id)

            assert extract_task.execution_result == "success"
            assert transform_task.execution_result == "success"
            assert extract_task.environment_state["build_id"] == build_id
            assert transform_task.environment_state["build_id"] == build_id

            # Verify build status
            build_status = build_tracker.get_build_status()
            assert build_status["stages_completed"] == 2
            assert build_status["status"] == "completed"


@pytest.mark.integration
class TestSchemaSystemIntegration:
    """Test schema integration with data processing modules."""

    def test_graph_rag_schema_storage_integration(self):
        """Test Graph RAG schemas with storage systems."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize storage manager
            storage_manager = StorageManager(LocalFilesystemBackend(root_path=temp_dir))

            # Create test data using schema classes
            stocks = []
            for ticker in MAGNIFICENT_7_TICKERS[:3]:  # Test with first 3 stocks
                stock = StockNode(
                    node_id=f"stock_{ticker.lower()}",
                    ticker=ticker,
                    company_name=f"{ticker} Inc.",
                    cik=f"000{ticker.lower()}123",
                    sector="Technology",
                )
                stocks.append(stock)

            # Create SEC filings for stocks
            filings = []
            for i, stock in enumerate(stocks):
                filing = SECFilingNode(
                    node_id=f"filing_{stock.ticker.lower()}_001",
                    accession_number=f"{stock.cik}-24-00000{i+1}",
                    filing_type=DocumentType.SEC_10K,
                    filing_date=datetime(2024, 1, 15 + i),
                    company_cik=stock.cik,
                )
                filings.append(filing)

            # Store stock data using storage manager
            stocks_data = {"stocks": [stock.__dict__ for stock in stocks]}
            storage_manager.write_json(Path("stocks.json"), stocks_data)

            # Store filings data
            filings_data = {"filings": []}
            for filing in filings:
                filing_dict = filing.__dict__.copy()
                # Convert datetime to ISO string for JSON serialization
                if filing_dict.get("filing_date"):
                    filing_dict["filing_date"] = filing_dict["filing_date"].isoformat()
                # Convert enum to string
                if filing_dict.get("filing_type"):
                    filing_dict["filing_type"] = filing_dict["filing_type"].value
                filings_data["filings"].append(filing_dict)

            storage_manager.write_json(Path("filings.json"), filings_data)

            # Verify data was stored correctly
            assert storage_manager.exists(Path("stocks.json"))
            assert storage_manager.exists(Path("filings.json"))

            # Read and verify data
            loaded_stocks = storage_manager.read_json(Path("stocks.json"))
            loaded_filings = storage_manager.read_json(Path("filings.json"))

            assert len(loaded_stocks["stocks"]) == 3
            assert len(loaded_filings["filings"]) == 3

            # Verify first stock data
            first_stock = loaded_stocks["stocks"][0]
            assert first_stock["ticker"] in MAGNIFICENT_7_TICKERS[:3]
            assert first_stock["node_type"] == "Stock"
            assert first_stock["sector"] == "Technology"

            # Verify first filing data
            first_filing = loaded_filings["filings"][0]
            assert first_filing["filing_type"] == "10k"
            assert first_filing["node_type"] == "SECFiling"

    def test_build_tracker_schema_integration(self):
        """Test BuildTracker with Graph RAG schema outputs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize build tracker
            tracker = BuildTracker(base_path=str(Path(temp_dir) / "build"))

            # Start build
            build_id = tracker.start_build("schema_integration", "pytest schema integration")

            # Simulate ETL stage with schema outputs
            tracker.start_stage("stage_01_extract")

            # Create mock extraction results using schemas
            extraction_results = {
                "stocks_extracted": len(MAGNIFICENT_7_TICKERS),
                "filings_found": 21,  # 3 filings per stock
                "document_types": [
                    DocumentType.SEC_10K.value,
                    DocumentType.SEC_10Q.value,
                    DocumentType.SEC_8K.value,
                ],
            }

            # Save extraction results as artifact
            tracker.save_artifact("stage_01_extract", "extraction_results.json", extraction_results)
            tracker.complete_stage("stage_01_extract", file_count=21)

            # Transform stage - create graph nodes
            tracker.start_stage("stage_02_transform")

            # Mock graph transformation results
            graph_results = {
                "nodes_created": 28,  # 7 stocks + 21 filings
                "relationships_created": 21,  # stock -> filing relationships
                "node_types": {"Stock": len(MAGNIFICENT_7_TICKERS), "SECFiling": 21},
            }

            tracker.save_artifact("stage_02_transform", "graph_results.json", graph_results)
            tracker.complete_stage("stage_02_transform", file_count=28)

            # Complete build
            tracker.complete_build("completed")

            # Verify integration results
            build_status = tracker.get_build_status()
            assert build_status["stages_completed"] == 2
            assert build_status["status"] == "completed"

            # Verify artifacts contain schema-based data
            extraction_artifact = (
                tracker.build_path / "artifacts" / "stage_01_extract_extraction_results.json"
            )
            assert extraction_artifact.exists()

            with open(extraction_artifact, "r") as f:
                data = json.load(f)
            assert data["stocks_extracted"] == len(MAGNIFICENT_7_TICKERS)
            assert "10k" in data["document_types"]


@pytest.mark.integration
class TestFullSystemIntegration:
    """Test full system integration across all modules."""

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow integrating all systems."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup base directory structure
            config_data = {
                "storage": {"backend": "local_filesystem", "root_path": str(temp_dir)},
                "data_layers": {
                    "stage_00_raw": "stage_00_raw",
                    "stage_01_daily_delta": "stage_01_daily_delta",
                },
                "logging": {"level": "INFO", "directory": str(Path(temp_dir) / "logs")},
            }

            config_file = Path(temp_dir) / "integration_config.yml"
            with open(config_file, "w") as f:
                import yaml

                yaml.dump(config_data, f)

            # Phase 1: Initialize all systems
            with patch("common.core.directory_manager.DEFAULT_CONFIG_PATH", config_file):
                # Initialize core systems
                config_manager = ConfigManager(config_file)
                directory_manager = DirectoryManager()
                storage_manager = directory_manager.get_storage_manager()

                # Initialize monitoring and tracking
                execution_monitor = ExecutionMonitor(log_directory=Path(temp_dir) / "logs")
                task_tracker = AgentTaskTracker(db_path=Path(temp_dir) / "tasks.db")
                build_tracker = BuildTracker()

                # Phase 2: Execute simulated workflow

                # Start build process
                build_id = build_tracker.start_build(
                    "end_to_end_integration", "pytest full integration"
                )

                # Track extraction task
                execution_monitor.start_execution("data-engineer-agent", "Extract M7 data")
                extract_task_id = task_tracker.create_task(
                    agent_type="data-engineer-agent",
                    task_description="Extract Magnificent 7 company data",
                    command="extract --config integration",
                )

                # Execute extraction stage
                build_tracker.start_stage("stage_01_extract")

                # Simulate data extraction using schemas
                for ticker in MAGNIFICENT_7_TICKERS:
                    stock_data = {
                        "ticker": ticker,
                        "node_type": "Stock",
                        "company_name": f"{ticker} Inc.",
                        "sector": "Technology",
                    }

                    # Store stock data
                    stock_path = Path(f"stocks/{ticker.lower()}.json")
                    storage_manager.write_json(stock_path, stock_data)

                # Complete extraction
                extraction_results = {
                    "stocks_processed": len(MAGNIFICENT_7_TICKERS),
                    "files_created": len(MAGNIFICENT_7_TICKERS),
                }

                build_tracker.save_artifact(
                    "stage_01_extract", "extraction_summary.json", extraction_results
                )
                build_tracker.complete_stage(
                    "stage_01_extract", file_count=len(MAGNIFICENT_7_TICKERS)
                )

                # Complete tracking
                execution_monitor.log_execution(ExecutionResult.SUCCESS)
                task_tracker.complete_task(
                    extract_task_id,
                    ExecutionResult.SUCCESS,
                    environment_state={
                        "build_id": build_id,
                        "stocks_processed": len(MAGNIFICENT_7_TICKERS),
                    },
                )

                # Transform stage
                execution_monitor.start_execution("data-engineer-agent", "Transform data to graph")
                transform_task_id = task_tracker.create_task(
                    agent_type="data-engineer-agent",
                    task_description="Transform data to graph format",
                    command="transform --format graph",
                )

                build_tracker.start_stage("stage_02_transform")

                # Simulate graph transformation
                graph_data = {"nodes": [], "relationships": []}

                # Create nodes for each stock
                for ticker in MAGNIFICENT_7_TICKERS:
                    # Read stock data
                    stock_path = Path(f"stocks/{ticker.lower()}.json")
                    stock_data = storage_manager.read_json(stock_path)

                    # Add to graph
                    graph_data["nodes"].append(
                        {
                            "node_id": f"stock_{ticker.lower()}",
                            "node_type": "Stock",
                            "properties": stock_data,
                        }
                    )

                # Store graph data
                storage_manager.write_json(Path("graph/nodes.json"), graph_data)

                # Complete transform stage
                transform_results = {
                    "nodes_created": len(MAGNIFICENT_7_TICKERS),
                    "graph_ready": True,
                }

                build_tracker.save_artifact(
                    "stage_02_transform", "transform_summary.json", transform_results
                )
                build_tracker.complete_stage("stage_02_transform", file_count=1)  # graph file

                execution_monitor.log_execution(ExecutionResult.SUCCESS)
                task_tracker.complete_task(
                    transform_task_id,
                    ExecutionResult.SUCCESS,
                    environment_state={
                        "build_id": build_id,
                        "nodes_created": len(MAGNIFICENT_7_TICKERS),
                    },
                )

                # Complete build
                build_tracker.complete_build("completed")

                # Phase 3: Verify integration results

                # Verify configuration was used correctly
                loaded_config = config_manager.get_config()
                assert loaded_config["storage"]["root_path"] == str(temp_dir)

                # Verify directory structure
                assert directory_manager.get_data_root() == Path(temp_dir)

                # Verify data storage
                for ticker in MAGNIFICENT_7_TICKERS:
                    stock_path = Path(f"stocks/{ticker.lower()}.json")
                    assert storage_manager.exists(stock_path)

                assert storage_manager.exists(Path("graph/nodes.json"))

                # Verify build tracking
                build_status = build_tracker.get_build_status()
                assert build_status["build_id"] == build_id
                assert build_status["status"] == "completed"
                assert build_status["stages_completed"] == 2

                # Verify task tracking
                extract_task = task_tracker.get_task(extract_task_id)
                transform_task = task_tracker.get_task(transform_task_id)

                assert extract_task.execution_result == "success"
                assert transform_task.execution_result == "success"
                assert extract_task.environment_state["build_id"] == build_id
                assert transform_task.environment_state["build_id"] == build_id

                # Verify execution monitoring
                exec_stats = execution_monitor.get_execution_stats(days=1)
                assert exec_stats["total_executions"] == 2
                assert exec_stats["success_count"] == 2
                assert exec_stats["failure_count"] == 0
                assert "data-engineer-agent" in exec_stats["agent_performance"]

                # Verify all systems are consistent
                agent_perf = exec_stats["agent_performance"]["data-engineer-agent"]
                assert agent_perf["total"] == 2
                assert agent_perf["success"] == 2

                # Verify build artifacts
                manifest_path = build_tracker.build_path / "BUILD_MANIFEST.json"
                assert manifest_path.exists()

                with open(manifest_path, "r") as f:
                    manifest = json.load(f)

                assert manifest["build_info"]["build_id"] == build_id
                assert manifest["stages"]["stage_01_extract"]["status"] == "completed"
                assert manifest["stages"]["stage_02_transform"]["status"] == "completed"

                print(f"✅ End-to-end integration test completed successfully!")
                print(f"   Build ID: {build_id}")
                print(f"   Stocks processed: {len(MAGNIFICENT_7_TICKERS)}")
                print(f"   Tasks completed: 2")
                print(f"   Executions tracked: 2")
                print(f"   Files created: {len(MAGNIFICENT_7_TICKERS) + 1}")  # stocks + graph
