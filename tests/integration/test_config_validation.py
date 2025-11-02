"""
Simple pytest-compatible test for configuration validation.

This test validates that the environment configuration is loaded correctly
and can be run with pytest.
"""

import pytest
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.backend_config import settings


class TestConfigValidation:
    """Test configuration loading and validation."""
    
    def test_rpc_url_configured(self):
        """Test that RPC URL is configured."""
        assert settings.RPC_URL is not None
        assert isinstance(settings.RPC_URL, str)
        assert settings.RPC_URL.startswith('http')
        assert len(settings.RPC_URL) > 10
    
    def test_chain_id_configured(self):
        """Test that Chain ID is configured."""
        assert settings.CHAIN_ID is not None
        assert isinstance(settings.CHAIN_ID, int)
        assert settings.CHAIN_ID > 0
    
    def test_router_address_configured(self):
        """Test that Router address is configured."""
        assert settings.ROUTER_ADDRESS is not None
        assert isinstance(settings.ROUTER_ADDRESS, str)
        assert settings.ROUTER_ADDRESS.startswith('0x')
        assert len(settings.ROUTER_ADDRESS) == 42
    
    def test_token_addresses_configured(self):
        """Test that token addresses are configured."""
        assert settings.WSTT is not None
        assert isinstance(settings.WSTT, str)
        assert settings.WSTT.startswith('0x')
        assert len(settings.WSTT) == 42
        
        assert settings.SUSDT is not None
        assert isinstance(settings.SUSDT, str)
        assert settings.SUSDT.startswith('0x')
        assert len(settings.SUSDT) == 42
    
    def test_private_key_configured(self):
        """Test that private key is configured."""
        assert settings.PRIVATE_KEY is not None
        assert isinstance(settings.PRIVATE_KEY, str)
        assert settings.PRIVATE_KEY.startswith('0x')
        assert len(settings.PRIVATE_KEY) == 66  # 0x + 64 hex chars
    
    def test_address_configured(self):
        """Test that address is configured."""
        assert settings.ADDRESS is not None
        assert isinstance(settings.ADDRESS, str)
        assert settings.ADDRESS.startswith('0x')
        assert len(settings.ADDRESS) == 42
    
    def test_database_configured(self):
        """Test that database configuration is present."""
        assert settings.MONGODB_URL is not None
        assert isinstance(settings.MONGODB_URL, str)
        assert len(settings.MONGODB_URL) > 5
        
        assert settings.DATABASE_NAME is not None
        assert isinstance(settings.DATABASE_NAME, str)
        assert len(settings.DATABASE_NAME) > 0
    
    def test_server_configuration(self):
        """Test server configuration."""
        assert settings.HOST is not None
        assert isinstance(settings.HOST, str)
        
        assert settings.PORT is not None
        assert isinstance(settings.PORT, int)
        assert 1000 <= settings.PORT <= 65535
    
    def test_gas_limit_configured(self):
        """Test that gas limit is reasonable."""
        assert settings.GAS_LIMIT is not None
        assert isinstance(settings.GAS_LIMIT, int)
        assert settings.GAS_LIMIT > 21000  # Minimum for ETH transfer
        assert settings.GAS_LIMIT < 10000000  # Reasonable upper bound
    
    def test_configuration_summary(self):
        """Test that prints configuration summary."""
        print("\n🔧 Configuration Summary:")
        print(f"  RPC URL: {settings.RPC_URL}")
        print(f"  Chain ID: {settings.CHAIN_ID}")
        print(f"  Router: {settings.ROUTER_ADDRESS}")
        print(f"  WSTT: {settings.WSTT}")
        print(f"  SUSDT: {settings.SUSDT}")
        print(f"  Database: {settings.DATABASE_NAME}")
        print(f"  Host: {settings.HOST}:{settings.PORT}")
        
        # This test always passes, it's just for information
        assert True


# Pytest markers
pytestmark = pytest.mark.integration


if __name__ == "__main__":
    # Run with pytest when executed directly
    pytest.main([__file__, "-v"])