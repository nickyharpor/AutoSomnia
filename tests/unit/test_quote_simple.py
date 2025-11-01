"""
Simple test for quote endpoint to verify the test infrastructure works.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import httpx

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.api.routes.exchange import router, get_exchange_service
from app.models.exchange_models import QuoteRequest, QuoteResponse
from app.services.somnia_exchange_service import SomniaExchangeService
from fastapi import FastAPI

# Create test app
app = FastAPI()
app.include_router(router)


class TestQuoteSimple:
    """Simple test class for quote endpoint."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock exchange service."""
        service = Mock(spec=SomniaExchangeService)
        service.quote = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_simple_quote_success(self, mock_service):
        """Test basic quote functionality."""
        # Arrange
        request_data = {
            "amount_a": 1000000000000000000,
            "reserve_a": 10000000000000000000000,
            "reserve_b": 5000000000000000000000
        }
        expected_quote = 500000000000000000
        mock_service.quote.return_value = expected_quote
        
        # Override dependency
        app.dependency_overrides[get_exchange_service] = lambda: mock_service
        
        try:
            # Act
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json=request_data)
            
            # Assert
            assert response.status_code == 200
            response_data = response.json()
            assert "amount_b" in response_data
            assert response_data["amount_b"] == expected_quote
            
            # Verify service was called
            mock_service.quote.assert_called_once_with(
                request_data["amount_a"],
                request_data["reserve_a"],
                request_data["reserve_b"]
            )
        finally:
            # Clean up
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_quote_validation_error(self):
        """Test validation error with missing fields."""
        invalid_request = {"amount_a": 1000}  # Missing reserves
        
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/exchange/quote", json=invalid_request)
        
        assert response.status_code == 422
        assert "detail" in response.json()
    
    def test_quote_models(self):
        """Test Pydantic models work correctly."""
        # Test request model
        request_data = {
            "amount_a": 1000000000000000000,
            "reserve_a": 10000000000000000000000,
            "reserve_b": 5000000000000000000000
        }
        request = QuoteRequest(**request_data)
        assert request.amount_a == 1000000000000000000
        
        # Test response model
        response_data = {"amount_b": 500000000000000000}
        response = QuoteResponse(**response_data)
        assert response.amount_b == 500000000000000000

    def test_quote_request_model(self):
        """Test QuoteRequest model creation and validation."""
        # Test valid request
        request_data = {
            "amount_a": 1000000000000000000,
            "reserve_a": 10000000000000000000000,
            "reserve_b": 5000000000000000000000
        }

        request = QuoteRequest(**request_data)

        assert request.amount_a == 1000000000000000000
        assert request.reserve_a == 10000000000000000000000
        assert request.reserve_b == 5000000000000000000000

    def test_quote_response_model(self):
        """Test QuoteResponse model creation and validation."""
        response_data = {"amount_b": 500000000000000000}

        response = QuoteResponse(**response_data)

        assert response.amount_b == 500000000000000000

    def test_quote_request_validation_error(self):
        """Test that invalid data raises validation error."""
        with pytest.raises(Exception):  # Pydantic validation error
            QuoteRequest(amount_a="invalid",
                         reserve_a=1000,
                         reserve_b=2000)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])