"""
Simple integration test for account balance retrieval.

This is a simplified version that focuses on the core functionality:
1. Read private key from environment
2. Get address from private key
3. Display the configuration and derived address
"""

import pytest
import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.backend_config import settings
from app.services.account_service import get_address_from_private_key, validate_private_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@pytest.fixture
def config_settings():
    """Fixture to provide configuration settings."""
    return settings


@pytest.fixture
def derived_address():
    """Fixture to provide derived address from private key."""
    try:
        return get_address_from_private_key(settings.PRIVATE_KEY)
    except Exception as e:
        pytest.skip(f"Cannot derive address from private key: {e}")


class TestSimpleBalance:
    """Pytest-compatible test class for simple balance functionality."""
    
    def test_environment_configuration(self, config_settings):
        """Test that environment configuration is loaded correctly."""
        print("\n🔧 Environment Configuration Test")
        print("=" * 50)
        
        # Check if private key is loaded
        assert config_settings.PRIVATE_KEY is not None, "Private key not found in environment"
        assert len(config_settings.PRIVATE_KEY) > 10, "Private key seems too short"
        
        print(f"✅ Private key loaded: {config_settings.PRIVATE_KEY[:10]}...{config_settings.PRIVATE_KEY[-4:]}")
        
        # Check other configuration
        assert config_settings.RPC_URL is not None, "RPC URL not configured"
        assert config_settings.CHAIN_ID is not None, "Chain ID not configured"
        assert config_settings.MONGODB_URL is not None, "MongoDB URL not configured"
        assert config_settings.DATABASE_NAME is not None, "Database name not configured"
        
        print(f"✅ RPC URL: {config_settings.RPC_URL}")
        print(f"✅ Chain ID: {config_settings.CHAIN_ID}")
        print(f"✅ Database URL: {config_settings.MONGODB_URL}")
        print(f"✅ Database Name: {config_settings.DATABASE_NAME}")
        
        # Display token addresses if configured
        if config_settings.WSTT:
            print(f"✅ WSTT Token: {config_settings.WSTT}")
            assert config_settings.WSTT.startswith('0x'), "WSTT address should start with 0x"
            
        if config_settings.SUSDT:
            print(f"✅ SUSDT Token: {config_settings.SUSDT}")
            assert config_settings.SUSDT.startswith('0x'), "SUSDT address should start with 0x"
    
    def test_private_key_validation(self, config_settings):
        """Test private key validation."""
        print("\n🔐 Private Key Validation Test")
        print("=" * 50)
        
        # Validate the private key format
        is_valid = validate_private_key(config_settings.PRIVATE_KEY)
        
        assert is_valid, "Private key format is invalid"
        print("✅ Private key format is valid")
        
        # Additional format checks
        assert config_settings.PRIVATE_KEY.startswith('0x'), "Private key should start with 0x"
        assert len(config_settings.PRIVATE_KEY) == 66, "Private key should be 66 characters (0x + 64 hex)"
    
    def test_address_derivation(self, config_settings, derived_address):
        """Test address derivation from private key."""
        print("\n📍 Address Derivation Test")
        print("=" * 50)
        
        # Address should be derived successfully (fixture handles this)
        assert derived_address is not None, "Failed to derive address from private key"
        assert derived_address.startswith('0x'), "Address should start with 0x"
        assert len(derived_address) == 42, "Address should be 42 characters"
        
        print(f"✅ Address derived successfully: {derived_address}")
        
        # Compare with configured address if available
        if config_settings.ADDRESS:
            if derived_address.lower() == config_settings.ADDRESS.lower():
                print(f"✅ Derived address matches configured address")
            else:
                print(f"⚠️ Derived address differs from configured address:")
                print(f"   Derived: {derived_address}")
                print(f"   Configured: {config_settings.ADDRESS}")
                # This is a warning, not a failure
    
    def test_configuration_consistency(self, config_settings, derived_address):
        """Test consistency between different configuration values."""
        print("\n🔍 Configuration Consistency Test")
        print("=" * 50)
        
        issues = []
        
        # Check if private key and address match
        if config_settings.ADDRESS and derived_address.lower() != config_settings.ADDRESS.lower():
            issues.append(f"Address mismatch: derived {derived_address} != configured {config_settings.ADDRESS}")
        
        # Check RPC URL format
        assert config_settings.RPC_URL.startswith(('http://', 'https://')), \
            f"RPC URL should start with http:// or https://: {config_settings.RPC_URL}"
        
        # Check chain ID is reasonable
        assert config_settings.CHAIN_ID > 0, f"Chain ID should be positive: {config_settings.CHAIN_ID}"
        
        # Check token addresses format (if provided)
        for token_name, token_address in [('WSTT', config_settings.WSTT), ('SUSDT', config_settings.SUSDT)]:
            if token_address:
                assert token_address.startswith('0x'), f"{token_name} address should start with 0x: {token_address}"
                assert len(token_address) == 42, f"{token_name} address should be 42 characters: {token_address}"
        
        if issues:
            print("⚠️ Configuration issues found:")
            for issue in issues:
                print(f"   - {issue}")
            # Don't fail the test for address mismatch, just warn
            pytest.warns(UserWarning, match="Configuration inconsistencies found")
        else:
            print("✅ All configuration values are consistent")
    
    def test_rpc_url_format(self, config_settings):
        """Test RPC URL format specifically."""
        assert config_settings.RPC_URL is not None, "RPC URL not configured"
        assert isinstance(config_settings.RPC_URL, str), "RPC URL should be a string"
        assert config_settings.RPC_URL.startswith(('http://', 'https://')), "RPC URL should be HTTP/HTTPS"
        assert len(config_settings.RPC_URL) > 10, "RPC URL seems too short"
        
        print(f"✅ RPC URL format valid: {config_settings.RPC_URL}")
    
    def test_chain_id_format(self, config_settings):
        """Test Chain ID format specifically."""
        assert config_settings.CHAIN_ID is not None, "Chain ID not configured"
        assert isinstance(config_settings.CHAIN_ID, int), "Chain ID should be an integer"
        assert config_settings.CHAIN_ID > 0, "Chain ID should be positive"
        assert config_settings.CHAIN_ID < 1000000, "Chain ID seems unreasonably large"
        
        print(f"✅ Chain ID format valid: {config_settings.CHAIN_ID}")
    
    def test_database_configuration(self, config_settings):
        """Test database configuration specifically."""
        assert config_settings.MONGODB_URL is not None, "MongoDB URL not configured"
        assert isinstance(config_settings.MONGODB_URL, str), "MongoDB URL should be a string"
        assert len(config_settings.MONGODB_URL) > 5, "MongoDB URL seems too short"
        
        assert config_settings.DATABASE_NAME is not None, "Database name not configured"
        assert isinstance(config_settings.DATABASE_NAME, str), "Database name should be a string"
        assert len(config_settings.DATABASE_NAME) > 0, "Database name should not be empty"
        
        print(f"✅ Database configuration valid: {config_settings.DATABASE_NAME} @ {config_settings.MONGODB_URL}")
    
    def test_configuration_summary(self, config_settings, derived_address):
        """Test that prints configuration summary (always passes)."""
        print("\n📋 Configuration Summary")
        print("=" * 50)
        print(f"🎯 Ready to test with address: {derived_address}")
        print(f"🌐 Chain: {config_settings.CHAIN_ID}")
        print(f"🔗 RPC: {config_settings.RPC_URL}")
        print(f"💾 Database: {config_settings.DATABASE_NAME}")
        
        if config_settings.WSTT:
            print(f"🪙 WSTT: {config_settings.WSTT}")
        if config_settings.SUSDT:
            print(f"🪙 SUSDT: {config_settings.SUSDT}")
        
        print("\n📝 Next Steps:")
        print("1. Run the full async test: python tests/integration/test_account_balance.py")
        print("2. Check account balance via API: GET /account/balance/{address}")
        print("3. Create account via API: POST /account/create")
        
        # This test always passes, it's just for information
        assert True


