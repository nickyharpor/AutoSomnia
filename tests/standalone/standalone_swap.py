#!/usr/bin/env python3
"""
Standalone integration test for swap endpoints.

This script tests the swap functionality against a live FastAPI server
without requiring pytest. It can be run directly to quickly test swap operations.

Usage:
    python tests/integration/standalone_swap.py

Requirements:
- FastAPI server running on localhost:8000
- Valid private key with some SOMI balance
- Access to Somnia testnet
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
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
TEST_AMOUNT_SUSDT = "100000000000000000"
DEADLINE_OFFSET = 300  # 5 minutes from now


class SwapIntegrationTest:
    """Standalone integration test for swap functionality."""
    
    def __init__(self):
        """Initialize the test with configuration."""
        self.base_url = f'http://{settings.HOST}:{settings.PORT}'
        self.private_key = settings.PRIVATE_KEY
        self.address = get_address_from_private_key(settings.PRIVATE_KEY)
        self.wstt_address = settings.WSTT
        self.susdt_address = settings.SUSDT
        self.chain_id = settings.CHAIN_ID
        self.rpc_url = settings.RPC_URL
        self.weth_address = None  # Will be fetched from API
        
        logger.info("🔄 Swap Integration Test Configuration:")
        logger.info(f"  API Base URL: {self.base_url}")
        logger.info(f"  Test Address: {self.address}")
        logger.info(f"  WSTT Token: {self.wstt_address}")
        logger.info(f"  SUSDT Token: {self.susdt_address}")
        logger.info(f"  Test Amount SOMI: {TEST_AMOUNT_SOMI} wei (0.01 SOMI)")

    @staticmethod
    def get_deadline():
        """Get deadline timestamp (current time + offset)."""
        return int(time.time()) + DEADLINE_OFFSET
    
    async def get_weth_address(self):
        """Get WETH address from the API."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/exchange/weth-address")
                
                if response.status_code == 200:
                    weth_data = response.json()
                    self.weth_address = weth_data["weth_address"]
                    logger.info(f"✅ WETH address: {self.weth_address}")
                    return True
                else:
                    logger.error(f"❌ Failed to get WETH address: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error getting WETH address: {e}")
            return False

    async def test_api_server_availability(self):
        """Test that the API server is running."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    health_data = response.json()
                    logger.info(f"✅ API server is available at {self.base_url}")
                    logger.info(f"✅ Health status: {health_data.get('status')}")
                    return True
                else:
                    logger.error(f"❌ Health check failed: {response.status_code}")
                    return False
                    
        except httpx.ConnectError:
            logger.error(f"❌ Cannot connect to API server at {self.base_url}")
            logger.error("   Please make sure the FastAPI server is running on localhost:8000")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking API server: {e}")
            return False
    
    async def check_account_balance(self):
        """Check account balance before running tests."""
        try:
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(self.rpc_url))
            
            # Check connection
            is_connected = await w3.is_connected()
            if not is_connected:
                logger.error(f"❌ Cannot connect to blockchain at {self.rpc_url}")
                return False
            
            # Check SOMI balance
            somi_balance = await w3.eth.get_balance(w3.to_checksum_address(self.address))
            somi_balance_eth = somi_balance / 10**18
            
            logger.info(f"✅ SOMI Balance: {somi_balance_eth:.6f} SOMI ({somi_balance} wei)")
            
            # Ensure we have enough SOMI
            min_somi_required = 0.1
            if somi_balance_eth < min_somi_required:
                logger.error(f"❌ Insufficient SOMI balance. Need at least {min_somi_required} SOMI, have {somi_balance_eth:.6f}")
                return False
            
            logger.info(f"✅ Sufficient SOMI balance for testing")
            
            # Cleanup
            try:
                if hasattr(w3.provider, '_session') and w3.provider._session:
                    await w3.provider._session.close()
            except Exception as e:
                logger.error(f"❌ No _session in w3.provider: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to check account balance: {e}")
            return False

    async def test_swap_exact_eth_for_tokens(self):
        """Test swapping exact ETH for tokens (SOMI -> SUSDT)."""
        logger.info("\n🔄 Testing Swap Exact ETH for Tokens (SOMI -> SUSDT)")
        logger.info("=" * 60)

        if not self.weth_address:
            logger.error("❌ WETH address not available")
            return False

        eth_value = int(TEST_AMOUNT_SOMI)

        try:
            swap_request = {
                "amount_in": 0,  # Not used for native token swaps
                "amount_out_min": 1,
                "path": [
                    self.weth_address,  # WETH (wrapped native token)
                    self.susdt_address  # SUSDT
                ],
                "to": self.address,
                "deadline": self.get_deadline(),
                "from_address": self.address,
                "private_key": self.private_key
            }
            
            logger.info(f"🧪 Swapping {eth_value} wei SOMI for SUSDT (ETH method)")
            logger.info(f"   From: {self.address}")
            logger.info(f"   ETH Value: {eth_value} wei")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/exchange/swap-exact-eth-for-tokens?eth_value={eth_value}",
                    json=swap_request
                )
                
                if response.status_code == 200:
                    swap_result = response.json()
                    tx_hash = swap_result["transaction_hash"]
                    
                    logger.info(f"✅ ETH->Tokens swap successful!")
                    logger.info(f"   Transaction Hash: {tx_hash}")
                    logger.info(f"   Status: {swap_result['status']}")
                    logger.info(f"   Gas Used: {swap_result['gas_used']}")
                    return True
                    
                else:
                    error_detail = response.json().get("detail", response.text) if response.status_code != 500 else "Internal server error"
                    logger.warning(f"⚠️ ETH->Tokens swap failed: {response.status_code} - {error_detail}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ ETH->Tokens swap test failed: {e}")
            return False

    async def test_swap_exact_tokens_for_tokens(self):
        """Test swapping exact tokens for tokens (SUSDT -> WSTT)."""
        logger.info("\n🔄 Testing Swap Exact Tokens for Tokens (SUSDT -> WSTT)")
        logger.info("=" * 60)

        # Check if we have SUSDT tokens first
        logger.info("ℹ️  Note: This test requires SUSDT tokens and router approval")
        logger.info("   Router approval should have been completed in the previous step")
        logger.info("   If this still fails, check:")
        logger.info("   1. You have SUSDT tokens in your account")
        logger.info("   2. The approval transaction was successful")
        logger.info(f"   Router address: {settings.ROUTER_ADDRESS}")

        try:
            swap_request = {
                "amount_in": int(TEST_AMOUNT_SUSDT),
                "amount_out_min": 1,  # Very low minimum for testing (1 wei)
                "path": [
                    self.susdt_address,  # SUSDT
                    self.wstt_address   # WSTT
                ],
                "to": self.address,
                "deadline": self.get_deadline(),
                "from_address": self.address,
                "private_key": self.private_key
            }

            logger.info(f"🧪 Swapping {TEST_AMOUNT_SUSDT} SUSDT for WSTT")
            logger.info(f"   From: {self.address}")
            logger.info(f"   Deadline: {swap_request['deadline']}")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/exchange/swap-exact-tokens-for-tokens",
                    json=swap_request
                )

                if response.status_code == 200:
                    swap_result = response.json()
                    tx_hash = swap_result["transaction_hash"]

                    logger.info(f"✅ Swap successful!")
                    logger.info(f"   Transaction Hash: {tx_hash}")
                    logger.info(f"   Status: {swap_result['status']}")
                    logger.info(f"   Gas Used: {swap_result['gas_used']}")
                    return True

                else:
                    error_detail = response.json().get("detail",
                                                       response.text) if response.status_code != 500 else "Internal server error"
                    logger.warning(f"⚠️ Swap failed: {response.status_code} - {error_detail}")

                    if "liquidity" in error_detail.lower():
                        logger.info("   This might be due to insufficient liquidity in the test pool")
                    elif "allowance" in error_detail.lower() or "transferfrom failed" in error_detail.lower():
                        logger.info("   ❌ Token approval required!")
                        logger.info("   You need to approve the router contract to spend your SUSDT tokens")
                        logger.info(f"   Router address: {settings.ROUTER_ADDRESS}")
                        logger.info("   Use a tool like Metamask or write an approval transaction")

                    return False

        except Exception as e:
            logger.error(f"❌ Swap test failed: {e}")
            return False

    async def test_approve_router_for_susdt(self):
        """Test approving the router to spend SUSDT tokens."""
        logger.info("\n🔐 Testing Router Approval for SUSDT Tokens")
        logger.info("=" * 60)

        # Use a large amount for approval (effectively unlimited)
        MAX_UINT256 = 2**256 - 1
        approval_amount = MAX_UINT256  # Approve maximum amount

        try:
            logger.info(f"🧪 Approving router to spend SUSDT tokens")
            logger.info(f"   Token: {self.susdt_address}")
            logger.info(f"   Router: {settings.ROUTER_ADDRESS}")
            logger.info(f"   Amount: {approval_amount} (MAX_UINT256)")
            logger.info(f"   From: {self.address}")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/exchange/approve-router",
                    params={
                        "token_address": self.susdt_address,
                        "amount": approval_amount,
                        "from_address": self.address,
                        "private_key": self.private_key
                    }
                )

                if response.status_code == 200:
                    approval_result = response.json()
                    tx_hash = approval_result["transaction_hash"]

                    logger.info(f"✅ Router approval successful!")
                    logger.info(f"   Transaction Hash: {tx_hash}")
                    logger.info(f"   Status: {approval_result['status']}")
                    logger.info(f"   Gas Used: {approval_result['gas_used']}")
                    logger.info(f"   Approved Amount: {approval_result['amount']}")
                    return True

                else:
                    error_detail = response.json().get("detail", response.text) if response.status_code != 500 else "Internal server error"
                    logger.warning(f"⚠️ Router approval failed: {response.status_code} - {error_detail}")
                    
                    if "insufficient funds" in error_detail.lower():
                        logger.info("   This might be due to insufficient SOMI for gas fees")
                    elif "nonce" in error_detail.lower():
                        logger.info("   This might be due to nonce issues - try again")
                    
                    return False

        except Exception as e:
            logger.error(f"❌ Router approval test failed: {e}")
            return False

    async def test_swap_exact_tokens_for_eth(self):
        """Test swapping exact tokens for ETH (SUSDT -> SOMI)."""
        logger.info("\n🔄 Testing Swap Exact Tokens for ETH (SUSDT -> SOMI)")
        logger.info("=" * 60)
        
        if not self.weth_address:
            logger.error("❌ WETH address not available")
            return False

        # Check if we have SUSDT tokens first
        logger.info("ℹ️  Note: This test requires SUSDT tokens and router approval")
        logger.info("   Router approval should have been completed in the previous step")
        logger.info("   If this still fails, check:")
        logger.info("   1. You have SUSDT tokens in your account")
        logger.info("   2. The approval transaction was successful")
        logger.info(f"   Router address: {settings.ROUTER_ADDRESS}")
        
        try:
            swap_request = {
                "amount_in": int(TEST_AMOUNT_SUSDT),
                "amount_out_min": 1,
                "path": [
                    self.susdt_address,  # SUSDT
                    self.weth_address   # WETH (wrapped native token)
                ],
                "to": self.address,
                "deadline": self.get_deadline(),
                "from_address": self.address,
                "private_key": self.private_key
            }
            
            logger.info(f"🧪 Swapping {TEST_AMOUNT_SUSDT} SUSDT for SOMI")
            logger.info(f"   From: {self.address}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/exchange/swap-exact-tokens-for-eth",
                    json=swap_request
                )
                
                if response.status_code == 200:
                    swap_result = response.json()
                    tx_hash = swap_result["transaction_hash"]
                    
                    logger.info(f"✅ Tokens->ETH swap successful!")
                    logger.info(f"   Transaction Hash: {tx_hash}")
                    logger.info(f"   Status: {swap_result['status']}")
                    logger.info(f"   Gas Used: {swap_result['gas_used']}")
                    return True
                    
                else:
                    error_detail = response.json().get("detail", response.text) if response.status_code != 500 else "Internal server error"
                    logger.warning(f"⚠️ Tokens->ETH swap failed: {response.status_code} - {error_detail}")
                    
                    if "allowance" in error_detail.lower() or "transferfrom failed" in error_detail.lower():
                        logger.info("   ❌ Token approval required!")
                        logger.info("   You need to approve the router contract to spend your SUSDT tokens")
                        logger.info(f"   Router address: {settings.ROUTER_ADDRESS}")
                        logger.info("   Use a tool like Metamask or write an approval transaction")
                    
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Tokens->ETH swap test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all swap integration tests."""
        logger.info("🚀 Starting Swap Integration Tests")
        logger.info("=" * 60)
        
        results = []
        
        # Test 1: API Server Availability
        logger.info("\n📡 Step 1: Checking API server availability")
        api_available = await self.test_api_server_availability()
        results.append(("API Server Available", api_available))
        
        if not api_available:
            logger.error("❌ Cannot proceed without API server. Please start the server first.")
            return False
        
        # Test 2: Get WETH Address
        logger.info("\n🔗 Step 2: Getting WETH address")
        weth_ok = await self.get_weth_address()
        results.append(("WETH Address Retrieved", weth_ok))
        
        if not weth_ok:
            logger.error("❌ Cannot proceed without WETH address.")
            return False
        
        # Test 3: Account Balance Check
        logger.info("\n💰 Step 3: Checking account balance")
        balance_ok = await self.check_account_balance()
        results.append(("Account Balance Check", balance_ok))
        
        if not balance_ok:
            logger.error("❌ Cannot proceed without sufficient balance.")
            return False
        
        # Test 4: Swap Exact ETH for Tokens
        logger.info("\n🔄 Step 4: Testing ETH-to-tokens swap")
        eth_swap = await self.test_swap_exact_eth_for_tokens()
        results.append(("Swap ETH for Tokens", eth_swap))

        # Test 5: Approve Router for SUSDT Tokens
        logger.info("\n🔐 Step 5: Approving router to spend SUSDT tokens")
        approval_ok = await self.test_approve_router_for_susdt()
        results.append(("Router Approval for SUSDT", approval_ok))
        
        if not approval_ok:
            logger.warning("⚠️ Router approval failed. Token swaps may fail.")
            logger.info("   Continuing with tests to demonstrate the difference...")

        # Test 6: Swap Exact Tokens for Tokens
        logger.info("\n🔄 Step 6: Testing token-to-token swap")
        tokens_swap = await self.test_swap_exact_tokens_for_tokens()
        results.append(("Swap Tokens for Tokens", tokens_swap))

        # Test 7: Swap Exact Tokens for ETH
        logger.info("\n🔄 Step 7: Testing tokens-to-ETH swap")
        tokens_eth_swap = await self.test_swap_exact_tokens_for_eth()
        results.append(("Swap Tokens for ETH", tokens_eth_swap))
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 SWAP INTEGRATION TEST RESULTS")
        logger.info("=" * 60)
        
        passed = 0
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{status} | {test_name}")
            if success:
                passed += 1
        
        total = len(results)
        logger.info(f"\n🎯 Summary: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            logger.info("🎉 All swap integration tests passed!")
            return True
        else:
            logger.warning("⚠️ Some tests failed. This might be due to:")
            logger.warning("   - Insufficient liquidity in test pools")
            logger.warning("   - Token approval requirements")
            logger.warning("   - Network connectivity issues")
            logger.warning("   - Contract configuration issues")
            return False


async def main():
    """Main function to run the swap integration tests."""
    test = SwapIntegrationTest()
    
    try:
        success = await test.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)