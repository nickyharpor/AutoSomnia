"""
Simple integration test for account balance retrieval.

This is a simplified version that focuses on the core functionality:
1. Read private key from environment
2. Get address from private key
3. Display the configuration and derived address
"""

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


def test_environment_configuration():
    """Test that environment configuration is loaded correctly."""
    print("🔧 Environment Configuration Test")
    print("=" * 50)
    
    # Check if private key is loaded
    if settings.PRIVATE_KEY:
        print(f"✅ Private key loaded: {settings.PRIVATE_KEY[:10]}...{settings.PRIVATE_KEY[-4:]}")
    else:
        print("❌ Private key not found in environment")
        return False
    
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
    
    return True


def test_private_key_validation():
    """Test private key validation."""
    print("\n🔐 Private Key Validation Test")
    print("=" * 50)
    
    try:
        # Validate the private key format
        is_valid = validate_private_key(settings.PRIVATE_KEY)
        
        if is_valid:
            print("✅ Private key format is valid")
            return True
        else:
            print("❌ Private key format is invalid")
            return False
            
    except Exception as e:
        print(f"❌ Error validating private key: {e}")
        return False


def test_address_derivation():
    """Test address derivation from private key."""
    print("\n📍 Address Derivation Test")
    print("=" * 50)
    
    try:
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
        
        return address
        
    except Exception as e:
        print(f"❌ Error deriving address: {e}")
        return None


def test_configuration_consistency():
    """Test consistency between different configuration values."""
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
        return False
    else:
        print("✅ All configuration values are consistent")
        return True


def main():
    """Run all simple tests."""
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


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)


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