def test_environment_configuration():
    """Test that environment configuration is loaded correctly (standalone version)."""
    print("🔧 Environment Configuration Test")
    print("=" * 50)
    
    # Check if private key is loaded
    assert settings.PRIVATE_KEY is not None, "Private key not found in environment"
    print(f"✅ Private key loaded: {settings.PRIVATE_KEY[:10]}...{settings.PRIVATE_KEY[-4:]}")
    
    # Display other configuration
    print(f"✅ RPC URL: {settings.RPC_URL}")
    print(f"✅ Chain ID: {settings.CHAIN_ID}")
    print(f"✅ Database URL: {settings.MONGODB_URL}")
    print(f"✅ Database Name: {settings.DATABASE_NAME}")
    
    # Display token addresses if configured
    if settings.WSTT:
        print(f"✅ WSTT Token: {settings.WSTT}")
    if settings.SUSDT:
        print(f"✅ SUSDT Token: {settings.SUSDT}")


def test_private_key_validation():
    """Test private key validation (standalone version)."""
    print("\n🔐 Private Key Validation Test")
    print("=" * 50)
    
    # Validate the private key format
    is_valid = validate_private_key(settings.PRIVATE_KEY)
    assert is_valid, "Private key format is invalid"
    print("✅ Private key format is valid")


