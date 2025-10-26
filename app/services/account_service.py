import logging
from typing import Dict, List, Optional
from decimal import Decimal

from web3 import Web3, AsyncWeb3
from eth_account import Account
from mnemonic import Mnemonic

from app.models.account_models import (
    EVMAccount,
    TokenBalance,
    AccountPortfolio,
    AccountCreateRequest,
    AccountCreateResponse,
)

logger = logging.getLogger(__name__)


def _validate_address(address: str) -> str:
    """Validate and format Ethereum address."""
    try:
        return Web3.to_checksum_address(address)
    except Exception as e:
        logger.error(f"Invalid address format: {address}")
        raise ValueError(f"Invalid Ethereum address: {address}")


def _wei_to_eth(wei_amount: int) -> Decimal:
    """Convert wei to ETH."""
    return Decimal(wei_amount) / Decimal(10**18)


def _eth_to_wei(eth_amount: Decimal) -> int:
    """Convert ETH to wei."""
    return int(eth_amount * Decimal(10**18))


class AccountService:
    """Service for managing EVM-compatible Web3 accounts."""

    def __init__(self, web3_provider: AsyncWeb3, chain_id: int = 1):
        """
        Initialize the AccountService.

        Args:
            web3_provider: Web3 instance connected to the blockchain
            chain_id: Chain ID for the network (1=Ethereum mainnet)
        """
        self.w3 = web3_provider
        self.chain_id = chain_id
        
        # Standard ERC-20 ABI for token operations
        self.erc20_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "symbol",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "name",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            }
        ]
        
        logger.info(f"AccountService initialized for chain ID {chain_id}")

    # ==================== Account Creation/Import ====================

    async def create_account(self, request: AccountCreateRequest) -> AccountCreateResponse:
        """
        Create a new EVM account or import existing one.
        
        Args:
            request: Account creation request
            
        Returns:
            AccountCreateResponse with account details and mnemonic (if generated)
        """
        try:
            mnemonic_phrase = None
            
            if request.import_private_key:
                # Import existing account
                private_key = request.import_private_key
                if not private_key.startswith('0x'):
                    private_key = '0x' + private_key
                    
                account = Account.from_key(private_key)
                logger.info(f"Imported account: {account.address}")
            else:
                # Generate new account with mnemonic
                mnemo = Mnemonic("english")
                mnemonic_phrase = mnemo.generate(strength=128)
                seed = mnemo.to_seed(mnemonic_phrase)
                account = Account.from_mnemonic(mnemonic_phrase)
                logger.info(f"Generated new account: {account.address}")

            # Get current balance and nonce
            balance_wei = await self.w3.eth.get_balance(account.address)
            balance_eth = _wei_to_eth(balance_wei)
            nonce = await self.w3.eth.get_transaction_count(account.address)

            # Create EVM account model
            evm_account = EVMAccount(
                address=account.address,
                private_key=account.key.hex(),
                balance=balance_eth,
                nonce=nonce,
                chain_id=request.chain_id
            )

            return AccountCreateResponse(
                account=evm_account,
                mnemonic=mnemonic_phrase
            )

        except Exception as e:
            logger.error(f"Error creating account: {e}")
            raise

    async def import_account_from_mnemonic(self, mnemonic: str, chain_id: int = 1) -> AccountCreateResponse:
        """
        Import account from mnemonic phrase.
        
        Args:
            mnemonic: 12-word mnemonic phrase
            chain_id: Chain ID for the account
            
        Returns:
            AccountCreateResponse with imported account
        """
        try:
            # Validate mnemonic
            mnemo = Mnemonic("english")
            if not mnemo.check(mnemonic):
                raise ValueError("Invalid mnemonic phrase")

            account = Account.from_mnemonic(mnemonic)
            
            # Get current balance and nonce
            balance_wei = await self.w3.eth.get_balance(account.address)
            balance_eth = _wei_to_eth(balance_wei)
            nonce = await self.w3.eth.get_transaction_count(account.address)

            evm_account = EVMAccount(
                address=account.address,
                private_key=account.key.hex(),
                balance=balance_eth,
                nonce=nonce,
                chain_id=chain_id
            )

            logger.info(f"Imported account from mnemonic: {account.address}")
            return AccountCreateResponse(account=evm_account, mnemonic=None)

        except Exception as e:
            logger.error(f"Error importing account from mnemonic: {e}")
            raise

    # ==================== Balance Operations ====================

    async def get_eth_balance(self, address: str) -> Decimal:
        """
        Get ETH balance for an address.
        
        Args:
            address: Ethereum address
            
        Returns:
            Balance in ETH
        """
        try:
            address = _validate_address(address)
            address_checksum = Web3.to_checksum_address(address)
            balance_wei = await self.w3.eth.get_balance(address_checksum)
            balance_eth = _wei_to_eth(balance_wei)
            logger.info(f"ETH balance for {address}: {balance_eth}")
            return balance_eth
        except Exception as e:
            logger.error(f"Error getting ETH balance for {address}: {e}")
            raise

    async def get_token_balance(self, address: str, token_address: str) -> TokenBalance:
        """
        Get ERC-20 token balance for an address.
        
        Args:
            address: Account address
            token_address: Token contract address
            
        Returns:
            TokenBalance object with token details
        """
        try:
            address = _validate_address(address)
            token_address = _validate_address(token_address)
            token_address_checksum = Web3.to_checksum_address(token_address)
            
            # Create token contract instance
            token_contract = self.w3.eth.contract(
                address=token_address_checksum,
                abi=self.erc20_abi
            )
            
            # Get token details
            balance_raw = await token_contract.functions.balanceOf(address).call()
            decimals = await token_contract.functions.decimals().call()
            symbol = await token_contract.functions.symbol().call()
            name = await token_contract.functions.name().call()
            
            # Convert balance to decimal format
            balance = Decimal(balance_raw) / Decimal(10**decimals)
            
            token_balance = TokenBalance(
                token_address=token_address,
                token_symbol=symbol,
                token_name=name,
                balance=balance,
                decimals=decimals
            )
            
            logger.info(f"Token balance for {address}: {balance} {symbol}")
            return token_balance
            
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            raise

    async def get_multiple_token_balances(
        self, 
        address: str, 
        token_addresses: List[str]
    ) -> Dict[str, TokenBalance]:
        """
        Get balances for multiple tokens.
        
        Args:
            address: Account address
            token_addresses: List of token contract addresses
            
        Returns:
            Dictionary of token balances keyed by token address
        """
        try:
            balances = {}
            for token_address in token_addresses:
                try:
                    balance = await self.get_token_balance(address, token_address)
                    balances[token_address.lower()] = balance
                except Exception as e:
                    logger.warning(f"Failed to get balance for token {token_address}: {e}")
                    continue
            
            logger.info(f"Retrieved {len(balances)} token balances for {address}")
            return balances
            
        except Exception as e:
            logger.error(f"Error getting multiple token balances: {e}")
            raise

    # ==================== Account Portfolio ====================

    async def get_account_portfolio(
        self, 
        address: str, 
        token_addresses: Optional[List[str]] = None
    ) -> AccountPortfolio:
        """
        Get complete account portfolio including ETH and token balances.
        
        Args:
            address: Account address
            token_addresses: Optional list of token addresses to include
            
        Returns:
            AccountPortfolio with complete balance information
        """
        try:
            address = _validate_address(address)
            
            # Get ETH balance and nonce
            eth_balance = await self.get_eth_balance(address)
            address_checksum = Web3.to_checksum_address(address)
            nonce = await self.w3.eth.get_transaction_count(address_checksum)
            
            # Create EVM account (without private key for security)
            evm_account = EVMAccount(
                address=address,
                private_key="",  # Don't expose private key in portfolio
                balance=eth_balance,
                nonce=nonce,
                chain_id=self.chain_id
            )
            
            # Get token balances if requested
            token_balances = {}
            if token_addresses:
                token_balances = await self.get_multiple_token_balances(address, token_addresses)
            
            portfolio = AccountPortfolio(
                account=evm_account,
                token_balances=token_balances,
                total_value_usd=None,  # Would need price oracle integration
                last_updated=int((await self.w3.eth.get_block('latest'))['timestamp'])
            )
            
            logger.info(f"Retrieved portfolio for {address}")
            return portfolio
            
        except Exception as e:
            logger.error(f"Error getting account portfolio: {e}")
            raise

    # ==================== Account Updates ====================

    async def update_account_balance(self, account: EVMAccount) -> EVMAccount:
        """
        Update account with current on-chain balance and nonce.
        
        Args:
            account: EVMAccount to update
            
        Returns:
            Updated EVMAccount
        """
        try:
            # Get current balance and nonce
            address_checksum = Web3.to_checksum_address(account.address)
            balance_wei = await self.w3.eth.get_balance(address_checksum)
            balance_eth = _wei_to_eth(balance_wei)
            nonce = await self.w3.eth.get_transaction_count(address_checksum)
            
            # Update account
            account.balance = balance_eth
            account.nonce = nonce
            
            logger.info(f"Updated account {account.address}: balance={balance_eth} ETH, nonce={nonce}")
            return account
            
        except Exception as e:
            logger.error(f"Error updating account balance: {e}")
            raise

    async def get_transaction_count(self, address: str) -> int:
        """
        Get current nonce (transaction count) for an address.
        
        Args:
            address: Ethereum address
            
        Returns:
            Current nonce
        """
        try:
            address = _validate_address(address)
            address_checksum = Web3.to_checksum_address(address)
            nonce = await self.w3.eth.get_transaction_count(address_checksum)
            logger.info(f"Transaction count for {address}: {nonce}")
            return nonce
        except Exception as e:
            logger.error(f"Error getting transaction count: {e}")
            raise

    # ==================== Utility Methods ====================

    def validate_private_key(self, private_key: str) -> bool:
        """
        Validate private key format and derive address.
        
        Args:
            private_key: Private key to validate
            
        Returns:
            True if valid
        """
        try:
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            Account.from_key(private_key)
            return True
        except Exception:
            return False

    def get_address_from_private_key(self, private_key: str) -> str:
        """
        Get Ethereum address from private key.
        
        Args:
            private_key: Private key
            
        Returns:
            Ethereum address
        """
        try:
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            account = Account.from_key(private_key)
            return account.address
        except Exception as e:
            logger.error(f"Error deriving address from private key: {e}")
            raise

    async def is_contract_address(self, address: str) -> bool:
        """
        Check if an address is a contract.
        
        Args:
            address: Ethereum address to check
            
        Returns:
            True if address is a contract
        """
        try:
            address = _validate_address(address)
            address_checksum = Web3.to_checksum_address(address)
            code = await self.w3.eth.get_code(address_checksum)
            return len(code) > 0
        except Exception as e:
            logger.error(f"Error checking if address is contract: {e}")
            return False