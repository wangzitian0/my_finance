from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_neo4j():
    """Mock Neo4j connection for testing"""
    with patch("neo4j.GraphDatabase.driver") as mock_driver:
        mock_session = Mock()
        mock_driver.return_value.session.return_value = mock_session
        yield mock_session
