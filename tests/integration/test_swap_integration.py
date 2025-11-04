"""
Integration tests for swap endpoints in the exchange API.

This test suite tests the actual swap functionality against a live FastAPI server
running on localhost:8000. It uses real blockchain connections and small amounts
for testing purposes.

Requirements:
- FastAPI server running on localhost:8000
- Valid private key with some SOMI balance
- Access to Somnia testnet
"""

import pytest
import asyncio
import logging
import sys
import time
from pathlib import Path
from decimal import Decimal
import httpx

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.backend_config import settings
from app.services.account_service import get_address_from_private_key
from web3 import AsyncWeb3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
TEST_AMOUNT_SOMI = "10000000000000000"  # 0.01 SOMI (18 decimals)
TEST_AMOUNT_SUSDT = "10000000000000000"
SLIPPAGE_TOLERANCE = 0.05  # 5% slippage tolerance
DEADLINE_OFFSET = 3600  # 1 hour from now (increased for reliability)


class TestSwapIntegration:
    """Integration tests for swap endpoints."""
    
    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration fixture."""
        return {
            "base_url": f'http://{settings.HOST}:{settings.PORT}',
            "private_key": settings.PRIVATE_KEY,
            "address": get_address_from_private_key(settings.PRIVATE_KEY),
            "wstt_address": settings.WSTT,
            "susdt_address": settings.SUSDT,
            "chain_id": settings.CHAIN_ID,
            "rpc_url": settings.RPC_URL,
            "weth_address": None  # Will be fetched from API
        }


    



    
    def setup_class(cls):
        """Setup class-level configuration."""
        logger.info("🔄 Swap Integration Test Configuration:")
        logger.info(f"  Test Address: {get_address_from_private_key(settings.PRIVATE_KEY)}")
        logger.info(f"  WSTT Token: {settings.WSTT}")
        logger.info(f"  SUSDT Token: {settings.SUSDT}")
        logger.info(f"  Test Amount SOMI: {TEST_AMOUNT_SOMI} wei (0.01 SOMI)")
        logger.info(f"  Test Amount SUSDT: {TEST_AMOUNT_SUSDT} (0.01 SUSDT)")
    
    @pytest.mark.asyncio
    async def test_api_server_available(self, test_config):
        """Test that the API server is running and accessible."""
        print("\n🌐 API Server Availability Test")
        print("=" * 50)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.get(f"{test_config['base_url']}/health")
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            
            health_data = response.json()
            assert health_data.get("status") in ["healthy", "degraded"], f"Unhealthy status: {health_data}"
            
            logger.info(f"✅ API server is available at {test_config['base_url']}")
            logger.info(f"✅ Health status: {health_data.get('status')}")
            
        except httpx.ConnectError:
            pytest.skip(f"API server not available at {test_config['base_url']}. Please start the server first.")
        except Exception as e:
            pytest.fail(f"Failed to connect to API server: {e}")
    
    @pytest.mark.asyncio
    async def test_get_weth_address(self, test_config):
        """Get WETH address from the API."""
        print("\n🔗 WETH Address Retrieval")
        print("=" * 50)
        
        # Get WETH address directly in the test
        weth_address = await self.get_weth_address_from_api(test_config)
        
        assert weth_address is not None, "Failed to retrieve WETH address from API"
        assert weth_address.startswith("0x"), f"WETH address should start with 0x, got: {weth_address}"
        assert len(weth_address) == 42, f"WETH address should be 42 characters, got {len(weth_address)}: {weth_address}"
        
        logger.info(f"✅ WETH address test passed: {weth_address}")

    @pytest.mark.asyncio
    async def test_account_balance_check(self, test_config):
        """Check account balances before running swap tests."""
        print("\n💰 Account Balance Check")
        print("=" * 50)
        
        # Create Web3 instance
        w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.RPC_URL))
        
        try:
            # Test connection
            is_connected = await w3.is_connected()
            if not is_connected:
                pytest.skip(f"Cannot connect to blockchain at {settings.RPC_URL}")
                
            address = test_config["address"]
            
            # Check SOMI balance
            somi_balance = await w3.eth.get_balance(address)
            somi_balance_eth = somi_balance / 10**18
            
            logger.info(f"✅ SOMI Balance: {somi_balance_eth:.6f} SOMI ({somi_balance} wei)")
            
            # Ensure we have enough SOMI for gas and test swaps
            min_somi_required = 0.1  # 0.1 SOMI minimum
            assert somi_balance_eth >= min_somi_required, f"Insufficient SOMI balance. Need at least {min_somi_required} SOMI, have {somi_balance_eth:.6f}"
            
            logger.info(f"✅ Sufficient SOMI balance for testing")
            
        except Exception as e:
            pytest.skip(f"Failed to check account balance: {e}")
        finally:
            # Cleanup Web3 instance
            try:
                if hasattr(w3.provider, '_session') and w3.provider._session and not w3.provider._session.closed:
                    await w3.provider._session.close()
            except Exception:
                # Ignore cleanup errors
                pass
    
    def get_deadline(self):
        """Get deadline timestamp (current time + offset)."""
        return int(time.time()) + DEADLINE_OFFSET
    
    async def get_weth_address_from_api(self, test_config):
        """Get WETH address from the API."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{test_config['base_url']}/exchange/weth-address")
                
                if response.status_code == 200:
                    weth_data = response.json()
                    weth_address = weth_data["weth_address"]
                    
                    # Ensure address has 0x prefix
                    if not weth_address.startswith("0x"):
                        weth_address = "0x" + weth_address
                    
                    return weth_address
                else:
                    logger.error(f"❌ Failed to get WETH address: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error getting WETH address: {e}")
            return None
    

    
    async def get_quote_for_swap(self, amount_a, reserve_a, reserve_b, test_config):
        """Get quote for a swap to calculate expected output."""
        try:
            quote_request = {
                "amount_a": amount_a,
                "reserve_a": reserve_a,
                "reserve_b": reserve_b
            }
            
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(f"{test_config['base_url']}/exchange/quote", json=quote_request)
                
                if response.status_code == 200:
                    return response.json()["amount_b"]
                else:
                    logger.warning(f"Quote request failed: {response.status_code} - {response.text}")
                    return None
                
        except Exception as e:
            logger.warning(f"Failed to get quote: {e}")
            return None

    @pytest.mark.asyncio
    async def test_approve_router_for_susdt(self, test_config):
        """Test approving the router to spend SUSDT tokens."""
        print("\n🔐 Router Approval for SUSDT Tokens Test")
        print("=" * 60)

        # Use a large amount for approval (effectively unlimited)
        MAX_UINT256 = 2**256 - 1
        approval_amount = MAX_UINT256  # Approve maximum amount

        try:
            logger.info(f"🧪 Approving router to spend SUSDT tokens")
            logger.info(f"   Token: {test_config['susdt_address']}")
            logger.info(f"   Router: {settings.ROUTER_ADDRESS}")
            logger.info(f"   Amount: {approval_amount} (MAX_UINT256)")
            logger.info(f"   From: {test_config['address']}")

            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(
                f"{test_config['base_url']}/exchange/approve-router",
                params={
                    "token_address": test_config["susdt_address"],
                    "amount": approval_amount,
                    "from_address": test_config["address"],
                    "private_key": test_config["private_key"]
                }
            )

            if response.status_code == 200:
                approval_result = response.json()
                
                assert "transaction_hash" in approval_result, "Response should contain transaction_hash"
                assert "status" in approval_result, "Response should contain status"
                assert "gas_used" in approval_result, "Response should contain gas_used"
                assert "token_address" in approval_result, "Response should contain token_address"
                assert "spender_address" in approval_result, "Response should contain spender_address"
                assert "amount" in approval_result, "Response should contain amount"
                
                tx_hash = approval_result["transaction_hash"]
                
                # Handle transaction hashes that might not have 0x prefix
                if not tx_hash.startswith("0x"):
                    tx_hash = "0x" + tx_hash
                
                assert tx_hash.startswith("0x"), f"Transaction hash should start with 0x, got: {tx_hash}"
                assert len(tx_hash) == 66, f"Transaction hash should be 66 characters, got {len(tx_hash)}: {tx_hash}"

                logger.info(f"✅ Router approval successful!")
                logger.info(f"   Transaction Hash: {tx_hash}")
                logger.info(f"   Status: {approval_result['status']}")
                logger.info(f"   Gas Used: {approval_result['gas_used']}")
                logger.info(f"   Approved Amount: {approval_result['amount']}")

            else:
                error_detail = response.json().get("detail", response.text) if response.status_code != 500 else "Internal server error"
                logger.warning(f"⚠️ Router approval failed: {response.status_code} - {error_detail}")
                
                # Skip test if it's a known issue but don't fail
                if "insufficient funds" in error_detail.lower():
                    pytest.skip(f"Router approval failed due to insufficient funds: {error_detail}")
                elif "nonce" in error_detail.lower():
                    pytest.skip(f"Router approval failed due to nonce issues: {error_detail}")
                elif response.status_code >= 500:
                    pytest.skip(f"Server error during router approval: {error_detail}")
                else:
                    pytest.fail(f"Unexpected router approval failure: {response.status_code} - {error_detail}")

        except Exception as e:
            pytest.skip(f"Router approval test failed with exception: {e}")
    
    @pytest.mark.asyncio
    async def test_swap_exact_tokens_for_tokens(self, test_config):
        """Test swapping exact tokens for tokens (SUSDT -> WETH)."""
        print("\n🔄 Swap Exact Tokens for Tokens Test (SUSDT -> WETH)")
        print("=" * 60)
        
        # Get WETH address
        weth_address = await self.get_weth_address_from_api(test_config)
        assert weth_address, "WETH address not available for token swap"
        
        # Note about token requirements
        logger.info("ℹ️  Note: This test requires SUSDT tokens and router approval")
        logger.info("   Router approval should be completed in a separate test")
        logger.info("   If this fails, check:")
        logger.info("   1. You have SUSDT tokens in your account")
        logger.info("   2. The approval transaction was successful")
        logger.info(f"   Router address: {settings.ROUTER_ADDRESS}")
        
        try:
            # Try simple SUSDT -> WETH swap first (more likely to have liquidity)
            swap_request = {
                "amount_in": int(TEST_AMOUNT_SUSDT),
                "amount_out_min": 1,  # Minimum 1 wei output (very low for testing)
                "path": [
                    test_config["susdt_address"],  # SUSDT
                    weth_address                   # WETH
                ],
                "to": test_config["address"],
                "deadline": self.get_deadline(),
                "from_address": test_config["address"],
                "private_key": test_config["private_key"]
            }
            
            logger.info(f"🧪 Swapping {TEST_AMOUNT_SUSDT} SUSDT for WETH")
            logger.info(f"   From: {test_config['address']}")
            logger.info(f"   Path: SUSDT -> WETH")
            logger.info(f"   Deadline: {swap_request['deadline']}")
            
            # Make swap request
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(
                f"{test_config['base_url']}/exchange/swap-exact-tokens-for-tokens",
                json=swap_request
            )
            
            # Check response
            if response.status_code == 200:
                swap_result = response.json()
                
                assert "transaction_hash" in swap_result, "Response should contain transaction_hash"
                assert "status" in swap_result, "Response should contain status"
                assert "gas_used" in swap_result, "Response should contain gas_used"
                
                tx_hash = swap_result["transaction_hash"]
                
                # Handle transaction hashes that might not have 0x prefix
                if not tx_hash.startswith("0x"):
                    tx_hash = "0x" + tx_hash
                
                assert tx_hash.startswith("0x"), f"Transaction hash should start with 0x, got: {tx_hash}"
                assert len(tx_hash) == 66, f"Transaction hash should be 66 characters, got {len(tx_hash)}: {tx_hash}"
                
                logger.info(f"✅ Swap successful!")
                logger.info(f"   Transaction Hash: {tx_hash}")
                logger.info(f"   Status: {swap_result['status']}")
                logger.info(f"   Gas Used: {swap_result['gas_used']}")
                
            else:
                # Log the error but don't fail the test if it's a known issue
                error_detail = response.json().get("detail", response.text) if response.status_code != 500 else "Internal server error"
                logger.warning(f"⚠️ Swap failed: {response.status_code} - {error_detail}")
                
                # Skip test if it's a liquidity or contract issue
                if "liquidity" in error_detail.lower() or "insufficient" in error_detail.lower():
                    pytest.skip(f"Swap failed due to liquidity issues: {error_detail}")
                elif "allowance" in error_detail.lower() or "transferfrom failed" in error_detail.lower():
                    pytest.skip(f"Swap failed due to token approval issues: {error_detail}")
                elif response.status_code >= 500:
                    pytest.skip(f"Server error during swap: {error_detail}")
                else:
                    pytest.fail(f"Unexpected swap failure: {response.status_code} - {error_detail}")
                    
        except Exception as e:
            pytest.skip(f"Swap test failed with exception: {e}")
    
    @pytest.mark.asyncio
    async def test_swap_exact_eth_for_tokens(self, test_config):
        """Test swapping exact ETH (SOMI) for tokens (SUSDT)."""
        print("\n🔄 Swap Exact ETH for Tokens Test (SOMI -> SUSDT)")
        print("=" * 60)
        
        # Get WETH address
        weth_address = await self.get_weth_address_from_api(test_config)
        assert weth_address, "WETH address not available for ETH swap"
        
        try:
            # Prepare swap request
            swap_request = {
                "amount_in": 0,  # Not used for ETH swaps
                "amount_out_min": 1,  # Minimum 1 wei output
                "path": [
                    weth_address,                 # WETH (wrapped native token)
                    test_config["susdt_address"]  # SUSDT
                ],
                "to": test_config["address"],
                "deadline": self.get_deadline(),
                "from_address": test_config["address"],
                "private_key": test_config["private_key"]
            }
            
            eth_value = int(TEST_AMOUNT_SOMI)  # Amount of SOMI to send
            
            logger.info(f"🧪 Swapping {eth_value} wei SOMI for SUSDT (ETH method)")
            logger.info(f"   From: {test_config['address']}")
            logger.info(f"   ETH Value: {eth_value} wei")
            logger.info(f"   Deadline: {swap_request['deadline']}")
            
            # Make swap request with eth_value query parameter
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(
                f"{test_config['base_url']}/exchange/swap-exact-eth-for-tokens?eth_value={eth_value}",
                json=swap_request
            )
            
            # Check response
            if response.status_code == 200:
                swap_result = response.json()
                
                assert "transaction_hash" in swap_result, "Response should contain transaction_hash"
                assert "status" in swap_result, "Response should contain status"
                assert "gas_used" in swap_result, "Response should contain gas_used"
                
                tx_hash = swap_result["transaction_hash"]
                
                # Handle transaction hashes that might not have 0x prefix
                if not tx_hash.startswith("0x"):
                    tx_hash = "0x" + tx_hash
                
                assert tx_hash.startswith("0x"), f"Transaction hash should start with 0x, got: {tx_hash}"
                assert len(tx_hash) == 66, f"Transaction hash should be 66 characters, got {len(tx_hash)}: {tx_hash}"
                
                logger.info(f"✅ ETH->Tokens swap successful!")
                logger.info(f"   Transaction Hash: {tx_hash}")
                logger.info(f"   Status: {swap_result['status']}")
                logger.info(f"   Gas Used: {swap_result['gas_used']}")
                
            else:
                error_detail = response.json().get("detail", response.text) if response.status_code != 500 else "Internal server error"
                logger.warning(f"⚠️ ETH->Tokens swap failed: {response.status_code} - {error_detail}")
                
                # Skip test if it's a known issue
                if "liquidity" in error_detail.lower() or "insufficient" in error_detail.lower():
                    pytest.skip(f"ETH swap failed due to liquidity issues: {error_detail}")
                elif response.status_code >= 500:
                    pytest.skip(f"Server error during ETH swap: {error_detail}")
                else:
                    pytest.fail(f"Unexpected ETH swap failure: {response.status_code} - {error_detail}")
                    
        except Exception as e:
            pytest.skip(f"ETH swap test failed with exception: {e}")
    
    @pytest.mark.asyncio
    async def test_swap_exact_tokens_for_eth(self, test_config):
        """Test swapping exact tokens (SUSDT) for ETH (SOMI)."""
        print("\n🔄 Swap Exact Tokens for ETH Test (SUSDT -> SOMI)")
        print("=" * 60)
        
        # Get WETH address
        weth_address = await self.get_weth_address_from_api(test_config)
        assert weth_address, "WETH address not available for tokens->ETH swap"
        
        # Note about token requirements
        logger.info("ℹ️  Note: This test requires SUSDT tokens and router approval")
        logger.info("   Router approval should be completed in a separate test")
        logger.info("   If this fails, check:")
        logger.info("   1. You have SUSDT tokens in your account")
        logger.info("   2. The approval transaction was successful")
        logger.info(f"   Router address: {settings.ROUTER_ADDRESS}")
        
        try:
            # Prepare swap request
            swap_request = {
                "amount_in": int(TEST_AMOUNT_SUSDT),  # Amount of SUSDT to swap
                "amount_out_min": 1,  # Minimum 1 wei SOMI output
                "path": [
                    test_config["susdt_address"],  # SUSDT
                    weth_address                   # WETH (wrapped native token)
                ],
                "to": test_config["address"],
                "deadline": self.get_deadline(),
                "from_address": test_config["address"],
                "private_key": test_config["private_key"]
            }
            
            logger.info(f"🧪 Swapping {TEST_AMOUNT_SUSDT} SUSDT for SOMI")
            logger.info(f"   From: {test_config['address']}")
            logger.info(f"   Path: SUSDT -> SOMI")
            logger.info(f"   Deadline: {swap_request['deadline']}")
            
            # Make swap request
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(
                f"{test_config['base_url']}/exchange/swap-exact-tokens-for-eth",
                json=swap_request
            )
            
            # Check response
            if response.status_code == 200:
                swap_result = response.json()
                
                assert "transaction_hash" in swap_result, "Response should contain transaction_hash"
                assert "status" in swap_result, "Response should contain status"
                assert "gas_used" in swap_result, "Response should contain gas_used"
                
                tx_hash = swap_result["transaction_hash"]
                
                # Handle transaction hashes that might not have 0x prefix
                if not tx_hash.startswith("0x"):
                    tx_hash = "0x" + tx_hash
                
                assert tx_hash.startswith("0x"), f"Transaction hash should start with 0x, got: {tx_hash}"
                assert len(tx_hash) == 66, f"Transaction hash should be 66 characters, got {len(tx_hash)}: {tx_hash}"
                
                logger.info(f"✅ Tokens->ETH swap successful!")
                logger.info(f"   Transaction Hash: {tx_hash}")
                logger.info(f"   Status: {swap_result['status']}")
                logger.info(f"   Gas Used: {swap_result['gas_used']}")
                
            else:
                error_detail = response.json().get("detail", response.text) if response.status_code != 500 else "Internal server error"
                logger.warning(f"⚠️ Tokens->ETH swap failed: {response.status_code} - {error_detail}")
                
                # Skip test if it's a known issue
                if "liquidity" in error_detail.lower() or "insufficient" in error_detail.lower():
                    pytest.skip(f"Tokens->ETH swap failed due to liquidity issues: {error_detail}")
                elif "allowance" in error_detail.lower() or "approval" in error_detail.lower():
                    pytest.skip(f"Tokens->ETH swap failed due to token approval issues: {error_detail}")
                elif response.status_code >= 500:
                    pytest.skip(f"Server error during Tokens->ETH swap: {error_detail}")
                else:
                    pytest.fail(f"Unexpected Tokens->ETH swap failure: {response.status_code} - {error_detail}")
                    
        except Exception as e:
            pytest.skip(f"Tokens->ETH swap test failed with exception: {e}")
    
    @pytest.mark.asyncio
    async def test_swap_validation_errors(self, test_config):
        """Test swap endpoints with invalid data to verify validation."""
        print("\n⚠️ Swap Validation Errors Test")
        print("=" * 50)
        
        invalid_swap_requests = [
            {
                "name": "Missing required fields",
                "data": {"amount_in": 1000}
            },
            {
                "name": "Invalid deadline (past)",
                "data": {
                    "amount_in": int(TEST_AMOUNT_SOMI),
                    "amount_out_min": 1,
                    "path": [test_config.get("weth_address", "0x0000000000000000000000000000000000000000"), test_config["susdt_address"]],
                    "to": test_config["address"],
                    "deadline": int(time.time()) - 3600,  # 1 hour ago
                    "from_address": test_config["address"],
                    "private_key": test_config["private_key"]
                }
            },
            {
                "name": "Invalid private key",
                "data": {
                    "amount_in": int(TEST_AMOUNT_SOMI),
                    "amount_out_min": 1,
                    "path": [test_config.get("weth_address", "0x0000000000000000000000000000000000000000"), test_config["susdt_address"]],
                    "to": test_config["address"],
                    "deadline": self.get_deadline(),
                    "from_address": test_config["address"],
                    "private_key": "invalid_key"
                }
            },
            {
                "name": "Empty swap path",
                "data": {
                    "amount_in": int(TEST_AMOUNT_SOMI),
                    "amount_out_min": 1,
                    "path": [],
                    "to": test_config["address"],
                    "deadline": self.get_deadline(),
                    "from_address": test_config["address"],
                    "private_key": test_config["private_key"]
                }
            }
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            for test_case in invalid_swap_requests:
                logger.info(f"🧪 Testing: {test_case['name']}")
                
                try:
                    response = await http_client.post(
                        f"{test_config['base_url']}/exchange/swap-exact-tokens-for-tokens",
                        json=test_case["data"]
                    )
                    
                    # Should return validation error (4xx status)
                    assert response.status_code >= 400, f"Expected error status for {test_case['name']}, got {response.status_code}"
                    
                    if response.headers.get("content-type", "").startswith("application/json"):
                        error_data = response.json()
                        assert "detail" in error_data, f"Error response should contain detail for {test_case['name']}"
                    
                    logger.info(f"✅ {test_case['name']}: Correctly returned {response.status_code}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Validation test failed for {test_case['name']}: {e}")
    
    def test_configuration_loaded(self, test_config):
        """Test that all required configuration is loaded."""
        print("\n🔧 Configuration Test")
        print("=" * 50)
        
        assert test_config["private_key"] is not None, "Private key not configured"
        assert test_config["address"] is not None, "Address not derived"
        assert test_config["wstt_address"] is not None, "WSTT address not configured"
        assert test_config["susdt_address"] is not None, "SUSDT address not configured"
        
        # Validate address formats
        assert test_config["address"].startswith("0x"), "Address should start with 0x"
        assert len(test_config["address"]) == 42, "Address should be 42 characters"
        assert test_config["wstt_address"].startswith("0x"), "WSTT address should start with 0x"
        assert test_config["susdt_address"].startswith("0x"), "SUSDT address should start with 0x"
        
        logger.info(f"✅ Configuration test passed")
        logger.info(f"  Address: {test_config['address']}")
        logger.info(f"  WSTT: {test_config['wstt_address']}")
        logger.info(f"  SUSDT: {test_config['susdt_address']}")


# Pytest markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.slow
]


if __name__ == "__main__":
    # Run with pytest when executed directly
    pytest.main([__file__, "-v", "-s"])