"""
Pytest-compatible integration tests for exchange routes, focusing on the get_quote endpoint.

This test uses real blockchain connections and environment configuration
to test the actual functionality of the exchange service.
"""

import pytest
import asyncio
import logging
import sys
from pathlib import Path
import httpx

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.backend_config import settings
from app.services.somnia_exchange_service import SomniaExchangeService
from web3 import AsyncWeb3
from fastapi import FastAPI
from app.api.routes.exchange import router

# Configure logging with UTF-8 encoding support
import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

logging.basicConfig(
    level=logging.INFO, 
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Helper function to safely handle Unicode characters
def safe_log(message):
    """Safely log messages, replacing problematic Unicode characters."""
    try:
        # Replace common Unicode characters with ASCII equivalents
        safe_message = message.replace('✅', '[OK]').replace('❌', '[ERROR]').replace('⚠️', '[WARN]')
        safe_message = safe_message.replace('🔗', '[CONN]').replace('💱', '[QUOTE]').replace('🌐', '[API]')
        safe_message = safe_message.replace('🏦', '[DEFI]').replace('📋', '[INFO]').replace('🔧', '[CONFIG]')
        safe_message = safe_message.replace('🧪', '[TEST]').replace('🎯', '[TARGET]').replace('🎉', '[SUCCESS]')
        return safe_message
    except Exception:
        return str(message).encode('ascii', 'replace').decode('ascii')


# Pytest fixtures
@pytest.fixture
def exchange_service_factory():
    """Factory to create exchange service instances with proper cleanup."""
    async def _create_service():
        try:
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.RPC_URL))
            
            # Test connection
            is_connected = await w3.is_connected()
            if not is_connected:
                pytest.skip(f"Cannot connect to blockchain at {settings.RPC_URL}")
            
            logger.info(safe_log(f"✅ Connected to blockchain at {settings.RPC_URL}"))
            
            # Get latest block for verification
            latest_block = await w3.eth.get_block('latest')
            logger.info(safe_log(f"✅ Latest block: {latest_block['number']}"))
            
            service = SomniaExchangeService(w3, settings.ROUTER_ADDRESS)
            return service
            
        except Exception as e:
            pytest.skip(f"Failed to setup exchange service: {e}")
    
    return _create_service


@pytest.fixture(scope="session")
def test_app():
    """Create FastAPI test application."""
    app = FastAPI()
    app.include_router(router)
    return app


