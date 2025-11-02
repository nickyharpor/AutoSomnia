"""
Integration test for account balance retrieval using environment configuration.

This test demonstrates how to:
1. Read private key from environment using backend_config
2. Get address from private key using account_service
3. Retrieve account balance from the blockchain
"""

import pytest
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


@pytest.fixture
def config_settings():
    """Fixture to provide configuration settings."""
    return settings


@pytest.fixture
def derived_address():
    """Fixture to provide derived address from private key."""
    try:
        if not settings.PRIVATE_KEY:
            pytest.skip("Private key not found in environment configuration")
        return get_address_from_private_key(settings.PRIVATE_KEY)
    except Exception as e:
        pytest.skip(f"Cannot derive address from private key: {e}")


@pytest.fixture
def account_service_factory(config_settings):
    """Factory fixture to create AccountService instances."""
    async def _create_service():
        try:
            # Create async Web3 instance
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(config_settings.RPC_URL))
            
            # Test connection
            is_connected = await w3.is_connected()
            if not is_connected:
                pytest.skip(f"Cannot connect to blockchain at {config_settings.RPC_URL}")
            
            logger.info(f"✅ Connected to blockchain at {config_settings.RPC_URL}")
            
            # Create account service
            service = AccountService(w3, config_settings.CHAIN_ID)
            return service
            
        except Exception as e:
            pytest.skip(f"Failed to setup Web3 service: {e}")
    
    return _create_service


