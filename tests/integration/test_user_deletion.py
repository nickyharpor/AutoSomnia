"""
Integration test for user deletion with cascading account removal.

This file demonstrates how to use the new DELETE /account/remove-user/{user_id} endpoint
that removes a user along with all their associated accounts.
"""

import pytest
import requests
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def base_url():
    """Base URL for API requests."""
    return "http://localhost:8000"


@pytest.fixture
def headers():
    """HTTP headers for API requests."""
    return {"Content-Type": "application/json"}


@pytest.fixture
def test_user_id():
    """Generate a unique test user ID."""
    return int(time.time())  # Use timestamp to ensure uniqueness


class TestUserDeletionIntegration:
    """Pytest-compatible integration tests for user deletion functionality."""
    
    def create_test_user(self, base_url: str, headers: dict, user_id: int, auto_exchange: bool = False) -> Dict[str, Any]:
        """Create a test user."""
        url = f"{base_url}/users/create"
        data = {
            "user_id": user_id,
            "auto_exchange": auto_exchange
        }
        
        response = requests.post(url, json=data, headers=headers)
        return response
    
    def create_test_account(self, base_url: str, headers: dict, user_id: int) -> Dict[str, Any]:
        """Create a test account for the user."""
        url = f"{base_url}/account/create"
        data = {
            "user_id": user_id,
            "chain_id": 1
        }
        
        response = requests.post(url, json=data, headers=headers)
        return response
    
    def list_user_accounts(self, base_url: str, headers: dict, user_id: int) -> Dict[str, Any]:
        """List all accounts for a user."""
        url = f"{base_url}/account/list_user_accounts/{user_id}"
        response = requests.get(url, headers=headers)
        return response
    
    def delete_user_with_accounts(self, base_url: str, headers: dict, user_id: int) -> Dict[str, Any]:
        """Delete user and all their accounts using the new cascading delete endpoint."""
        url = f"{base_url}/account/remove-user/{user_id}"
        response = requests.delete(url, headers=headers)
        return response
    
    def check_user_exists(self, base_url: str, headers: dict, user_id: int) -> bool:
        """Check if user still exists after deletion."""
        url = f"{base_url}/users/{user_id}"
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    
    def test_api_server_available(self, base_url, headers):
        """Test that the API server is available."""
        try:
            response = requests.get(f"{base_url}/health", headers=headers, timeout=5)
            if response.status_code != 200:
                pytest.skip("API server not available - start with: python app/main.py")
        except requests.exceptions.RequestException:
            pytest.skip("API server not available - start with: python app/main.py")
    
    def test_create_user(self, base_url, headers, test_user_id):
        """Test user creation."""
        self.test_api_server_available(base_url, headers)
        
        response = self.create_test_user(base_url, headers, test_user_id, auto_exchange=True)
        
        assert response.status_code in [200, 201], f"Failed to create user: {response.text}"
        
        user_data = response.json()
        assert user_data["user_id"] == test_user_id
        assert user_data["auto_exchange"] is True
        
        print(f"✅ User created: {test_user_id}")
    
    def test_create_account_for_user(self, base_url, headers, test_user_id):
        """Test account creation for a user."""
        self.test_api_server_available(base_url, headers)
        
        # First create the user
        user_response = self.create_test_user(base_url, headers, test_user_id)
        if user_response.status_code not in [200, 201, 409]:  # 409 = already exists
            pytest.fail(f"Failed to create user: {user_response.text}")
        
        # Then create an account
        response = self.create_test_account(base_url, headers, test_user_id)
        
        assert response.status_code in [200, 201], f"Failed to create account: {response.text}"
        
        account_data = response.json()
        assert "account" in account_data
        assert account_data["account"]["address"].startswith("0x")
        
        print(f"✅ Account created for user {test_user_id}")
    
    def test_list_user_accounts(self, base_url, headers, test_user_id):
        """Test listing user accounts."""
        self.test_api_server_available(base_url, headers)
        
        # Create user and account first
        self.create_test_user(base_url, headers, test_user_id)
        self.create_test_account(base_url, headers, test_user_id)
        
        response = self.list_user_accounts(base_url, headers, test_user_id)
        
        assert response.status_code == 200, f"Failed to list accounts: {response.text}"
        
        accounts_data = response.json()
        assert "accounts" in accounts_data
        assert "total_count" in accounts_data
        
        print(f"✅ Listed accounts for user {test_user_id}: {accounts_data['total_count']} accounts")
    
    def test_delete_user_with_accounts(self, base_url, headers, test_user_id):
        """Test cascading user deletion."""
        self.test_api_server_available(base_url, headers)
        
        # Setup: Create user and accounts
        self.create_test_user(base_url, headers, test_user_id)
        
        # Create multiple accounts
        accounts_created = []
        for i in range(2):  # Create 2 test accounts
            account_response = self.create_test_account(base_url, headers, test_user_id)
            if account_response.status_code in [200, 201]:
                account_data = account_response.json()
                accounts_created.append(account_data["account"]["address"])
        
        # Verify accounts exist
        accounts_before = self.list_user_accounts(base_url, headers, test_user_id)
        assert accounts_before.status_code == 200
        
        # Delete user with cascading account deletion
        delete_response = self.delete_user_with_accounts(base_url, headers, test_user_id)
        
        assert delete_response.status_code == 200, f"Failed to delete user: {delete_response.text}"
        
        deletion_result = delete_response.json()
        assert "message" in deletion_result
        assert "accounts_deleted" in deletion_result
        assert deletion_result["user_id"] == test_user_id
        
        print(f"✅ User {test_user_id} deleted with {deletion_result['accounts_deleted']} accounts")
    
    def test_verify_deletion(self, base_url, headers, test_user_id):
        """Test that user and accounts are actually deleted."""
        self.test_api_server_available(base_url, headers)
        
        # Setup: Create user and account, then delete
        self.create_test_user(base_url, headers, test_user_id)
        self.create_test_account(base_url, headers, test_user_id)
        self.delete_user_with_accounts(base_url, headers, test_user_id)
        
        # Verify user no longer exists
        user_exists = self.check_user_exists(base_url, headers, test_user_id)
        assert not user_exists, "User should not exist after deletion"
        
        # Verify accounts are gone
        accounts_after = self.list_user_accounts(base_url, headers, test_user_id)
        assert accounts_after.status_code == 200
        accounts_data = accounts_after.json()
        assert accounts_data["total_count"] == 0, "No accounts should remain after user deletion"
        
        print(f"✅ Verified user {test_user_id} and accounts are deleted")
    
    def test_complete_user_deletion_workflow(self, base_url, headers, test_user_id):
        """Test the complete user deletion workflow."""
        self.test_api_server_available(base_url, headers)
        
        print(f"\n🚀 Starting Complete User Deletion Workflow for user {test_user_id}")
        
        try:
            # Step 1: Create user
            print("📝 Step 1: Creating test user")
            user_response = self.create_test_user(base_url, headers, test_user_id, auto_exchange=True)
            assert user_response.status_code in [200, 201], f"Failed to create user: {user_response.text}"
            print(f"✅ User {test_user_id} created")
            
            # Step 2: Create multiple accounts
            print("💼 Step 2: Creating accounts for user")
            accounts_created = []
            for i in range(3):
                account_response = self.create_test_account(base_url, headers, test_user_id)
                assert account_response.status_code in [200, 201], f"Failed to create account {i+1}: {account_response.text}"
                account_data = account_response.json()
                accounts_created.append(account_data["account"]["address"])
                print(f"✅ Account {i+1} created: {account_data['account']['address']}")
            
            # Step 3: Verify accounts exist
            print("📋 Step 3: Verifying accounts exist")
            accounts_response = self.list_user_accounts(base_url, headers, test_user_id)
            assert accounts_response.status_code == 200
            accounts_data = accounts_response.json()
            assert accounts_data["total_count"] >= len(accounts_created)
            print(f"✅ Found {accounts_data['total_count']} accounts")
            
            # Step 4: Delete user with cascading deletion
            print("🗑️ Step 4: Deleting user with cascading account deletion")
            delete_response = self.delete_user_with_accounts(base_url, headers, test_user_id)
            assert delete_response.status_code == 200, f"Failed to delete user: {delete_response.text}"
            deletion_result = delete_response.json()
            print(f"✅ Deletion completed: {deletion_result['accounts_deleted']} accounts deleted")
            
            # Step 5: Verify deletion
            print("🔍 Step 5: Verifying complete deletion")
            user_exists = self.check_user_exists(base_url, headers, test_user_id)
            assert not user_exists, "User should not exist after deletion"
            
            accounts_after = self.list_user_accounts(base_url, headers, test_user_id)
            assert accounts_after.status_code == 200
            accounts_data_after = accounts_after.json()
            assert accounts_data_after["total_count"] == 0, "No accounts should remain"
            
            print("✅ Verification complete: User and all accounts deleted")
            print("🎉 Complete workflow test passed!")
            
        except Exception as e:
            pytest.fail(f"Complete workflow test failed: {str(e)}")


