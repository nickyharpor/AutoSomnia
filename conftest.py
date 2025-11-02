"""
Root pytest configuration file.

This file contains global pytest configuration and plugins
that apply to the entire test suite.
"""

import pytest
import asyncio

# Global pytest plugins
pytest_plugins = []

# Global fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

# Global pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "blockchain: marks tests that require blockchain connection"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that require API server"
    )
    config.addinivalue_line(
        "markers", "discovery: marks tests for pytest discovery verification"
    )
    config.addinivalue_line(
        "markers", "config: marks tests for configuration validation"
    )