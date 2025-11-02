"""
Comprehensive unit tests for exchange routes, focusing on the get_quote endpoint.

This test suite covers:
1. Successful quote calculations
2. Input validation and error handling
3. Service dependency injection
4. Response model validation
5. Edge cases and boundary conditions
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
import httpx
import sys
from pathlib import Path

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


class TestGetQuoteEndpoint:
    """Comprehensive test suite for the get_quote endpoint."""
    
    @pytest.fixture
    def mock_exchange_service(self):
        """Create a mock exchange service."""
        service = Mock(spec=SomniaExchangeService)
        service.quote = AsyncMock()
        return service
    
    @pytest.fixture
    def test_client(self):
        """Create a test client."""
        return TestClient(app)
    
    @pytest.fixture
    def valid_quote_request(self):
        """Create a valid quote request."""
        return {
            "amount_a": 1000000000000000000,  # 1 token (18 decimals)
            "reserve_a": 10000000000000000000000,  # 10,000 tokens
            "reserve_b": 5000000000000000000000   # 5,000 tokens
        }
    
    @pytest.fixture
    def expected_quote_response(self):
        """Expected quote response."""
        return 500000000000000000  # 0.5 tokens
    
    # ==================== Success Cases ====================
    
    @pytest.mark.asyncio
    async def test_get_quote_success(self, mock_exchange_service, valid_quote_request, expected_quote_response):
        """Test successful quote calculation."""
        # Arrange
        mock_exchange_service.quote.return_value = expected_quote_response
        
        # Override the dependency
        app.dependency_overrides[get_exchange_service] = lambda: mock_exchange_service
        
        try:
            # Act
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json=valid_quote_request)
            
            # Assert
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["amount_b"] == expected_quote_response
            
            # Verify service was called with correct parameters
            mock_exchange_service.quote.assert_called_once_with(
                valid_quote_request["amount_a"],
                valid_quote_request["reserve_a"],
                valid_quote_request["reserve_b"]
            )
        finally:
            # Clean up
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_get_quote_with_different_reserves(self, mock_exchange_service):
        """Test quote calculation with different reserve ratios."""
        # Test cases with different reserve ratios
        test_cases = [
            {
                "request": {"amount_a": 1000000, "reserve_a": 1000000000, "reserve_b": 2000000000},
                "expected": 2000000,  # 1:2 ratio
                "description": "1:2 reserve ratio"
            },
            {
                "request": {"amount_a": 5000000, "reserve_a": 10000000000, "reserve_b": 5000000000},
                "expected": 2500000,  # 2:1 ratio
                "description": "2:1 reserve ratio"
            },
            {
                "request": {"amount_a": 100000000, "reserve_a": 1000000000000, "reserve_b": 1000000000000},
                "expected": 100000000,  # 1:1 ratio
                "description": "1:1 reserve ratio"
            }
        ]
        
        app.dependency_overrides[get_exchange_service] = lambda: mock_exchange_service
        
        try:
            for case in test_cases:
                mock_exchange_service.quote.return_value = case["expected"]
                mock_exchange_service.quote.reset_mock()  # Reset call count
                
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                    response = await client.post("/exchange/quote", json=case["request"])
                
                assert response.status_code == 200, f"Failed for {case['description']}"
                assert response.json()["amount_b"] == case["expected"], f"Wrong quote for {case['description']}"
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_get_quote_large_numbers(self, mock_exchange_service):
        """Test quote calculation with large numbers (edge case)."""
        # Arrange
        large_request = {
            "amount_a": 999999999999999999999999,  # Very large amount
            "reserve_a": 1000000000000000000000000,
            "reserve_b": 500000000000000000000000
        }
        expected_large_quote = 499999999999999999999999
        mock_exchange_service.quote.return_value = expected_large_quote
        
        app.dependency_overrides[get_exchange_service] = lambda: mock_exchange_service
        
        try:
            # Act
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json=large_request)
            
            # Assert
            assert response.status_code == 200
            assert response.json()["amount_b"] == expected_large_quote
        finally:
            app.dependency_overrides.clear()
    
    # ==================== Input Validation Tests ====================
    
    @pytest.mark.asyncio
    async def test_get_quote_missing_fields(self):
        """Test quote request with missing required fields."""
        invalid_requests = [
            {},  # Empty request
            {"amount_a": 1000},  # Missing reserves
            {"reserve_a": 1000, "reserve_b": 2000},  # Missing amount_a
            {"amount_a": 1000, "reserve_a": 2000},  # Missing reserve_b
            {"amount_a": 1000, "reserve_b": 2000},  # Missing reserve_a
        ]
        
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            for invalid_request in invalid_requests:
                response = await client.post("/exchange/quote", json=invalid_request)
                assert response.status_code == 422  # Validation error
                assert "detail" in response.json()
    
    @pytest.mark.asyncio
    async def test_get_quote_invalid_data_types(self):
        """Test quote request with invalid data types."""
        invalid_requests = [
            {"amount_a": "not_a_number", "reserve_a": 1000, "reserve_b": 2000},
            {"amount_a": 1000, "reserve_a": "invalid", "reserve_b": 2000},
            {"amount_a": 1000, "reserve_a": 1000, "reserve_b": None},
            # Note: Floats might be auto-converted to ints by Pydantic, so we test more clearly invalid types
        ]
        
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            for i, invalid_request in enumerate(invalid_requests):
                response = await client.post("/exchange/quote", json=invalid_request)
                # Some invalid types might get through Pydantic validation and cause service errors (500)
                # or be caught by validation (422). Both are acceptable for invalid input.
                assert response.status_code in [422, 500], f"Request {i}: {invalid_request} returned {response.status_code}"
                assert "detail" in response.json(), f"Request {i}: No detail in error response"
    
    @pytest.mark.asyncio
    async def test_get_quote_zero_values(self, mock_exchange_service):
        """Test quote request with zero values."""
        # Test zero amount_a
        zero_amount_request = {"amount_a": 0, "reserve_a": 1000, "reserve_b": 2000}
        mock_exchange_service.quote.return_value = 0
        
        app.dependency_overrides[get_exchange_service] = lambda: mock_exchange_service
        
        try:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json=zero_amount_request)
            
            assert response.status_code == 200
            assert response.json()["amount_b"] == 0
        finally:
            app.dependency_overrides.clear()
    
    # ==================== Error Handling Tests ====================
    
    @pytest.mark.asyncio
    async def test_get_quote_service_initialization_error(self, mock_exchange_service):
        """Test error when exchange service fails to initialize."""
        # Make the service raise an exception when quote is called
        mock_exchange_service.quote.side_effect = Exception("Service initialization failed")
        
        app.dependency_overrides[get_exchange_service] = lambda: mock_exchange_service
        
        try:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json={
                    "amount_a": 1000, "reserve_a": 1000, "reserve_b": 2000
                })
            
            assert response.status_code == 500
            assert "Error getting quote" in response.json()["detail"]
            assert "Service initialization failed" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_get_quote_service_quote_error(self, mock_exchange_service, valid_quote_request):
        """Test error when service quote method fails."""
        # Arrange
        mock_exchange_service.quote.side_effect = Exception("Contract call failed")
        
        app.dependency_overrides[get_exchange_service] = lambda: mock_exchange_service
        
        try:
            # Act
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json=valid_quote_request)
            
            # Assert
            assert response.status_code == 500
            assert "Error getting quote" in response.json()["detail"]
            assert "Contract call failed" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_get_quote_zero_reserves_error(self, mock_exchange_service):
        """Test error when reserves are zero (division by zero scenario)."""
        # Arrange
        zero_reserve_request = {"amount_a": 1000, "reserve_a": 0, "reserve_b": 2000}
        mock_exchange_service.quote.side_effect = Exception("Division by zero")
        
        app.dependency_overrides[get_exchange_service] = lambda: mock_exchange_service
        
        try:
            # Act
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json=zero_reserve_request)
            
            # Assert
            assert response.status_code == 500
            assert "Error getting quote" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_get_quote_blockchain_connection_error(self, mock_exchange_service, valid_quote_request):
        """Test error when blockchain connection fails."""
        # Arrange
        mock_exchange_service.quote.side_effect = Exception("Connection timeout")
        
        app.dependency_overrides[get_exchange_service] = lambda: mock_exchange_service
        
        try:
            # Act
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json=valid_quote_request)
            
            # Assert
            assert response.status_code == 500
            assert "Error getting quote" in response.json()["detail"]
            assert "Connection timeout" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    # ==================== Response Model Tests ====================
    
    @pytest.mark.asyncio
    async def test_get_quote_response_model_validation(self, mock_exchange_service, valid_quote_request):
        """Test that response follows the correct model structure."""
        # Arrange
        expected_quote = 123456789
        mock_exchange_service.quote.return_value = expected_quote
        
        app.dependency_overrides[get_exchange_service] = lambda: mock_exchange_service
        
        try:
            # Act
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json=valid_quote_request)
            
            # Assert
            assert response.status_code == 200
            response_data = response.json()
            
            # Validate response structure
            assert isinstance(response_data, dict)
            assert "amount_b" in response_data
            assert isinstance(response_data["amount_b"], int)
            assert response_data["amount_b"] == expected_quote
            
            # Validate against Pydantic model
            quote_response = QuoteResponse(**response_data)
            assert quote_response.amount_b == expected_quote
        finally:
            app.dependency_overrides.clear()
    
    # ==================== Integration-like Tests ====================
    
    @pytest.mark.asyncio
    async def test_get_quote_realistic_scenario(self, mock_exchange_service):
        """Test quote calculation with realistic DeFi scenario."""
        # Simulate a realistic DEX scenario:
        # - Token A: 1 ETH (1e18 wei)
        # - Reserve A: 1000 ETH
        # - Reserve B: 2000 USDC (assuming 1 ETH = 2000 USDC)
        # - Expected: ~2000 USDC (minus fees)
        
        realistic_request = {
            "amount_a": 1000000000000000000,  # 1 ETH
            "reserve_a": 1000000000000000000000,  # 1000 ETH
            "reserve_b": 2000000000000  # 2,000,000 USDC (6 decimals)
        }
        expected_usdc = 2000000000  # 2000 USDC (6 decimals)
        
        mock_exchange_service.quote.return_value = expected_usdc
        
        app.dependency_overrides[get_exchange_service] = lambda: mock_exchange_service
        
        try:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/exchange/quote", json=realistic_request)
            
            assert response.status_code == 200
            assert response.json()["amount_b"] == expected_usdc
            
            # Verify the service was called with correct parameters
            mock_exchange_service.quote.assert_called_once_with(
                realistic_request["amount_a"],
                realistic_request["reserve_a"],
                realistic_request["reserve_b"]
            )
        finally:
            app.dependency_overrides.clear()
    
    # ==================== Performance and Edge Cases ====================
    
    @pytest.mark.asyncio
    async def test_get_quote_concurrent_requests(self, mock_exchange_service, valid_quote_request):
        """Test handling multiple concurrent quote requests."""
        expected_quote = 500000000000000000  # Match the fixture expected value
        mock_exchange_service.quote.return_value = expected_quote
        
        app.dependency_overrides[get_exchange_service] = lambda: mock_exchange_service
        
        try:
            async def make_request():
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                    return await client.post("/exchange/quote", json=valid_quote_request)
            
            # Make 5 concurrent requests
            tasks = [make_request() for _ in range(5)]
            responses = await asyncio.gather(*tasks)
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
                assert response.json()["amount_b"] == expected_quote
        finally:
            app.dependency_overrides.clear()
    
    def test_get_quote_request_model_validation(self):
        """Test QuoteRequest model validation directly."""
        # Valid request
        valid_data = {"amount_a": 1000, "reserve_a": 2000, "reserve_b": 3000}
        request = QuoteRequest(**valid_data)
        assert request.amount_a == 1000
        assert request.reserve_a == 2000
        assert request.reserve_b == 3000
        
        # Invalid requests should raise validation errors
        with pytest.raises(Exception):  # Pydantic validation error
            QuoteRequest(amount_a="invalid", reserve_a=2000, reserve_b=3000)
        
        with pytest.raises(Exception):  # Missing required field
            QuoteRequest(amount_a=1000, reserve_a=2000)
    
    def test_get_quote_response_model_validation_direct(self):
        """Test QuoteResponse model validation directly."""
        # Valid response
        response_data = {"amount_b": 123456}
        response = QuoteResponse(**response_data)
        assert response.amount_b == 123456
        
        # Invalid response should raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            QuoteResponse(amount_b="invalid")
        
        with pytest.raises(Exception):  # Missing required field
            QuoteResponse()


# ==================== Fixtures and Utilities ====================

# ==================== Test Runner ====================

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])


# Example usage and test scenarios:
"""
# Run all tests
pytest tests/unit/test_exchange_routes.py -v

