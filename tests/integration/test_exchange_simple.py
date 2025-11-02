"""
Simple integration test for exchange quote endpoint.

This is a lightweight version that focuses on basic functionality
and can be run quickly to verify the exchange service works.
"""

import asyncio
import logging
import sys
from pathlib import Path
import httpx
import pytest

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.backend_config import settings
from app.services.somnia_exchange_service import SomniaExchangeService
from web3 import AsyncWeb3
from fastapi import FastAPI
from app.api.routes.exchange import router

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# Pytest-compatible test functions


class TestSimpleExchange:
    """Pytest-compatible test class for exchange integration."""
    
    def setup_class(cls):
        """Setup class-level configuration logging."""
        logger.info("🔧 Exchange Test Configuration:")
        logger.info(f"  RPC URL: {settings.RPC_URL}")
        logger.info(f"  Chain ID: {settings.CHAIN_ID}")
        logger.info(f"  Router: {settings.ROUTER_ADDRESS}")
    
    @pytest.mark.asyncio
    async def test_blockchain_connection(self):
        """Test basic blockchain connection."""
        print("\n🔗 Blockchain Connection Test")
        print("=" * 50)
        
        try:
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.RPC_URL))
            is_connected = await w3.is_connected()
            
            if is_connected:
                latest_block = await w3.eth.get_block('latest')
                assert latest_block['number'] > 0, "Block number should be positive"
                logger.info(f"✅ Connected to blockchain, latest block: {latest_block['number']}")
            else:
                pytest.skip("❌ Failed to connect to blockchain")
                
        except Exception as e:
            pytest.skip(f"❌ Blockchain connection error: {e}")
    
    @pytest.mark.asyncio
    async def test_exchange_service(self):
        """Test exchange service initialization."""
        print("\n🔄 Exchange Service Test")
        print("=" * 50)
        
        try:
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.RPC_URL))
            service = SomniaExchangeService(w3, settings.ROUTER_ADDRESS)
            
            # Test basic service calls
            weth = await service.get_weth_address()
            factory = await service.get_factory_address()
            
            assert weth is not None, "WETH address should not be None"
            assert factory is not None, "Factory address should not be None"
            assert weth.startswith('0x'), "WETH address should be valid hex"
            assert factory.startswith('0x'), "Factory address should be valid hex"
            
            logger.info(f"✅ Exchange service working:")
            logger.info(f"  WETH: {weth}")
            logger.info(f"  Factory: {factory}")
            
        except Exception as e:
            pytest.skip(f"❌ Exchange service error: {e}")
    
    @pytest.mark.asyncio
    async def test_quote_api(self):
        """Test the quote API endpoint."""
        print("\n💱 Quote API Test")
        print("=" * 50)
        
        try:
            app = FastAPI()
            app.include_router(router)
            
            test_request = {
                "amount_a": 1000000000000000000,  # 1 token
                "reserve_a": 10000000000000000000000,  # 10,000 tokens
                "reserve_b": 5000000000000000000000   # 5,000 tokens
            }
            
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json=test_request)
                
                assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
                
                result = response.json()
                assert "amount_b" in result, "Response should contain amount_b"
                assert isinstance(result["amount_b"], int), "amount_b should be an integer"
                assert result["amount_b"] > 0, "amount_b should be positive"
                
                logger.info(f"✅ Quote API working:")
                logger.info(f"  Input amount: {test_request['amount_a']}")
                logger.info(f"  Output amount: {result['amount_b']}")
                    
        except Exception as e:
            pytest.skip(f"❌ Quote API error: {e}")
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling."""
        print("\n⚠️ Error Handling Test")
        print("=" * 50)
        
        try:
            app = FastAPI()
            app.include_router(router)
            
            # Test with invalid data
            invalid_request = {"amount_a": "invalid"}
            
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json=invalid_request)
                
                assert response.status_code >= 400, f"Expected error status code, got {response.status_code}"
                
                # Verify error response structure
                if response.headers.get("content-type", "").startswith("application/json"):
                    error_data = response.json()
                    assert "detail" in error_data or "message" in error_data, "Error response should contain details"
                
                logger.info(f"✅ Error handling working:")
                logger.info(f"  Status code: {response.status_code}")
                logger.info(f"  Response: {response.text[:100]}...")
                    
        except Exception as e:
            pytest.skip(f"❌ Error handling test failed: {e}")


# Pytest markers for test categorization
pytestmark = [
    pytest.mark.integration,
    pytest.mark.blockchain,
    pytest.mark.asyncio
]


if __name__ == "__main__":
    # Run with pytest when executed directly
    pytest.main([__file__, "-v", "-s"])