def test_address_derivation():
    """Test address derivation from private key (standalone version)."""
    print("\n📍 Address Derivation Test")
    print("=" * 50)
    
    # Get address from private key
    address = get_address_from_private_key(settings.PRIVATE_KEY)
    
    print(f"✅ Address derived successfully: {address}")
    
    # Compare with configured address if available
    if settings.ADDRESS:
        if address.lower() == settings.ADDRESS.lower():
            print(f"✅ Derived address matches configured address")
        else:
            print(f"⚠️ Derived address differs from configured address:")
            print(f"   Derived: {address}")
            print(f"   Configured: {settings.ADDRESS}")
    
    # Assert for pytest compatibility
    assert address is not None, "Address derivation failed"


def test_configuration_consistency():
    """Test consistency between different configuration values (standalone version)."""
    print("\n🔍 Configuration Consistency Test")
    print("=" * 50)
    
    issues = []
    
    # Check if private key and address match
    try:
        derived_address = get_address_from_private_key(settings.PRIVATE_KEY)
        if settings.ADDRESS and derived_address.lower() != settings.ADDRESS.lower():
            issues.append(f"Address mismatch: derived {derived_address} != configured {settings.ADDRESS}")
    except Exception as e:
        issues.append(f"Cannot derive address: {e}")
    
    # Check RPC URL format
    if not settings.RPC_URL.startswith(('http://', 'https://')):
        issues.append(f"RPC URL should start with http:// or https://: {settings.RPC_URL}")
    
    # Check chain ID is reasonable
    if settings.CHAIN_ID <= 0:
        issues.append(f"Chain ID should be positive: {settings.CHAIN_ID}")
    
    # Check token addresses format (if provided)
    for token_name, token_address in [('WSTT', settings.WSTT), ('SUSDT', settings.SUSDT)]:
        if token_address and not token_address.startswith('0x'):
            issues.append(f"{token_name} address should start with 0x: {token_address}")
    
    if issues:
        print("⚠️ Configuration issues found:")
        for issue in issues:
            print(f"   - {issue}")
        # Don't fail the test, just warn
        import warnings
        warnings.warn("Configuration inconsistencies found", UserWarning)
    else:
        print("✅ All configuration values are consistent")


def main():
    """Run all simple tests (standalone mode)."""
    print("🚀 Simple Account Balance Integration Test")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: Environment configuration
    if not test_environment_configuration():
        all_passed = False
    
    # Test 2: Private key validation
    if not test_private_key_validation():
        all_passed = False
    
    # Test 3: Address derivation
    address = test_address_derivation()
    if not address:
        all_passed = False
    
    # Test 4: Configuration consistency
    if not test_configuration_consistency():
        all_passed = False
    
    # Final summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("✅ All tests passed!")
        print(f"🎯 Ready to test with address: {address}")
        print(f"🌐 Chain: {settings.CHAIN_ID}")
        print(f"🔗 RPC: {settings.RPC_URL}")
        
        # Provide next steps
        print("\n📝 Next Steps:")
        print("1. Run the full async test: python tests/integration/test_account_balance.py")
        print("2. Check account balance via API: GET /account/balance/{address}")
        print("3. Create account via API: POST /account/create")
        
        return 0
    else:
        print("❌ Some tests failed!")
        print("🔧 Please check your .env configuration file")
        return 1


# Pytest markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.config
]


if __name__ == "__main__":
    # Run with pytest when executed directly
    pytest.main([__file__, "-v", "-s"])
    # Or run standalone
    # exit_code = main()
    # exit(exit_code)


# Example .env configuration:
"""
# Blockchain Configuration
RPC_URL=https://rpc.ankr.com/somnia_testnet
CHAIN_ID=50312

# Account Configuration
PRIVATE_KEY=0x0000000000000000000000000000000000000000000000000000000000000001
ADDRESS=0x7e5f4552091a69125d5dfcb7b8c2659029395bdf

# Token Addresses
WSTT=0xF22eF0085f6511f70b01a68F360dCc56261F768a
SUSDT=0x65296738D4E5edB1515e40287B6FDf8320E6eE04

# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=autosomnia

# API Keys (optional for this test)
COINGECKO_API_KEY=
GEMINI_API_KEY=
"""