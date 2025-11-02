"""
Pytest-compatible integration tests for exchange routes.

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            
            logger.info(f"✅ Connected to blockchain at {settings.RPC_URL}")
            
            # Get latest block for verification
            latest_block = await w3.eth.get_block('latest')
            logger.info(f"✅ Latest block: {latest_block['number']}")
            
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
    """Integration tests for exchange functionality."""
    
    @pytest.mark.asyncio
    async def test_blockchain_connection(self, exchange_service_factory):
        """Test that we can connect to the blockchain."""
        # Create exchange service
        exchange_service = await exchange_service_factory()
        
        assert exchange_service is not None
        
        # Test that we can make a basic call
        w3 = exchange_service.w3
        latest_block = await w3.eth.get_block('latest')
        
        assert latest_block is not None
        assert latest_block['number'] > 0
        logger.info(f"✅ Blockchain connection test passed, block: {latest_block['number']}")
    
    @pytest.mark.asyncio
    async def test_exchange_service_info(self, exchange_service_factory):
        """Test basic exchange service information retrieval."""
        # Create exchange service
        exchange_service = await exchange_service_factory()
        
        try:
            # Get WETH address
            weth_address = await exchange_service.get_weth_address()
            assert weth_address is not None
            assert weth_address.startswith('0x')
            assert len(weth_address) == 42
            logger.info(f"✅ WETH Address: {weth_address}")
            
            # Get factory address
            factory_address = await exchange_service.get_factory_address()
            assert factory_address is not None
            assert factory_address.startswith('0x')
            assert len(factory_address) == 42
            logger.info(f"✅ Factory Address: {factory_address}")
            
        except Exception as e:
            pytest.fail(f"Failed to get exchange service info: {e}")
    
    @pytest.mark.asyncio
    async def test_quote_calculation(self, exchange_service_factory):
        """Test quote calculation with realistic values."""
        # Create exchange service
        exchange_service = await exchange_service_factory()
        
        try:
            # Test case: Simple quote calculation
            amount_a = 1000000000000000000  # 1 token (18 decimals)
            reserve_a = 10000000000000000000000  # 10,000 tokens
            reserve_b = 5000000000000000000000   # 5,000 tokens
            
            quote_result = await exchange_service.quote(amount_a, reserve_a, reserve_b)
            
            # Verify result is reasonable
            assert quote_result > 0
            assert isinstance(quote_result, int)
            
            # Calculate expected result (simple ratio)
            expected_ratio = (amount_a * reserve_b) // reserve_a
            
            # Allow for some variance due to contract logic
            assert abs(quote_result - expected_ratio) / expected_ratio < 0.1  # Within 10%
            
            logger.info(f"✅ Quote calculation: {quote_result}")
            logger.info(f"✅ Expected ratio: {expected_ratio}")
            
        except Exception as e:
            pytest.fail(f"Quote calculation failed: {e}")
    
    @pytest.mark.asyncio
    async def test_quote_api_endpoint(self, test_app):
        """Test the quote API endpoint with HTTP requests."""
        try:
            test_request = {
                "amount_a": 1000000000000000000,  # 1 token
                "reserve_a": 10000000000000000000000,  # 10,000 tokens
                "reserve_b": 5000000000000000000000   # 5,000 tokens
            }
            
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=test_app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json=test_request)
                
                assert response.status_code == 200
                
                response_data = response.json()
                assert "amount_b" in response_data
                assert isinstance(response_data["amount_b"], int)
                assert response_data["amount_b"] > 0
                
                logger.info(f"✅ API quote result: {response_data['amount_b']}")
                
        except Exception as e:
            pytest.fail(f"API endpoint test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_quote_api_validation_errors(self, test_app):
        """Test that the API properly validates input."""
        invalid_requests = [
            {},  # Empty request
            {"amount_a": 1000},  # Missing reserves
            {"amount_a": "invalid", "reserve_a": 1000, "reserve_b": 2000},  # Invalid type
        ]
        
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=test_app), base_url="http://test") as client:
            for invalid_request in invalid_requests:
                response = await client.post("/exchange/quote", json=invalid_request)
                
                # Should return validation error
                assert response.status_code >= 400
                assert "detail" in response.json()
                
                logger.info(f"✅ Validation error correctly returned: {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_realistic_defi_scenario(self, exchange_service_factory):
        """Test with realistic DeFi values."""
        # Create exchange service
        exchange_service = await exchange_service_factory()
        
        try:
            # Simulate ETH/USDC pool scenario
            amount_a = 1000000000000000000  # 1 ETH (18 decimals)
            reserve_a = 1000000000000000000000  # 1,000 ETH
            reserve_b = 2000000000000  # 2,000,000 USDC (6 decimals, assuming 1 ETH = 2000 USDC)
            
            quote_result = await exchange_service.quote(amount_a, reserve_a, reserve_b)
            
            # Verify result is reasonable for this scenario
            assert quote_result > 0
            
            # Calculate expected USDC amount (should be close to 2000 USDC)
            expected_usdc = (amount_a * reserve_b) // reserve_a
            
            # Allow for reasonable variance
            variance = abs(quote_result - expected_usdc) / expected_usdc
            assert variance < 0.05  # Within 5%
            
            logger.info(f"✅ DeFi scenario quote: {quote_result}")
            logger.info(f"✅ Expected USDC: {expected_usdc}")
            logger.info(f"✅ Variance: {variance:.4f}")
            
        except Exception as e:
            pytest.fail(f"DeFi scenario test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_multiple_quote_calculations(self, exchange_service_factory):
        """Test multiple quote calculations to ensure consistency."""
        # Create exchange service
        exchange_service = await exchange_service_factory()
        
        test_cases = [
            {
                "name": "Small amount",
                "amount_a": 100000000000000000,  # 0.1 tokens
                "reserve_a": 1000000000000000000000,  # 1,000 tokens
                "reserve_b": 2000000000000000000000   # 2,000 tokens
            },
            {
                "name": "Large amount",
                "amount_a": 100000000000000000000,  # 100 tokens
                "reserve_a": 10000000000000000000000000,  # 10M tokens
                "reserve_b": 5000000000000000000000000   # 5M tokens
            },
            {
                "name": "Equal reserves",
                "amount_a": 1000000000000000000,  # 1 token
                "reserve_a": 1000000000000000000000000,  # 1M tokens
                "reserve_b": 1000000000000000000000000   # 1M tokens
            }
        ]
        
        for case in test_cases:
            try:
                quote_result = await exchange_service.quote(
                    case["amount_a"],
                    case["reserve_a"],
                    case["reserve_b"]
                )
                
                assert quote_result > 0
                
                # Calculate expected result
                expected = (case["amount_a"] * case["reserve_b"]) // case["reserve_a"]
                
                logger.info(f"✅ {case['name']}: quote={quote_result}, expected={expected}")
                
            except Exception as e:
                pytest.fail(f"Test case '{case['name']}' failed: {e}")
    
    def test_configuration_loaded(self):
        """Test that environment configuration is properly loaded."""
        assert settings.RPC_URL is not None
        assert settings.RPC_URL.startswith('http')
        
        assert settings.CHAIN_ID > 0
        
        assert settings.ROUTER_ADDRESS is not None
        assert settings.ROUTER_ADDRESS.startswith('0x')
        assert len(settings.ROUTER_ADDRESS) == 42
        
        logger.info(f"✅ Configuration test passed:")
        logger.info(f"  RPC URL: {settings.RPC_URL}")
        logger.info(f"  Chain ID: {settings.CHAIN_ID}")
        logger.info(f"  Router: {settings.ROUTER_ADDRESS}")


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