# Original standalone class for backward compatibility
class UserDeletionExample:
    """Example class demonstrating user deletion with cascading account removal (standalone mode)."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
    
    def create_test_user(self, user_id: int, auto_exchange: bool = False) -> Dict[str, Any]:
        """Create a test user."""
        url = f"{self.base_url}/users/create"
        data = {
            "user_id": user_id,
            "auto_exchange": auto_exchange
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
    
    def create_test_account(self, user_id: int) -> Dict[str, Any]:
        """Create a test account for the user."""
        url = f"{self.base_url}/account/create"
        data = {
            "user_id": user_id,
            "chain_id": 1
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
    
    def list_user_accounts(self, user_id: int) -> Dict[str, Any]:
        """List all accounts for a user."""
        url = f"{self.base_url}/account/list_user_accounts/{user_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def delete_user_with_accounts(self, user_id: int) -> Dict[str, Any]:
        """Delete user and all their accounts using the new cascading delete endpoint."""
        url = f"{self.base_url}/account/remove-user/{user_id}"
        response = requests.delete(url, headers=self.headers)
        return response.json()
    
    def check_user_exists(self, user_id: int) -> bool:
        """Check if user still exists after deletion."""
        url = f"{self.base_url}/users/{user_id}"
        response = requests.get(url, headers=self.headers)
        return response.status_code == 200
    
    def run_example(self):
        """Run the complete example workflow."""
        print("🚀 Starting User Deletion Example")
        print("=" * 50)
        
        test_user_id = 12345
        
        try:
            # Step 1: Create a test user
            print(f"📝 Step 1: Creating test user {test_user_id}")
            user_result = self.create_test_user(test_user_id, auto_exchange=True)
            print(f"✅ User created: {json.dumps(user_result, indent=2)}")
            
            # Step 2: Create multiple accounts for the user
            print(f"\n💼 Step 2: Creating accounts for user {test_user_id}")
            accounts_created = []
            
            for i in range(3):  # Create 3 test accounts
                account_result = self.create_test_account(test_user_id)
                accounts_created.append(account_result['account']['address'])
                print(f"✅ Account {i+1} created: {account_result['account']['address']}")
            
            # Step 3: List user accounts before deletion
            print(f"\n📋 Step 3: Listing accounts for user {test_user_id}")
            user_accounts = self.list_user_accounts(test_user_id)
            print(f"📊 Found {user_accounts['total_count']} accounts")
            
            # Step 4: Delete user with all accounts using cascading delete
            print(f"\n🗑️ Step 4: Deleting user {test_user_id} with all accounts")
            deletion_result = self.delete_user_with_accounts(test_user_id)
            print(f"✅ Deletion result: {json.dumps(deletion_result, indent=2)}")
            
            # Step 5: Verify user and accounts are deleted
            print(f"\n🔍 Step 5: Verifying deletion")
            user_exists = self.check_user_exists(test_user_id)
            print(f"👤 User exists after deletion: {user_exists}")
            
            # Check accounts after deletion
            user_accounts_after = self.list_user_accounts(test_user_id)
            print(f"📊 Accounts remaining: {user_accounts_after['total_count']}")

            if user_accounts_after['total_count'] == 0 and not user_exists:
                print("\n🎉 Example completed successfully!")
            else:
                print("\n❌ Example didn't work as expected.")
            
        except Exception as e:
            print(f"❌ Error during example: {str(e)}")


def main():
    """Run the user deletion example."""
    example = UserDeletionExample()
    example.run_example()


# Pytest markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.api
]


if __name__ == "__main__":
    # Run with pytest when executed directly
    pytest.main([__file__, "-v", "-s"])
    # Or run standalone
    # main()


# Example usage with curl commands:
"""
# 1. Create a user
curl -X POST "http://localhost:8000/users/create" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 12345, "auto_exchange": true}'

# 2. Create accounts for the user
curl -X POST "http://localhost:8000/account/create" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 12345, "chain_id": 1}'

# 3. List user accounts
curl -X GET "http://localhost:8000/account/list_user_accounts/12345"

# 4. Delete user with all accounts (NEW ENDPOINT)
curl -X DELETE "http://localhost:8000/account/remove-user/12345"

# 5. Verify deletion
curl -X GET "http://localhost:8000/users/12345"
curl -X GET "http://localhost:8000/account/list_user_accounts/12345"
"""