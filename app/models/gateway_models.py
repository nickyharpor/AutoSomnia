from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict, field_serializer
from decimal import Decimal
import re


# ==================== Gateway Models ====================

class GatewayBase(BaseModel):
    """Base model for Gateway."""
    name: str = Field(..., description="Gateway name (mandatory)")
    merchant_id: int = Field(..., description="Merchant ID")
    redirect_url: Optional[str] = Field(None, description="Redirect URL after payment")
    callback: Optional[str] = Field(None, description="Callback URL for notifications")
    allowed_origin: Optional[str] = Field(None, description="Allowed CORS origin")


class GatewayCreate(GatewayBase):
    """Request model for creating a gateway."""
    pass


class GatewayUpdate(BaseModel):
    """Request model for updating a gateway."""
    name: Optional[str] = Field(None, description="Gateway name")
    redirect_url: Optional[str] = Field(None, description="Redirect URL after payment")
    callback: Optional[str] = Field(None, description="Callback URL for notifications")
    allowed_origin: Optional[str] = Field(None, description="Allowed CORS origin")


class Gateway(GatewayBase):
    """Response model for Gateway."""
    gateway_id: int = Field(..., description="Unique gateway ID")
    model_config = ConfigDict(from_attributes=True)


# ==================== Payment Account Models ====================

class PaymentAccount(BaseModel):
    """Model representing a Web3 EVM-compatible account."""

    address: str = Field(..., description="Payment address")
    private_key: str = Field(..., description="Private key for the account")
    balance: Decimal = Field(default=Decimal('0'), description="Account balance")
    nonce: int = Field(default=0, description="Current transaction nonce")
    chain_id: int = Field(..., description="Chain ID")
    memo: Optional[str] = Field(None, description="Optional memo")

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

    @field_serializer('balance')
    def serialize_balance(self, value: Decimal) -> str:
        """Serialize Decimal balance to string."""
        return str(value)

    model_config = ConfigDict()


class PaymentAccountCreateRequest(BaseModel):
    """Request model for creating a new account."""

    payment_id: int = Field(..., description="Payment ID")
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


class PaymentAccountCreateResponse(BaseModel):
    """Response model for account creation."""
    
    account: PaymentAccount = Field(..., description="The created account")
    mnemonic: Optional[str] = Field(
        None, 
        description="Mnemonic phrase (only if generated new account)"
    )

