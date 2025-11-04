import json
import logging
from typing import List, Optional
from pathlib import Path

from web3 import Web3, AsyncWeb3
from web3.contract import AsyncContract
from web3.types import ChecksumAddress, TxReceipt
from app.core.backend_config import settings

logger = logging.getLogger(__name__)


class SomniaExchangeService:
    """Service to interact with SomniaExchangeRouter02 contract."""

    def __init__(self, web3_provider: AsyncWeb3, contract_address: str, abi_path: Optional[str] = None):
        """
        Initialize the SomniaExchangeService.

        Args:
            web3_provider: Web3 instance connected to the blockchain
            contract_address: Address of the SomniaExchangeRouter02 contract
            abi_path: Path to the ABI JSON file (defaults to app/abi/SomniaExchangeRouter02.json)
        """
        self.w3 = web3_provider
        self.contract_address = Web3.to_checksum_address(contract_address)

        # Load ABI
        if abi_path is None:
            abi_path = Path(__file__).parent.parent / "abi" / "SomniaExchangeRouter02.json"

        with open(abi_path, "r") as f:
            abi_data = json.load(f)
            self.abi = abi_data["abi"]

        # Initialize contract
        self.contract: AsyncContract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.abi
        )

        logger.info(f"SomniaExchangeService initialized with contract at {self.contract_address}")

    def _validate_private_key(self, private_key: str) -> str:
        """Validate and fix private key format."""
        if not private_key:
            raise ValueError("Private key cannot be None or empty")
        
        private_key = str(private_key).strip()
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
        
        # Validate private key length and format
        if len(private_key) != 66:
            raise ValueError(f"Invalid private key length: {len(private_key)}, expected 66 characters (0x + 64 hex). Key: {private_key[:10]}...")
        
        # Validate private key hex format
        try:
            int(private_key[2:], 16)
        except ValueError as e:
            raise ValueError(f"Invalid private key hex format: {private_key[:10]}... Error: {e}")
        
        return private_key

    def _validate_address(self, address: str) -> str:
        """Validate and fix address format."""
        # Handle None or empty addresses
        if not address:
            raise ValueError(f"Address cannot be None or empty: {address}")
        
        # Convert to string if needed
        address = str(address).strip()
        
        if not address.startswith('0x'):
            address = '0x' + address
        
        # Validate address length and format
        if len(address) != 42:
            raise ValueError(f"Invalid address length: {len(address)}, expected 42 characters. Address: '{address}'")
        
        # Validate hex format - check each character
        hex_part = address[2:]
        for i, char in enumerate(hex_part):
            if char not in '0123456789abcdefABCDEF':
                raise ValueError(f"Invalid hex character '{char}' at position {i+2} in address: '{address}'")
        
        # Validate hex format
        try:
            int(hex_part, 16)  # Check if the part after 0x is valid hex
        except ValueError as e:
            raise ValueError(f"Invalid hex address format: '{address}'. Hex part: '{hex_part}'. Error: {e}")
        
        try:
            result = Web3.to_checksum_address(address)
            return result
        except Exception as e:
            raise ValueError(f"Failed to convert to checksum address: '{address}'. Error: {e}")

    # ==================== View Functions ====================

    async def get_weth_address(self) -> ChecksumAddress:
        """Get the WETH token address."""
        try:
            result = await self.contract.functions.WETH().call()
            logger.info(f"WETH address: {result}")
            return result
        except Exception as e:
            logger.error(f"Error getting WETH address: {e}")
            raise

    async def get_factory_address(self) -> ChecksumAddress:
        """Get the factory contract address."""
        try:
            result = await self.contract.functions.factory().call()
            logger.info(f"Factory address: {result}")
            return result
        except Exception as e:
            logger.error(f"Error getting factory address: {e}")
            raise

    async def get_amount_out(self, amount_in: int, reserve_in: int, reserve_out: int) -> int:
        """Get the output amount for a given input amount."""
        try:
            result = await self.contract.functions.getAmountOut(amount_in, reserve_in, reserve_out).call()
            logger.info(f"Amount out: {result}")
            return result
        except Exception as e:
            logger.error(f"Error calculating amount out: {e}")
            raise

    async def get_amount_in(self, amount_out: int, reserve_in: int, reserve_out: int) -> int:
        """Get the input amount required for a given output amount."""
        try:
            result = await self.contract.functions.getAmountIn(amount_out, reserve_in, reserve_out).call()
            logger.info(f"Amount in: {result}")
            return result
        except Exception as e:
            logger.error(f"Error calculating amount in: {e}")
            raise

    async def get_amounts_out(self, amount_in: int, path: List[str]) -> List[int]:
        """Get output amounts for a token swap path."""
        try:
            path = [self._validate_address(addr) for addr in path]
            result = await self.contract.functions.getAmountsOut(amount_in, path).call()
            logger.info(f"Amounts out for path: {result}")
            return result
        except Exception as e:
            logger.error(f"Error getting amounts out for path {path}: {e}")
            raise ValueError(f"Cannot get amounts out - likely no liquidity for this path: {e}")

    async def get_amounts_in(self, amount_out: int, path: List[str]) -> List[int]:
        """Get input amounts required for a token swap path."""
        try:
            path = [self._validate_address(addr) for addr in path]
            result = await self.contract.functions.getAmountsIn(amount_out, path).call()
            logger.info(f"Amounts in for path: {result}")
            return result
        except Exception as e:
            logger.error(f"Error getting amounts in: {e}")
            raise

    async def quote(self, amount_a: int, reserve_a: int, reserve_b: int) -> int:
        """Get the quote for token B given token A amount and reserves."""
        try:
            result = await self.contract.functions.quote(amount_a, reserve_a, reserve_b).call()
            logger.info(f"Quote: {result}")
            return result
        except Exception as e:
            logger.error(f"Error getting quote: {e}")
            raise

    # ==================== Token Approval Functions ====================

    async def approve_token(
        self,
        token_address: str,
        spender_address: str,
        amount: int,
        from_address: str,
        private_key: str
    ) -> TxReceipt:
        """
        Approve a spender (like router) to spend tokens on behalf of the owner.
        
        Args:
            token_address: Address of the ERC-20 token contract
            spender_address: Address that will be approved to spend tokens (usually router)
            amount: Amount of tokens to approve (in wei/smallest unit)
            from_address: Address of the token owner
            private_key: Private key of the token owner
            
        Returns:
            Transaction receipt
        """
        try:
            token_address = self._validate_address(token_address)
            spender_address = self._validate_address(spender_address)
            from_address = self._validate_address(from_address)
            from_address_checksum = Web3.to_checksum_address(from_address)

            # Standard ERC-20 ABI for approve function
            erc20_abi = [
                {
                    "constant": False,
                    "inputs": [
                        {"name": "spender", "type": "address"},
                        {"name": "value", "type": "uint256"}
                    ],
                    "name": "approve",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                }
            ]

            token_address_checksum = Web3.to_checksum_address(token_address)

            # Create token contract instance
            token_contract = self.w3.eth.contract(
                address=token_address_checksum,
                abi=erc20_abi
            )

            # Build approval transaction
            tx = await token_contract.functions.approve(
                spender_address, amount
            ).build_transaction({
                "from": from_address,
                "nonce": await self.w3.eth.get_transaction_count(from_address_checksum),
                "gas": settings.GAS_LIMIT,
                "gasPrice": await self.w3.eth.gas_price,
            })

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"Token approval transaction: {tx_hash.hex()}")
            logger.info(f"Approved {amount} tokens at {token_address} for spender {spender_address}")
            
            return receipt
            
        except Exception as e:
            logger.error(f"Error approving token: {e}")
            raise

    async def approve_router_for_token(
        self,
        token_address: str,
        amount: int,
        from_address: str,
        private_key: str
    ) -> TxReceipt:
        """
        Convenience method to approve the router contract to spend tokens.
        
        Args:
            token_address: Address of the ERC-20 token contract
            amount: Amount of tokens to approve (in wei/smallest unit)
            from_address: Address of the token owner
            private_key: Private key of the token owner
            
        Returns:
            Transaction receipt
        """
        return await self.approve_token(
            token_address=token_address,
            spender_address=self.contract_address,  # Router contract address
            amount=amount,
            from_address=from_address,
            private_key=private_key
        )

    # ==================== Liquidity Functions ====================

    async def add_liquidity(
        self,
        token_a: str,
        token_b: str,
        amount_a_desired: int,
        amount_b_desired: int,
        amount_a_min: int,
        amount_b_min: int,
        to: str,
        deadline: int,
        from_address: str,
        private_key: str
    ) -> TxReceipt:
        """Add liquidity to a token pair."""
        try:
            token_a = self._validate_address(token_a)
            token_b = self._validate_address(token_b)
            to = self._validate_address(to)
            from_address = self._validate_address(from_address)
            from_address_checksum = Web3.to_checksum_address(from_address)

            tx = await self.contract.functions.addLiquidity(
                token_a, token_b, amount_a_desired, amount_b_desired,
                amount_a_min, amount_b_min, to, deadline
            ).build_transaction({
                "from": from_address,
                "nonce": await self.w3.eth.get_transaction_count(from_address_checksum),
                "gas": settings.GAS_LIMIT,
                "gasPrice": await self.w3.eth.gas_price,
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.info(f"Add liquidity transaction: {tx_hash.hex()}")
            return receipt
        except Exception as e:
            logger.error(f"Error adding liquidity: {e}")
            raise

    async def swap_exact_tokens_for_tokens(
        self,
        amount_in: int,
        amount_out_min: int,
        path: List[str],
        to: str,
        deadline: int,
        from_address: str,
        private_key: str
    ) -> TxReceipt:
        """Swap exact amount of tokens for tokens."""
        try:
            logger.info(f"Starting swap_exact_tokens_for_tokens with path: {path}")
            
            # Validate path
            if not path or len(path) < 2:
                raise ValueError(f"Invalid swap path: must contain at least 2 addresses, got {len(path) if path else 0}: {path}")
            
            # Validate all addresses
            path = [self._validate_address(addr) for addr in path]
            to = self._validate_address(to)
            from_address = self._validate_address(from_address)
            from_address_checksum = Web3.to_checksum_address(from_address)
            
            logger.info(f"All addresses validated successfully. Path: {path}")

            logger.info(f"Building transaction with parameters:")
            logger.info(f"  amount_in: {amount_in}")
            logger.info(f"  amount_out_min: {amount_out_min}")
            logger.info(f"  path: {path}")
            logger.info(f"  to: {to}")
            logger.info(f"  deadline: {deadline}")
            logger.info(f"  from_address: {from_address}")
            
            try:
                tx = await self.contract.functions.swapExactTokensForTokens(
                    amount_in, amount_out_min, path, to, deadline
                ).build_transaction({
                    "from": from_address,
                    "nonce": await self.w3.eth.get_transaction_count(from_address_checksum),
                    "gas": settings.GAS_LIMIT,
                    "gasPrice": await self.w3.eth.gas_price,
                })
                logger.info(f"Transaction built successfully: {tx}")
            except Exception as e:
                logger.error(f"Error building transaction: {e}")
                raise

            # Validate private key
            private_key = self._validate_private_key(private_key)
            logger.info(f"Signing transaction with validated private_key length: {len(private_key)}")
            
            try:
                signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
                logger.info(f"Transaction signed successfully")
            except Exception as e:
                logger.error(f"Error signing transaction: {e}")
                raise

            try:
                tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                logger.info(f"Transaction sent successfully: {tx_hash.hex()}")
            except Exception as e:
                logger.error(f"Error sending transaction: {e}")
                raise

            try:
                receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
                logger.info(f"Swap exact tokens for tokens transaction: {tx_hash.hex()}")
                return receipt
            except Exception as e:
                logger.error(f"Error waiting for transaction receipt: {e}")
                raise
        except Exception as e:
            logger.error(f"Error swapping exact tokens for tokens: {e}")
            raise

    async def swap_exact_eth_for_tokens(
        self,
        amount_out_min: int,
        path: List[str],
        to: str,
        deadline: int,
        from_address: str,
        private_key: str,
        eth_value: int
    ) -> TxReceipt:
        """Swap exact ETH for tokens."""
        try:
            path = [self._validate_address(addr) for addr in path]
            to = self._validate_address(to)
            from_address = self._validate_address(from_address)
            from_address_checksum = Web3.to_checksum_address(from_address)

            tx = await self.contract.functions.swapExactETHForTokens(
                amount_out_min, path, to, deadline
            ).build_transaction({
                "from": from_address,
                "value": eth_value,
                "nonce": await self.w3.eth.get_transaction_count(from_address_checksum),
                "gas": settings.GAS_LIMIT,
                "gasPrice": await self.w3.eth.gas_price,
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.info(f"Swap exact ETH for tokens transaction: {tx_hash.hex()}")
            return receipt
        except Exception as e:
            logger.error(f"Error swapping exact ETH for tokens: {e}")
            raise

    async def swap_exact_tokens_for_eth(
        self,
        amount_in: int,
        amount_out_min: int,
        path: List[str],
        to: str,
        deadline: int,
        from_address: str,
        private_key: str
    ) -> TxReceipt:
        """Swap exact tokens for ETH."""
        try:
            path = [self._validate_address(addr) for addr in path]
            to = self._validate_address(to)
            from_address = self._validate_address(from_address)
            from_address_checksum = Web3.to_checksum_address(from_address)

            tx = await self.contract.functions.swapExactTokensForETH(
                amount_in, amount_out_min, path, to, deadline
            ).build_transaction({
                "from": from_address,
                "nonce": await self.w3.eth.get_transaction_count(from_address_checksum),
                "gas": settings.GAS_LIMIT,
                "gasPrice": await self.w3.eth.gas_price,
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.info(f"Swap exact tokens for ETH transaction: {tx_hash.hex()}")
            return receipt
        except Exception as e:
            logger.error(f"Error swapping exact tokens for ETH: {e}")
            raise

    async def remove_liquidity(
        self,
        token_a: str,
        token_b: str,
        liquidity: int,
        amount_a_min: int,
        amount_b_min: int,
        to: str,
        deadline: int,
        from_address: str,
        private_key: str
    ) -> TxReceipt:
        """Remove liquidity from a token pair."""
        try:
            token_a = self._validate_address(token_a)
            token_b = self._validate_address(token_b)
            to = self._validate_address(to)
            from_address = self._validate_address(from_address)
            from_address_checksum = Web3.to_checksum_address(from_address)

            tx = await self.contract.functions.removeLiquidity(
                token_a, token_b, liquidity, amount_a_min, amount_b_min, to, deadline
            ).build_transaction({
                "from": from_address,
                "nonce": await self.w3.eth.get_transaction_count(from_address_checksum),
                "gas": settings.GAS_LIMIT,
                "gasPrice": await self.w3.eth.gas_price,
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.info(f"Remove liquidity transaction: {tx_hash.hex()}")
            return receipt
        except Exception as e:
            logger.error(f"Error removing liquidity: {e}")
            raise
