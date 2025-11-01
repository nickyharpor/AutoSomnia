"""
Integration test example for user deletion with cascading account removal.

This file demonstrates how to use the new DELETE /account/remove-user/{user_id} endpoint
that removes a user along with all their associated accounts.
"""

import requests
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class UserDeletionExample:
    """Example class demonstrating user deletion with cascading account removal."""
    
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

            if user_accounts_after == 0 and not user_exists:
                print("\n🎉 Example completed successfully!")
            else:
                print("\n❌ Example didn't work as expected.")
            
        except Exception as e:
            print(f"❌ Error during example: {str(e)}")


def main():
    """Run the user deletion example."""
    example = UserDeletionExample()
    example.run_example()


if __name__ == "__main__":
    main()


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