class TestExchangeIntegration:
    """Pytest-compatible integration tests for exchange functionality."""
    
    def setup_class(cls):
        """Setup class-level configuration logging."""
        logger.info(safe_log("🔧 Exchange Integration Test Configuration:"))
        logger.info(f"  RPC URL: {settings.RPC_URL}")
        logger.info(f"  Chain ID: {settings.CHAIN_ID}")
        logger.info(f"  Router Address: {settings.ROUTER_ADDRESS}")
        logger.info(f"  WSTT Address: {settings.WSTT}")
        logger.info(f"  SUSDT Address: {settings.SUSDT}")
    
    def test_configuration_loaded(self):
        """Test that environment configuration is properly loaded."""
        print("\n🔧 Configuration Test")
        print("=" * 50)
        
        assert settings.RPC_URL is not None, "RPC URL not found"
        assert settings.RPC_URL.startswith('http'), "RPC URL should start with http"
        
        assert settings.CHAIN_ID > 0, "Chain ID should be positive"
        
        assert settings.ROUTER_ADDRESS is not None, "Router address not found"
        assert settings.ROUTER_ADDRESS.startswith('0x'), "Router address should start with 0x"
        assert len(settings.ROUTER_ADDRESS) == 42, "Router address should be 42 characters"
        
        logger.info(safe_log(f"✅ Configuration test passed"))
        logger.info(f"  RPC URL: {settings.RPC_URL}")
        logger.info(f"  Chain ID: {settings.CHAIN_ID}")
        logger.info(f"  Router: {settings.ROUTER_ADDRESS}")
    
    @pytest.mark.asyncio
    async def test_blockchain_connection(self, exchange_service_factory):
        """Test that we can connect to the blockchain."""
        print("\n🔗 Blockchain Connection Test")
        print("=" * 50)
        
        # Create exchange service
        exchange_service = await exchange_service_factory()
        
        assert exchange_service is not None, "Exchange service should be initialized"
        
        # Test that we can make a basic call
        w3 = exchange_service.w3
        latest_block = await w3.eth.get_block('latest')
        
        assert latest_block is not None, "Should be able to get latest block"
        assert latest_block['number'] > 0, "Block number should be positive"
        
        logger.info(safe_log(f"✅ Successfully connected to blockchain"))
        logger.info(safe_log(f"✅ Latest block: {latest_block['number']}"))
    
    @pytest.mark.asyncio
    async def test_service_basic_info(self, exchange_service_factory):
        """Test basic service information retrieval."""
        print("\n📋 Service Basic Info Test")
        print("=" * 50)
        
        # Create exchange service
        exchange_service = await exchange_service_factory()
        
        try:
            # Get WETH address
            weth_address = await exchange_service.get_weth_address()
            assert weth_address is not None, "WETH address should not be None"
            assert weth_address.startswith('0x'), "WETH address should start with 0x"
            assert len(weth_address) == 42, "WETH address should be 42 characters"
            logger.info(safe_log(f"✅ WETH Address: {weth_address}"))
            
            # Get factory address
            factory_address = await exchange_service.get_factory_address()
            assert factory_address is not None, "Factory address should not be None"
            assert factory_address.startswith('0x'), "Factory address should start with 0x"
            assert len(factory_address) == 42, "Factory address should be 42 characters"
            logger.info(safe_log(f"✅ Factory Address: {factory_address}"))
            
        except Exception as e:
            pytest.fail(f"Failed to get basic service info: {e}")
    
    @pytest.mark.asyncio
    async def test_quote_calculation(self, exchange_service_factory):
        """Test quote calculation with realistic values."""
        print("\n💱 Quote Calculation Test")
        print("=" * 50)
        
        # Create exchange service
        exchange_service = await exchange_service_factory()
        
        try:
            # Test case 1: Small amount quote
            amount_a = 1000000000000000000  # 1 token (18 decimals)
            reserve_a = 10000000000000000000000  # 10,000 tokens
            reserve_b = 5000000000000000000000   # 5,000 tokens
            
            quote_result = await exchange_service.quote(amount_a, reserve_a, reserve_b)
            expected_ratio = (amount_a * reserve_b) // reserve_a  # Simple calculation
            
            assert quote_result > 0, "Quote result should be positive"
            assert isinstance(quote_result, int), "Quote result should be an integer"
            
            # Allow for some variance due to contract logic
            variance = abs(quote_result - expected_ratio) / expected_ratio
            assert variance < 0.1, f"Quote variance too high: {variance:.4f}"
            
            logger.info(safe_log(f"✅ Quote Result: {quote_result}"))
            logger.info(safe_log(f"✅ Expected Ratio: {expected_ratio}"))
            logger.info(safe_log(f"✅ Variance: {variance:.4f}"))
            
            # Test case 2: Different ratio
            amount_a2 = 5000000000000000000  # 5 tokens
            reserve_a2 = 20000000000000000000000  # 20,000 tokens
            reserve_b2 = 10000000000000000000000  # 10,000 tokens
            
            quote_result2 = await exchange_service.quote(amount_a2, reserve_a2, reserve_b2)
            expected_ratio2 = (amount_a2 * reserve_b2) // reserve_a2
            
            assert quote_result2 > 0, "Quote result 2 should be positive"
            
            variance2 = abs(quote_result2 - expected_ratio2) / expected_ratio2
            assert variance2 < 0.1, f"Quote variance 2 too high: {variance2:.4f}"
            
            logger.info(safe_log(f"✅ Quote Result 2: {quote_result2}"))
            logger.info(safe_log(f"✅ Expected Ratio 2: {expected_ratio2}"))
            logger.info(safe_log(f"✅ Variance 2: {variance2:.4f}"))
            
        except Exception as e:
            pytest.fail(f"Failed to calculate quote: {e}")
    
    @pytest.mark.asyncio
    async def test_api_endpoint_quote(self, test_app):
        """Test the actual API endpoint with HTTP requests."""
        print("\n🌐 API Endpoint Test")
        print("=" * 50)
        
        try:
            # Test data based on environment configuration
            test_requests = [
                {
                    "name": "Basic Quote Test",
                    "data": {
                        "amount_a": 1000000000000000000,  # 1 token
                        "reserve_a": 10000000000000000000000,  # 10,000 tokens
                        "reserve_b": 5000000000000000000000   # 5,000 tokens
                    }
                },
                {
                    "name": "Large Amount Test",
                    "data": {
                        "amount_a": 100000000000000000000,  # 100 tokens
                        "reserve_a": 1000000000000000000000000,  # 1,000,000 tokens
                        "reserve_b": 500000000000000000000000   # 500,000 tokens
                    }
                },
                {
                    "name": "Small Amount Test",
                    "data": {
                        "amount_a": 1000000000000000,  # 0.001 tokens
                        "reserve_a": 1000000000000000000000,  # 1,000 tokens
                        "reserve_b": 2000000000000000000000   # 2,000 tokens
                    }
                }
            ]
            
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=test_app), base_url="http://test") as client:
                for test_case in test_requests:
                    logger.info(safe_log(f"🧪 Running: {test_case['name']}"))
                    
                    response = await client.post("/exchange/quote", json=test_case["data"])
                    
                    assert response.status_code == 200, f"{test_case['name']} failed: {response.status_code} - {response.text}"
                    
                    response_data = response.json()
                    assert "amount_b" in response_data, "Response should contain amount_b"
                    assert isinstance(response_data["amount_b"], int), "amount_b should be an integer"
                    assert response_data["amount_b"] > 0, "amount_b should be positive"
                    
                    logger.info(safe_log(f"✅ {test_case['name']}: {response_data['amount_b']}"))
            
        except Exception as e:
            pytest.fail(f"Failed to test API endpoint: {e}")
    
    @pytest.mark.asyncio
    async def test_error_scenarios(self, test_app):
        """Test error scenarios with the API."""
        print("\n⚠️ Error Scenarios Test")
        print("=" * 50)
        
        try:
            error_test_cases = [
                {
                    "name": "Missing Fields",
                    "data": {"amount_a": 1000}  # Missing reserves
                },
                {
                    "name": "Zero Reserve A",
                    "data": {"amount_a": 1000, "reserve_a": 0, "reserve_b": 2000}
                },
                {
                    "name": "Zero Reserve B", 
                    "data": {"amount_a": 1000, "reserve_a": 2000, "reserve_b": 0}
                },
                {
                    "name": "Invalid Data Types",
                    "data": {"amount_a": "invalid", "reserve_a": 1000, "reserve_b": 2000}
                }
            ]
            
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=test_app), base_url="http://test") as client:
                for test_case in error_test_cases:
                    logger.info(safe_log(f"🧪 Running error test: {test_case['name']}"))
                    
                    response = await client.post("/exchange/quote", json=test_case["data"])
                    
                    # Error responses should be 4xx or 5xx
                    assert response.status_code >= 400, f"{test_case['name']}: Expected error status code, got {response.status_code}"
                    
                    # Verify error response structure
                    if response.headers.get("content-type", "").startswith("application/json"):
                        error_data = response.json()
                        assert "detail" in error_data or "message" in error_data, "Error response should contain details"
                    
                    logger.info(safe_log(f"✅ {test_case['name']}: Correctly returned {response.status_code}"))
            
        except Exception as e:
            pytest.fail(f"Failed to test error scenarios: {e}")
    
    @pytest.mark.asyncio
    async def test_realistic_defi_scenario(self, exchange_service_factory):
        """Test with realistic DeFi values using configured tokens."""
        print("\n🏦 Realistic DeFi Scenarios Test")
        print("=" * 50)
        
        # Create exchange service
        exchange_service = await exchange_service_factory()
        
        try:
            # Simulate realistic liquidity pool scenarios
            scenarios = [
                {
                    "name": "ETH/USDC Pool Simulation",
                    "description": "Simulating 1 ETH swap in ETH/USDC pool",
                    "amount_a": 1000000000000000000,  # 1 ETH (18 decimals)
                    "reserve_a": 1000000000000000000000,  # 1,000 ETH
                    "reserve_b": 2000000000000,  # 2,000,000 USDC (6 decimals, assuming 1 ETH = 2000 USDC)
                },
                {
                    "name": "Large Trade Simulation",
                    "description": "Simulating 100 token swap in large pool",
                    "amount_a": 100000000000000000000,  # 100 tokens
                    "reserve_a": 10000000000000000000000000,  # 10M tokens
                    "reserve_b": 5000000000000000000000000,   # 5M tokens
                },
                {
                    "name": "Small Trade Simulation", 
                    "description": "Simulating 0.1 token swap in small pool",
                    "amount_a": 100000000000000000,  # 0.1 tokens
                    "reserve_a": 100000000000000000000000,  # 100K tokens
                    "reserve_b": 200000000000000000000000,   # 200K tokens
                }
            ]
            
            for scenario in scenarios:
                logger.info(safe_log(f"🧪 Running: {scenario['name']}"))
                logger.info(f"   {scenario['description']}")
                
                quote_result = await exchange_service.quote(
                    scenario["amount_a"],
                    scenario["reserve_a"], 
                    scenario["reserve_b"]
                )
                
                # Verify result is reasonable
                assert quote_result > 0, f"{scenario['name']}: Quote result should be positive"
                assert isinstance(quote_result, int), f"{scenario['name']}: Quote result should be an integer"
                
                # Calculate expected result for comparison
                expected = (scenario["amount_a"] * scenario["reserve_b"]) // scenario["reserve_a"]
                
                # Allow for reasonable variance (within 10%)
                variance = abs(quote_result - expected) / expected
                assert variance < 0.1, f"{scenario['name']}: Quote variance too high: {variance:.4f}"
                
                # Calculate price impact
                price_before = scenario["reserve_b"] / scenario["reserve_a"]
                price_after = (scenario["reserve_b"] - quote_result) / (scenario["reserve_a"] + scenario["amount_a"])
                price_impact = abs(price_after - price_before) / price_before * 100
                
                logger.info(safe_log(f"✅ Quote Result: {quote_result}"))
                logger.info(safe_log(f"✅ Expected (simple): {expected}"))
                logger.info(safe_log(f"✅ Price Impact: {price_impact:.4f}%"))
                logger.info(safe_log(f"✅ Variance: {variance:.4f}"))
            
        except Exception as e:
            pytest.fail(f"Failed to test DeFi scenarios: {e}")


# Pytest markers for different test categories
pytestmark = [
    pytest.mark.integration
]


# Skip tests if blockchain is not available
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle blockchain availability."""
    for item in items:
        if "exchange_service_factory" in item.fixturenames:
            item.add_marker(pytest.mark.slow)


if __name__ == "__main__":
    # Run with pytest when executed directly
    pytest.main([__file__, "-v", "-s"])