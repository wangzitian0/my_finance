#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j Health Check HTTP Endpoint

Provides HTTP endpoint for Neo4j health monitoring suitable for
production monitoring systems and load balancers.

Issue #266: Comprehensive Neo4j Testing Infrastructure
"""

import json
import logging
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

from .health_checks import HealthChecker
from .neo4j_manager import Neo4jManager


class HealthEndpointHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Neo4j health checks."""

    def __init__(self, health_checker: HealthChecker, *args, **kwargs):
        self.health_checker = health_checker
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests for health checks."""
        if self.path == "/health/neo4j":
            self._handle_health_check()
        elif self.path == "/health/neo4j/metrics":
            self._handle_metrics()
        elif self.path == "/health/neo4j/detailed":
            self._handle_detailed_health()
        else:
            self._send_response(404, {"error": "Endpoint not found"})

    def _handle_health_check(self):
        """Handle basic health check endpoint."""
        try:
            health_data = self.health_checker.health_check_endpoint()

            # Return appropriate HTTP status based on health
            if health_data["status"] == "healthy":
                status_code = 200
            elif health_data["status"] == "degraded":
                status_code = 200  # Still serving, but with warnings
            else:
                status_code = 503  # Service unavailable

            self._send_response(status_code, health_data)

        except Exception as e:
            self._send_response(
                503,
                {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()},
            )

    def _handle_metrics(self):
        """Handle metrics endpoint for monitoring systems."""
        try:
            metrics = self.health_checker.monitoring_metrics()
            self._send_response(200, metrics)

        except Exception as e:
            self._send_response(500, {"error": str(e)})

    def _handle_detailed_health(self):
        """Handle detailed health check with full diagnostics."""
        try:
            # Include CRUD tests only in development
            include_crud = self.health_checker.manager.environment == "development"
            health_data = self.health_checker.health_check_endpoint(include_crud)

            # Add additional diagnostic information
            health_data["diagnostics"] = {
                "environment": self.health_checker.manager.environment,
                "configuration": {
                    "host": self.health_checker.manager.config.get("host"),
                    "port": self.health_checker.manager.config.get("port"),
                    "database": self.health_checker.manager.config.get("database"),
                },
                "performance_baseline_ms": self.health_checker.performance_baseline_ms,
            }

            status_code = 200 if health_data["status"] in ["healthy", "degraded"] else 503
            self._send_response(status_code, health_data)

        except Exception as e:
            self._send_response(
                503,
                {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()},
            )

    def _send_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        response_data = json.dumps(data, indent=2)
        self.wfile.write(response_data.encode("utf-8"))

    def log_message(self, format, *args):
        """Override to use proper logging."""
        logging.info(f"Health endpoint: {format % args}")


class Neo4jHealthServer:
    """
    HTTP server for Neo4j health check endpoints.

    Provides health check endpoints that can be used by:
    - Load balancers for health checks
    - Monitoring systems (Prometheus, etc.)
    - Operations teams for diagnostics
    """

    def __init__(self, manager: Neo4jManager, host: str = "0.0.0.0", port: int = 8080):
        """
        Initialize health server.

        Args:
            manager: Neo4jManager instance
            host: Server host address
            port: Server port
        """
        self.manager = manager
        self.health_checker = HealthChecker(manager)
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self._logger = logging.getLogger(__name__)

    def start(self) -> bool:
        """
        Start the health check server.

        Returns:
            True if server started successfully
        """
        try:
            # Create handler class with health checker injected
            def handler_factory(*args, **kwargs):
                return HealthEndpointHandler(self.health_checker, *args, **kwargs)

            self.server = HTTPServer((self.host, self.port), handler_factory)

            # Start server in background thread
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()

            self._logger.info(f"Neo4j health server started on {self.host}:{self.port}")
            self._logger.info("Available endpoints:")
            self._logger.info(f"  http://{self.host}:{self.port}/health/neo4j - Basic health check")
            self._logger.info(f"  http://{self.host}:{self.port}/health/neo4j/metrics - Metrics")
            self._logger.info(
                f"  http://{self.host}:{self.port}/health/neo4j/detailed - Detailed diagnostics"
            )

            return True

        except Exception as e:
            self._logger.error(f"Failed to start health server: {e}")
            return False

    def stop(self):
        """Stop the health check server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()

        if self.server_thread:
            self.server_thread.join(timeout=5)

        self._logger.info("Neo4j health server stopped")

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health status without HTTP server.

        Returns:
            Health status dictionary
        """
        return self.health_checker.health_check_endpoint()


def create_health_server(
    environment: str = None, host: str = "0.0.0.0", port: int = 8080
) -> Neo4jHealthServer:
    """
    Create and configure a Neo4j health server.

    Args:
        environment: Neo4j environment (auto-detected if None)
        host: Server host address
        port: Server port

    Returns:
        Configured Neo4jHealthServer instance
    """
    manager = Neo4jManager(environment)
    return Neo4jHealthServer(manager, host, port)


# CLI interface for running health server
if __name__ == "__main__":
    import argparse
    import signal
    import sys

    parser = argparse.ArgumentParser(description="Neo4j Health Check Server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("--environment", help="Neo4j environment (dev/ci/production)")
    parser.add_argument("--log-level", default="INFO", help="Logging level")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create and start server
    server = create_health_server(args.environment, args.host, args.port)

    if not server.start():
        print("Failed to start health server")
        sys.exit(1)

    print(f"Neo4j Health Server running on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop")

    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        print("\nShutting down health server...")
        server.stop()
        server.manager.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Keep main thread alive
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        signal_handler(None, None)
