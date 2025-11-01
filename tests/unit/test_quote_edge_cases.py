"""
Simple tests for edge cases that were failing.
"""

import pytest
import httpx
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.api.routes.exchange import router, get_exchange_service
from app.services.somnia_exchange_service import SomniaExchangeService
from fastapi import FastAPI

# Create test app
app = FastAPI()
app.include_router(router)


class TestQuoteEdgeCases:
    """Test edge cases that were previously failing."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock exchange service."""
        service = Mock(spec=SomniaExchangeService)
        service.quote = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_invalid_data_handling(self):
        """Test that invalid data is handled gracefully."""
        invalid_request = {"amount_a": "not_a_number", "reserve_a": 1000, "reserve_b": 2000}
        
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/exchange/quote", json=invalid_request)
            
            # Should get either validation error (422) or service error (500)
            assert response.status_code in [422, 500]
            assert "detail" in response.json()
    
    @pytest.mark.asyncio
    async def test_service_error_handling(self, mock_service):
        """Test that service errors are handled properly."""
        # Make service raise an exception
        mock_service.quote.side_effect = Exception("Service error")
        
        app.dependency_overrides[get_exchange_service] = lambda: mock_service
        
        try:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json={
                    "amount_a": 1000, "reserve_a": 1000, "reserve_b": 2000
                })
            
            assert response.status_code == 500
            response_data = response.json()
            assert "detail" in response_data
            assert "Error getting quote" in response_data["detail"]
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_successful_quote(self, mock_service):
        """Test that successful quotes work correctly."""
        expected_quote = 500000000000000000
        mock_service.quote.return_value = expected_quote
        
        app.dependency_overrides[get_exchange_service] = lambda: mock_service
        
        try:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json={
                    "amount_a": 1000000000000000000,
                    "reserve_a": 10000000000000000000000,
                    "reserve_b": 5000000000000000000000
                })
            
            assert response.status_code == 200
            response_data = response.json()
            assert "amount_b" in response_data
            assert response_data["amount_b"] == expected_quote
        finally:
            app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])