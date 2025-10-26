from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
import re


class EVMAccount(BaseModel):
    """Model representing a Web3 EVM-compatible account."""
    
    address: str = Field(..., description="Ethereum address (0x...)")
    private_key: str = Field(..., description="Private key for the account")
    balance: Decimal = Field(default=Decimal('0'), description="Account balance in ETH")
    nonce: int = Field(default=0, description="Current transaction nonce")
    chain_id: int = Field(default=1, description="Chain ID (1=Ethereum mainnet)")
    
    @field_validator('address')
    @classmethod
    def validate_address(cls, v):
        """Validate Ethereum address format."""
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError('Invalid Ethereum address format')
        return v.lower()
    
    @field_validator('private_key')
    @classmethod
    def validate_private_key(cls, v):
        """Validate private key format."""
        # Remove 0x prefix if present
        if v.startswith('0x'):
            v = v[2:]
        if not re.match(r'^[a-fA-F0-9]{64}$', v):
            raise ValueError('Invalid private key format')
        return v
    
    @field_validator('balance')
    @classmethod
    def validate_balance(cls, v):
        """Ensure balance is non-negative."""
        if v < 0:
            raise ValueError('Balance cannot be negative')
        return v
    
    @field_validator('nonce')
    @classmethod
    def validate_nonce(cls, v):
        """Ensure nonce is non-negative."""
        if v < 0:
            raise ValueError('Nonce cannot be negative')
        return v

    class Config:
        json_encoders = {
            Decimal: str
        }


class TokenBalance(BaseModel):
    """Model representing a token balance for an account."""
    
    token_address: str = Field(..., description="Token contract address")
    token_symbol: str = Field(..., description="Token symbol (e.g., USDC)")
    token_name: str = Field(..., description="Token name")
    balance: Decimal = Field(..., description="Token balance")
    decimals: int = Field(..., description="Token decimals")
    
    @field_validator('token_address')
    @classmethod
    def validate_token_address(cls, v):
        """Validate token address format."""
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError('Invalid token address format')
        return v.lower()
    
    @field_validator('balance')
    @classmethod
    def validate_balance(cls, v):
        """Ensure balance is non-negative."""
        if v < 0:
            raise ValueError('Token balance cannot be negative')
        return v
    
    @field_validator('decimals')
    @classmethod
    def validate_decimals(cls, v):
        """Ensure decimals is within valid range."""
        if v < 0 or v > 77:  # ERC20 standard allows up to 77 decimals
            raise ValueError('Token decimals must be between 0 and 77')
        return v

    class Config:
        json_encoders = {
            Decimal: str
        }


class AccountPortfolio(BaseModel):
    """Model representing an account's complete portfolio."""
    
    account: EVMAccount = Field(..., description="The EVM account")
    token_balances: Dict[str, TokenBalance] = Field(
        default_factory=dict, 
        description="Token balances keyed by token address"
    )
    total_value_usd: Optional[Decimal] = Field(
        None, 
        description="Total portfolio value in USD"
    )
    last_updated: Optional[int] = Field(
        None, 
        description="Last update timestamp (unix)"
    )
    
    class Config:
        json_encoders = {
            Decimal: str
        }


class AccountCreateRequest(BaseModel):
    """Request model for creating a new account."""

    user_id: int = Field(default=0, description="Telegram User ID")
    chain_id: int = Field(default=1, description="Chain ID for the account")
    import_private_key: Optional[str] = Field(
        None, 
        description="Private key to import (optional, generates new if not provided)"
    )
    
    @field_validator('import_private_key')
    @classmethod
    def validate_import_private_key(cls, v):
        """Validate imported private key format."""
        if v is None:
            return v
        # Remove 0x prefix if present
        if v.startswith('0x'):
            v = v[2:]
        if not re.match(r'^[a-fA-F0-9]{64}$', v):
            raise ValueError('Invalid private key format')
        return v


class AccountCreateResponse(BaseModel):
    """Response model for account creation."""
    
    account: EVMAccount = Field(..., description="The created account")
    mnemonic: Optional[str] = Field(
        None, 
        description="Mnemonic phrase (only if generated new account)"
    )


class BalanceUpdateRequest(BaseModel):
    """Request model for updating account balance."""
    
    address: str = Field(..., description="Account address")
    new_balance: Decimal = Field(..., description="New balance in ETH")
    
    @field_validator('address')
    @classmethod
    def validate_address(cls, v):
        """Validate Ethereum address format."""
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError('Invalid Ethereum address format')
        return v.lower()
    
    @field_validator('new_balance')
    @classmethod
    def validate_balance(cls, v):
        """Ensure balance is non-negative."""
        if v < 0:
            raise ValueError('Balance cannot be negative')
        return v

    class Config:
        json_encoders = {
            Decimal: str
        }