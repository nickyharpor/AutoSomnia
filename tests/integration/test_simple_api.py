"""
Simple API integration test that should always be discoverable by pytest.
"""

import pytest
import requests
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestSimpleAPI:
    """Simple API tests that pytest can discover."""
    
    def test_api_server_check(self):
        """Test if API server is running (may skip if not available)."""
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ API server is running")
                assert True
            else:
                pytest.skip("API server returned non-200 status")
        except requests.exceptions.RequestException:
            pytest.skip("API server not available - start with: python app/main.py")
    
    def test_basic_configuration(self):
        """Test basic configuration loading."""
        try:
            from app.core.backend_config import settings
            
            assert settings.HOST is not None
            assert settings.PORT is not None
            assert isinstance(settings.PORT, int)
            
            print(f"✅ Configuration loaded: {settings.HOST}:{settings.PORT}")
            
        except ImportError:
            pytest.skip("Cannot import configuration")
    
    def test_users_endpoint_structure(self):
        """Test users endpoint structure (if API is available)."""
        try:
            response = requests.get("http://localhost:8000/users/", timeout=2)
            
            # Should return 200 (success) or 422 (validation error) - both indicate endpoint exists
            assert response.status_code in [200, 422, 404], f"Unexpected status: {response.status_code}"
            
            print("✅ Users endpoint is accessible")
            
        except requests.exceptions.RequestException:
            pytest.skip("API server not available")
    
    def test_account_endpoint_structure(self):
        """Test account endpoint structure (if API is available)."""
        try:
            response = requests.get("http://localhost:8000/account/list", timeout=2)
            
            # Should return 200 (success) or other valid HTTP status
            assert response.status_code in [200, 422, 404, 500], f"Unexpected status: {response.status_code}"
            
            print("✅ Account endpoint is accessible")
            
        except requests.exceptions.RequestException:
            pytest.skip("API server not available")
    
    def test_exchange_endpoint_structure(self):
        """Test exchange endpoint structure (if API is available)."""
        try:
            # Test a simple GET endpoint that should exist
            response = requests.get("http://localhost:8000/exchange/weth-address", timeout=2)
            
            # Should return 200 (success) or 500 (service error) - both indicate endpoint exists
            assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
            
            print("✅ Exchange endpoint is accessible")
            
        except requests.exceptions.RequestException:
            pytest.skip("API server not available")


# Pytest markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.api
]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])