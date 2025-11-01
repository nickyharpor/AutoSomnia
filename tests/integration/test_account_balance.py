"""
Integration test for account balance retrieval using environment configuration.

This test demonstrates how to:
1. Read private key from environment using backend_config
2. Get address from private key using account_service
3. Retrieve account balance from the blockchain
"""

import asyncio
import logging
import sys
from pathlib import Path
from web3 import AsyncWeb3

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.backend_config import settings
from app.services.account_service import AccountService, get_address_from_private_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccountBalanceTest:
    """Integration test for account balance operations."""
    
    def __init__(self):
        """Initialize the test with configuration from environment."""
        self.private_key = settings.PRIVATE_KEY
        self.rpc_url = settings.RPC_URL
        self.chain_id = settings.CHAIN_ID
        
        logger.info(f"Initialized test with:")
        logger.info(f"  RPC URL: {self.rpc_url}")
        logger.info(f"  Chain ID: {self.chain_id}")
        logger.info(f"  Private key loaded: {'Yes' if self.private_key else 'No'}")
    
    async def setup_web3_service(self) -> AccountService:
        """Setup Web3 connection and AccountService."""
        try:
            # Create async Web3 instance
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(self.rpc_url))
            
            # Test connection
            is_connected = await w3.is_connected()
            if not is_connected:
                raise ConnectionError(f"Failed to connect to {self.rpc_url}")
            
            logger.info("✅ Successfully connected to blockchain")
            
            # Create account service
            service = AccountService(w3, self.chain_id)
            return service
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Web3 service: {e}")
            raise
    
    def get_address_from_private_key_test(self) -> str:
        """Test getting address from private key using the utility function."""
        try:
            if not self.private_key:
                raise ValueError("Private key not found in environment configuration")
            
            # Use the utility function from account_service
            address = get_address_from_private_key(self.private_key)
            
            logger.info(f"✅ Address derived from private key: {address}")
            return address
            
        except Exception as e:
            logger.error(f"❌ Failed to derive address from private key: {e}")
            raise
    
    async def get_account_balance_test(self, service: AccountService, address: str) -> dict:
        """Test getting account balance."""
        try:
            # Get SOMI balance
            eth_balance = await service.get_eth_balance(address)
            
            # Get transaction count (nonce)
            nonce = await service.get_transaction_count(address)
            
            # Check if address is a contract
            is_contract = await service.is_contract_address(address)
            
            # Get latest block for context
            latest_block = await service.w3.eth.get_block('latest')
            
            result = {
                "address": address,
                "eth_balance": str(eth_balance),
                "nonce": nonce,
                "is_contract": is_contract,
                "latest_block": latest_block['number'],
                "chain_id": self.chain_id
            }
            
            logger.info(f"✅ Account balance retrieved successfully:")
            logger.info(f"  Address: {address}")
            logger.info(f"  SOMI Balance: {eth_balance}")
            logger.info(f"  Nonce: {nonce}")
            logger.info(f"  Is Contract: {is_contract}")
            logger.info(f"  Latest Block: {latest_block['number']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to get account balance: {e}")
            raise
    
    async def test_token_balance(self, service: AccountService, address: str) -> dict:
        """Test getting token balances for configured tokens."""
        try:
            token_balances = {}
            
            # Test WSTT token balance
            if settings.WSTT:
                try:
                    wstt_balance = await service.get_token_balance(address, settings.WSTT)
                    token_balances['WSTT'] = {
                        "address": wstt_balance.token_address,
                        "symbol": wstt_balance.token_symbol,
                        "name": wstt_balance.token_name,
                        "balance": str(wstt_balance.balance),
                        "decimals": wstt_balance.decimals
                    }
                    logger.info(f"✅ WSTT Balance: {wstt_balance.balance} {wstt_balance.token_symbol}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to get WSTT balance: {e}")
            
            # Test SUSDT token balance
            if settings.SUSDT:
                try:
                    susdt_balance = await service.get_token_balance(address, settings.SUSDT)
                    token_balances['SUSDT'] = {
                        "address": susdt_balance.token_address,
                        "symbol": susdt_balance.token_symbol,
                        "name": susdt_balance.token_name,
                        "balance": str(susdt_balance.balance),
                        "decimals": susdt_balance.decimals
                    }
                    logger.info(f"✅ SUSDT Balance: {susdt_balance.balance} {susdt_balance.token_symbol}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to get SUSDT balance: {e}")
            
            return token_balances
            
        except Exception as e:
            logger.error(f"❌ Failed to get token balances: {e}")
            raise
    
    async def run_complete_test(self):
        """Run the complete integration test."""
        logger.info("🚀 Starting Account Balance Integration Test")
        logger.info("=" * 60)
        
        try:
            # Step 1: Get address from private key
            logger.info("📝 Step 1: Deriving address from private key")
            address = self.get_address_from_private_key_test()
            
            # Step 2: Setup Web3 service
            logger.info("\n🔗 Step 2: Setting up Web3 connection")
            service = await self.setup_web3_service()
            
            # Step 3: Get account balance
            logger.info("\n💰 Step 3: Getting account balance")
            balance_result = await self.get_account_balance_test(service, address)
            
            # Step 4: Get token balances
            logger.info("\n🪙 Step 4: Getting token balances")
            token_balances = await self.test_token_balance(service, address)
            
            # Step 5: Create complete portfolio summary
            logger.info("\n📊 Step 5: Creating portfolio summary")
            portfolio_summary = {
                "account_info": balance_result,
                "token_balances": token_balances,
                "test_timestamp": asyncio.get_event_loop().time(),
                "configuration": {
                    "rpc_url": self.rpc_url,
                    "chain_id": self.chain_id,
                    "wstt_address": settings.WSTT,
                    "susdt_address": settings.SUSDT
                }
            }
            
            logger.info("✅ Portfolio Summary:")
            logger.info(f"  SOMI Balance: {balance_result['eth_balance']}")
            logger.info(f"  Token Count: {len(token_balances)}")
            logger.info(f"  Chain ID: {balance_result['chain_id']}")
            
            logger.info("\n🎉 Integration test completed successfully!")
            return portfolio_summary
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            raise
        finally:
            # Cleanup if needed
            logger.info("\n🧹 Test cleanup completed")


