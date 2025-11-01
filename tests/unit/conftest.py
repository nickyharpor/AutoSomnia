"""
Pytest configuration and shared fixtures for unit tests.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def mock_web3():
    """Create a mock Web3 instance."""
    mock_w3 = Mock()
    mock_w3.eth = Mock()
    mock_w3.eth.contract = Mock()
    return mock_w3


@pytest.fixture
def mock_exchange_service():
    """Create a mock SomniaExchangeService."""
    from app.services.somnia_exchange_service import SomniaExchangeService
    
    service = Mock(spec=SomniaExchangeService)
    
    # Mock all async methods
    service.quote = AsyncMock()
    service.get_amount_out = AsyncMock()
    service.get_amounts_out = AsyncMock()
    service.get_weth_address = AsyncMock()
    service.get_factory_address = AsyncMock()
    service.swap_exact_tokens_for_tokens = AsyncMock()
    service.swap_exact_eth_for_tokens = AsyncMock()
    service.swap_exact_tokens_for_eth = AsyncMock()
    
    return service


@pytest.fixture
def sample_quote_request():
    """Sample quote request data."""
    return {
        "amount_a": 1000000000000000000,  # 1 token (18 decimals)
        "reserve_a": 10000000000000000000000,  # 10,000 tokens
        "reserve_b": 5000000000000000000000   # 5,000 tokens
    }


@pytest.fixture
def async_client():
    """Create an async test client."""
    from httpx import AsyncClient
    from fastapi import FastAPI
    
    app = FastAPI()
    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture
def sample_amounts_out_request():
    """Sample amounts out request data."""
    return {
        "amount_in": 1000000000000000000,  # 1 token
        "path": [
            "0x1234567890123456789012345678901234567890",
            "0x0987654321098765432109876543210987654321"
        ]
    }


@pytest.fixture
def sample_swap_request():
    """Sample swap request data."""
    return {
        "amount_in": 1000000000000000000,
        "amount_out_min": 900000000000000000,
        "path": [
            "0x1234567890123456789012345678901234567890",
            "0x0987654321098765432109876543210987654321"
        ],
        "to": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
        "deadline": 1700000000,
        "from_address": "0x1111111111111111111111111111111111111111",
        "private_key": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef01"
    }


# Test configuration
pytest_plugins = []