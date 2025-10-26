from typing import List
from pydantic import BaseModel, Field

class AmountOutRequest(BaseModel):
    """Request model for getting amount out."""
    amount_in: int = Field(..., description="Input amount in wei")
    reserve_in: int = Field(..., description="Reserve of input token")
    reserve_out: int = Field(..., description="Reserve of output token")


class AmountOutResponse(BaseModel):
    """Response model for amount out."""
    amount_out: int = Field(..., description="Output amount in wei")


class AmountsOutRequest(BaseModel):
    """Request model for getting amounts out for a path."""
    amount_in: int = Field(..., description="Input amount in wei")
    path: List[str] = Field(..., description="Token addresses in swap path")


class AmountsOutResponse(BaseModel):
    """Response model for amounts out."""
    amounts: List[int] = Field(..., description="Amounts for each step in path")


class QuoteRequest(BaseModel):
    """Request model for getting a quote."""
    amount_a: int = Field(..., description="Amount of token A")
    reserve_a: int = Field(..., description="Reserve of token A")
    reserve_b: int = Field(..., description="Reserve of token B")


class QuoteResponse(BaseModel):
    """Response model for quote."""
    amount_b: int = Field(..., description="Quoted amount of token B")


class SwapRequest(BaseModel):
    """Request model for swap operations."""
    amount_in: int = Field(..., description="Input amount in wei")
    amount_out_min: int = Field(..., description="Minimum output amount")
    path: List[str] = Field(..., description="Token addresses in swap path")
    to: str = Field(..., description="Recipient address")
    deadline: int = Field(..., description="Transaction deadline (unix timestamp)")
    from_address: str = Field(..., description="Sender address")
    private_key: str = Field(..., description="Private key for signing")


class SwapResponse(BaseModel):
    """Response model for swap operations."""
    transaction_hash: str = Field(..., description="Transaction hash")
    status: int = Field(..., description="Transaction status (1=success)")
    gas_used: int = Field(..., description="Gas used in transaction")