async def main():
    """Main function to run the integration test."""
    test = AccountBalanceTest()
    
    try:
        result = await test.run_complete_test()
        
        # Print final summary
        print("\n" + "=" * 60)
        print("📋 FINAL TEST RESULTS")
        print("=" * 60)
        print(f"Address: {result['account_info']['address']}")
        print(f"SOMI Balance: {result['account_info']['eth_balance']}")
        print(f"Nonce: {result['account_info']['nonce']}")
        print(f"Latest Block: {result['account_info']['latest_block']}")
        
        if result['token_balances']:
            print("\nToken Balances:")
            for token_name, token_info in result['token_balances'].items():
                print(f"  {token_name}: {token_info['balance']} {token_info['symbol']}")
        else:
            print("\nNo token balances found or tokens not configured")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    # Run the async test
    exit_code = asyncio.run(main())
    exit(exit_code)


# Example usage with different configurations:
"""
# 1. Run with default environment configuration
python tests/integration/test_account_balance.py

# 2. Run with custom environment file
PRIVATE_KEY=0x... RPC_URL=https://... python tests/integration/test_account_balance.py

# 3. Expected output:
# 🚀 Starting Account Balance Integration Test
# ============================================================
# 📝 Step 1: Deriving address from private key
# ✅ Address derived from private key: 0x7e5f4552091a69125d5dfcb7b8c2659029395bdf
# 
# 🔗 Step 2: Setting up Web3 connection
# ✅ Successfully connected to blockchain
# 
# 💰 Step 3: Getting account balance
# ✅ Account balance retrieved successfully:
#   Address: 0x7e5f4552091a69125d5dfcb7b8c2659029395bdf
#   SOMI Balance: 1.234567890123456789
#   Nonce: 42
#   Is Contract: False
#   Latest Block: 123456
# 
# 🪙 Step 4: Getting token balances
# ✅ WSTT Balance: 100.0 WSTT
# ✅ SUSDT Balance: 50.123456 SUSDT
# 
# 📊 Step 5: Creating portfolio summary
# ✅ Portfolio Summary:
#   SOMI Balance: 1.234567890123456789
#   Token Count: 2
#   Chain ID: 50312
# 
# 🎉 Integration test completed successfully!
"""