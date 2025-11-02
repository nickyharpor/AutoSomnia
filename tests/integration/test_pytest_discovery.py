"""
Test to verify that pytest can discover all integration tests.

This test validates that the pytest conversion was successful.
"""

import pytest
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestPytestDiscovery:
    """Test that pytest can discover all integration tests."""
    
    def test_config_validation_discoverable(self):
        """Test that config validation tests are discoverable."""
        # This test just verifies the structure exists
        from tests.integration.test_config_validation import TestConfigValidation
        
        # Check that the class has test methods
        test_methods = [method for method in dir(TestConfigValidation) if method.startswith('test_')]
        
        assert len(test_methods) >= 5, f"Expected at least 5 test methods, found {len(test_methods)}"
        
        print(f"✅ Config validation has {len(test_methods)} discoverable test methods")
    
    def test_simple_balance_discoverable(self):
        """Test that simple balance tests are discoverable."""
        from tests.integration.test_simple_balance import TestSimpleBalance
        
        # Check that the class has test methods
        test_methods = [method for method in dir(TestSimpleBalance) if method.startswith('test_')]
        
        assert len(test_methods) >= 5, f"Expected at least 5 test methods, found {len(test_methods)}"
        
        print(f"✅ Simple balance has {len(test_methods)} discoverable test methods")
    
    def test_user_deletion_discoverable(self):
        """Test that user deletion tests are discoverable."""
        from tests.integration.test_user_deletion import TestUserDeletionIntegration
        
        # Check that the class has test methods
        test_methods = [method for method in dir(TestUserDeletionIntegration) if method.startswith('test_')]
        
        assert len(test_methods) >= 5, f"Expected at least 5 test methods, found {len(test_methods)}"
        
        print(f"✅ User deletion has {len(test_methods)} discoverable test methods")
    
    def test_exchange_pytest_discoverable(self):
        """Test that exchange pytest tests are discoverable."""
        from tests.integration.test_exchange_pytest import TestExchangeIntegration
        
        # Check that the class has test methods
        test_methods = [method for method in dir(TestExchangeIntegration) if method.startswith('test_')]
        
        assert len(test_methods) >= 5, f"Expected at least 5 test methods, found {len(test_methods)}"
        
        print(f"✅ Exchange integration has {len(test_methods)} discoverable test methods")
    
    def test_simple_api_discoverable(self):
        """Test that simple API tests are discoverable."""
        from tests.integration.test_simple_api import TestSimpleAPI
        
        # Check that the class has test methods
        test_methods = [method for method in dir(TestSimpleAPI) if method.startswith('test_')]
        
        assert len(test_methods) >= 3, f"Expected at least 3 test methods, found {len(test_methods)}"
        
        print(f"✅ Simple API has {len(test_methods)} discoverable test methods")
    
    def test_account_balance_discoverable(self):
        """Test that account balance tests are discoverable."""
        from tests.integration.test_account_balance import TestAccountBalance
        
        # Check that the class has test methods
        test_methods = [method for method in dir(TestAccountBalance) if method.startswith('test_')]
        
        assert len(test_methods) >= 5, f"Expected at least 5 test methods, found {len(test_methods)}"
        
        print(f"✅ Account balance has {len(test_methods)} discoverable test methods")
    
    def test_all_integration_files_exist(self):
        """Test that all expected integration test files exist."""
        integration_dir = Path(__file__).parent
        
        expected_files = [
            "test_config_validation.py",
            "test_simple_balance.py", 
            "test_account_balance.py",
            "test_user_deletion.py",
            "test_exchange_pytest.py",
            "test_simple_api.py"
        ]
        
        for filename in expected_files:
            file_path = integration_dir / filename
            assert file_path.exists(), f"Expected test file not found: {filename}"
        
        print(f"✅ All {len(expected_files)} expected test files exist")
    
    def test_pytest_markers_configured(self):
        """Test that pytest markers are properly configured."""
        # Import test modules to check for markers
        test_modules = [
            "tests.integration.test_config_validation",
            "tests.integration.test_simple_balance",
            "tests.integration.test_account_balance",
            "tests.integration.test_user_deletion",
            "tests.integration.test_exchange_pytest",
            "tests.integration.test_simple_api"
        ]
        
        markers_found = 0
        
        for module_name in test_modules:
            try:
                module = __import__(module_name, fromlist=[''])
                if hasattr(module, 'pytestmark'):
                    markers_found += 1
            except ImportError:
                pass  # Skip if module can't be imported
        
        assert markers_found >= 3, f"Expected at least 3 modules with pytest markers, found {markers_found}"
        
        print(f"✅ Found pytest markers in {markers_found} test modules")
    
    def test_configuration_import_works(self):
        """Test that configuration can be imported successfully."""
        try:
            from app.core.backend_config import settings
            
            # Basic checks that settings loaded
            assert hasattr(settings, 'RPC_URL'), "Settings should have RPC_URL"
            assert hasattr(settings, 'CHAIN_ID'), "Settings should have CHAIN_ID"
            assert hasattr(settings, 'PRIVATE_KEY'), "Settings should have PRIVATE_KEY"
            
            print("✅ Configuration imports and loads successfully")
            
        except ImportError as e:
            pytest.fail(f"Cannot import configuration: {e}")
    
    def test_account_service_import_works(self):
        """Test that account service functions can be imported."""
        try:
            from app.services.account_service import get_address_from_private_key, validate_private_key
            
            # Check that functions are callable
            assert callable(get_address_from_private_key), "get_address_from_private_key should be callable"
            assert callable(validate_private_key), "validate_private_key should be callable"
            
            print("✅ Account service functions import successfully")
            
        except ImportError as e:
            pytest.fail(f"Cannot import account service functions: {e}")


# Pytest markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.discovery
]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])