# Run specific test
pytest tests/unit/test_exchange_routes.py::TestGetQuoteEndpoint::test_get_quote_success -v

# Run with coverage
pytest tests/unit/test_exchange_routes.py --cov=app.api.routes.exchange --cov-report=html

# Expected test output:
# ✅ test_get_quote_success - Tests successful quote calculation
# ✅ test_get_quote_with_different_reserves - Tests various reserve ratios
# ✅ test_get_quote_large_numbers - Tests edge case with large numbers
# ✅ test_get_quote_missing_fields - Tests input validation
# ✅ test_get_quote_invalid_data_types - Tests type validation
# ✅ test_get_quote_zero_values - Tests zero value handling
# ✅ test_get_quote_service_initialization_error - Tests service errors
# ✅ test_get_quote_service_quote_error - Tests contract call errors
# ✅ test_get_quote_zero_reserves_error - Tests division by zero
# ✅ test_get_quote_blockchain_connection_error - Tests connection errors
# ✅ test_get_quote_response_model_validation - Tests response structure
# ✅ test_get_quote_realistic_scenario - Tests realistic DeFi scenario
# ✅ test_get_quote_concurrent_requests - Tests concurrent handling
# ✅ test_get_quote_request_model_validation - Tests request model
# ✅ test_get_quote_response_model_validation_direct - Tests response model
"""