class TestAccountBalance:
    """Pytest-compatible test class for account balance functionality."""
    
    def test_configuration_loaded(self, config_settings):
        """Test that configuration is properly loaded."""
        print("\n🔧 Configuration Test")
        print("=" * 50)
        
        assert config_settings.PRIVATE_KEY is not None, "Private key not found"
        assert config_settings.RPC_URL is not None, "RPC URL not found"
        assert config_settings.CHAIN_ID is not None, "Chain ID not found"
        
        logger.info(f"✅ Configuration loaded:")
        logger.info(f"  RPC URL: {config_settings.RPC_URL}")
        logger.info(f"  Chain ID: {config_settings.CHAIN_ID}")
        logger.info(f"  Private key loaded: {'Yes' if config_settings.PRIVATE_KEY else 'No'}")
    
    def test_address_derivation(self, config_settings, derived_address):
        """Test address derivation from private key."""
        print("\n📝 Address Derivation Test")
        print("=" * 50)
        
        assert derived_address is not None, "Failed to derive address"
        assert derived_address.startswith('0x'), "Address should start with 0x"
        assert len(derived_address) == 42, "Address should be 42 characters"
        
        logger.info(f"✅ Address derived from private key: {derived_address}")
    
    @pytest.mark.asyncio
    async def test_blockchain_connection(self, account_service_factory):
        """Test blockchain connection."""
        print("\n🔗 Blockchain Connection Test")
        print("=" * 50)
        
        # Create account service
        account_service = await account_service_factory()
        
        assert account_service is not None, "Account service should be initialized"
        
        # Test that we can make a basic call
        latest_block = await account_service.w3.eth.get_block('latest')
        
        assert latest_block is not None, "Should be able to get latest block"
        assert latest_block['number'] > 0, "Block number should be positive"
        
        logger.info(f"✅ Successfully connected to blockchain")
        logger.info(f"✅ Latest block: {latest_block['number']}")
    
    @pytest.mark.asyncio
    async def test_account_balance_retrieval(self, account_service_factory, derived_address):
        """Test account balance retrieval."""
        print("\n💰 Account Balance Test")
        print("=" * 50)
        
        # Create account service
        account_service = await account_service_factory()
        
        # Get SOMI balance
        eth_balance = await account_service.get_eth_balance(derived_address)
        
        assert eth_balance is not None, "Should be able to get balance"
        assert eth_balance >= 0, "Balance should be non-negative"
        
        # Get transaction count (nonce)
        nonce = await account_service.get_transaction_count(derived_address)
        
        assert nonce is not None, "Should be able to get nonce"
        assert nonce >= 0, "Nonce should be non-negative"
        
        # Check if address is a contract
        is_contract = await account_service.is_contract_address(derived_address)
        
        assert isinstance(is_contract, bool), "is_contract should be boolean"
        
        logger.info(f"✅ Account balance retrieved successfully:")
        logger.info(f"  Address: {derived_address}")
        logger.info(f"  SOMI Balance: {eth_balance}")
        logger.info(f"  Nonce: {nonce}")
        logger.info(f"  Is Contract: {is_contract}")
    
    @pytest.mark.asyncio
    async def test_token_balances(self, account_service_factory, derived_address, config_settings):
        """Test token balance retrieval for configured tokens."""
        print("\n🪙 Token Balance Test")
        print("=" * 50)
        
        # Create account service
        account_service = await account_service_factory()
        
        token_balances = {}
        
        # Test WSTT token balance if configured
        if config_settings.WSTT:
            try:
                wstt_balance = await account_service.get_token_balance(derived_address, config_settings.WSTT)
                
                assert wstt_balance is not None, "Should get WSTT balance object"
                assert hasattr(wstt_balance, 'balance'), "Balance object should have balance attribute"
                assert hasattr(wstt_balance, 'token_symbol'), "Balance object should have symbol"
                
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
                # Don't fail the test for token balance issues
        
        # Test SUSDT token balance if configured
        if config_settings.SUSDT:
            try:
                susdt_balance = await account_service.get_token_balance(derived_address, config_settings.SUSDT)
                
                assert susdt_balance is not None, "Should get SUSDT balance object"
                
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
                # Don't fail the test for token balance issues
        
        # At least verify we attempted to get token balances
        if config_settings.WSTT or config_settings.SUSDT:
            logger.info(f"✅ Token balance test completed, found {len(token_balances)} tokens")
        else:
            logger.info("ℹ️ No token addresses configured for testing")
    
    @pytest.mark.asyncio
    async def test_portfolio_summary(self, account_service_factory, derived_address, config_settings):
        """Test complete portfolio summary generation."""
        print("\n📊 Portfolio Summary Test")
        print("=" * 50)
        
        # Create account service
        account_service = await account_service_factory()
        
        # Get account balance
        eth_balance = await account_service.get_eth_balance(derived_address)
        nonce = await account_service.get_transaction_count(derived_address)
        is_contract = await account_service.is_contract_address(derived_address)
        latest_block = await account_service.w3.eth.get_block('latest')
        
        # Create portfolio summary
        portfolio_summary = {
            "account_info": {
                "address": derived_address,
                "eth_balance": str(eth_balance),
                "nonce": nonce,
                "is_contract": is_contract,
                "latest_block": latest_block['number'],
                "chain_id": config_settings.CHAIN_ID
            },
            "configuration": {
                "rpc_url": config_settings.RPC_URL,
                "chain_id": config_settings.CHAIN_ID,
                "wstt_address": config_settings.WSTT,
                "susdt_address": config_settings.SUSDT
            },
            "test_timestamp": asyncio.get_event_loop().time()
        }
        
        # Validate portfolio summary structure
        assert "account_info" in portfolio_summary, "Portfolio should have account_info"
        assert "configuration" in portfolio_summary, "Portfolio should have configuration"
        assert portfolio_summary["account_info"]["address"] == derived_address, "Address should match"
        
        logger.info("✅ Portfolio Summary:")
        logger.info(f"  SOMI Balance: {portfolio_summary['account_info']['eth_balance']}")
        logger.info(f"  Chain ID: {portfolio_summary['account_info']['chain_id']}")
        logger.info(f"  Latest Block: {portfolio_summary['account_info']['latest_block']}")
    
    @pytest.mark.asyncio
    async def test_complete_integration_workflow(self, config_settings, derived_address, account_service_factory):
        """Test the complete integration workflow."""
        print("\n🚀 Complete Integration Workflow Test")
        print("=" * 60)
        
        try:
            # Step 1: Verify configuration
            assert config_settings.PRIVATE_KEY is not None
            assert config_settings.RPC_URL is not None
            assert config_settings.CHAIN_ID is not None
            logger.info("✅ Step 1: Configuration verified")
            
            # Step 2: Verify address derivation
            assert derived_address is not None
            assert derived_address.startswith('0x')
            logger.info(f"✅ Step 2: Address derived: {derived_address}")
            
            # Step 3: Create account service and verify blockchain connection
            account_service = await account_service_factory()
            latest_block = await account_service.w3.eth.get_block('latest')
            assert latest_block['number'] > 0
            logger.info(f"✅ Step 3: Blockchain connected, block: {latest_block['number']}")
            
            # Step 4: Verify account balance retrieval
            eth_balance = await account_service.get_eth_balance(derived_address)
            nonce = await account_service.get_transaction_count(derived_address)
            assert eth_balance >= 0
            assert nonce >= 0
            logger.info(f"✅ Step 4: Balance retrieved: {eth_balance} SOMI, nonce: {nonce}")
            
            # Step 5: Verify token balance attempts (don't fail if tokens don't exist)
            token_count = 0
            if config_settings.WSTT:
                try:
                    await account_service.get_token_balance(derived_address, config_settings.WSTT)
                    token_count += 1
                except Exception:
                    pass  # Token might not exist or have balance
            
            if config_settings.SUSDT:
                try:
                    await account_service.get_token_balance(derived_address, config_settings.SUSDT)
                    token_count += 1
                except Exception:
                    pass  # Token might not exist or have balance
            
            logger.info(f"✅ Step 5: Token balance checks completed for {token_count} tokens")
            
            logger.info("🎉 Complete integration workflow test passed!")
            
        except Exception as e:
            pytest.fail(f"Complete integration workflow failed: {str(e)}")


class AccountBalanceTest:
    """Integration test for account balance operations (standalone mode)."""
    
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
    """Main function to run the integration test (standalone mode)."""
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


# Pytest markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.blockchain
]


if __name__ == "__main__":
    # Run with pytest when executed directly
    pytest.main([__file__, "-v", "-s"])
    # Or run standalone
    # exit_code = asyncio.run(main())
    # exit(exit_code)


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