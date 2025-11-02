from fastapi import APIRouter, HTTPException, Depends, Query, Request
from web3 import AsyncWeb3
from app.models.exchange_models import *
from app.core.backend_config import settings
from app.services.somnia_exchange_service import SomniaExchangeService

router = APIRouter(prefix="/exchange", tags=["exchange"])

# ==================== Dependency ====================

async def get_exchange_service(request: Request) -> SomniaExchangeService:
    """Get SomniaExchangeService instance using shared Web3 connection."""
    try:
        # Use the shared Web3 instance from app state
        if not hasattr(request.app, 'web3_instance') or request.app.web3_instance is None:
            # Fallback to creating new instance if shared one is not available
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.RPC_URL))
        else:
            w3 = request.app.web3_instance
        
        return SomniaExchangeService(w3, settings.ROUTER_ADDRESS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize exchange service: {str(e)}")


# ==================== View Functions ====================

@router.get("/weth-address")
async def get_weth_address(
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Get WETH token address."""
    try:
        weth = await service.get_weth_address()
        return {"weth_address": weth}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting WETH address: {str(e)}")


@router.get("/factory-address")
async def get_factory_address(
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Get factory contract address."""
    try:
        factory = await service.get_factory_address()
        return {"factory_address": factory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting factory address: {str(e)}")


@router.post("/amount-out", response_model=AmountOutResponse)
async def get_amount_out(
    amount_request: AmountOutRequest,
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Calculate output amount for given input amount."""
    try:
        amount_out = await service.get_amount_out(
            amount_request.amount_in,
            amount_request.reserve_in,
            amount_request.reserve_out
        )
        return AmountOutResponse(amount_out=amount_out)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating amount out: {str(e)}")


@router.post("/amounts-out", response_model=AmountsOutResponse)
async def get_amounts_out(
    amounts_request: AmountsOutRequest,
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Get output amounts for a swap path."""
    try:
        amounts = await service.get_amounts_out(amounts_request.amount_in, amounts_request.path)
        return AmountsOutResponse(amounts=amounts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting amounts out: {str(e)}")


@router.post("/quote", response_model=QuoteResponse)
async def get_quote(
    quote_request: QuoteRequest,
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Get quote for token pair."""
    try:
        quote = await service.quote(quote_request.amount_a, quote_request.reserve_a, quote_request.reserve_b)
        return QuoteResponse(amount_b=quote)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting quote: {str(e)}")


# ==================== Swap Functions ====================

@router.post("/swap-exact-tokens-for-tokens", response_model=SwapResponse)
async def swap_exact_tokens_for_tokens(
    swap_request: SwapRequest,
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Swap exact tokens for tokens."""
    try:
        receipt = await service.swap_exact_tokens_for_tokens(
            amount_in=swap_request.amount_in,
            amount_out_min=swap_request.amount_out_min,
            path=swap_request.path,
            to=swap_request.to,
            deadline=swap_request.deadline,
            from_address=swap_request.from_address,
            private_key=swap_request.private_key
        )
        return SwapResponse(
            transaction_hash=receipt['transactionHash'].hex(),
            status=receipt['status'],
            gas_used=receipt['gasUsed']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error swapping tokens: {str(e)}")


@router.post("/swap-exact-eth-for-tokens", response_model=SwapResponse)
async def swap_exact_eth_for_tokens(
    swap_request: SwapRequest,
    eth_value: int = Query(..., description="ETH value to send in wei"),
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Swap exact ETH for tokens."""
    try:
        receipt = await service.swap_exact_eth_for_tokens(
            amount_out_min=swap_request.amount_out_min,
            path=swap_request.path,
            to=swap_request.to,
            deadline=swap_request.deadline,
            from_address=swap_request.from_address,
            private_key=swap_request.private_key,
            eth_value=eth_value
        )
        return SwapResponse(
            transaction_hash=receipt['transactionHash'].hex(),
            status=receipt['status'],
            gas_used=receipt['gasUsed']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error swapping ETH for tokens: {str(e)}")


@router.post("/swap-exact-tokens-for-eth", response_model=SwapResponse)
async def swap_exact_tokens_for_eth(
    swap_request: SwapRequest,
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Swap exact tokens for ETH."""
    try:
        receipt = await service.swap_exact_tokens_for_eth(
            amount_in=swap_request.amount_in,
            amount_out_min=swap_request.amount_out_min,
            path=swap_request.path,
            to=swap_request.to,
            deadline=swap_request.deadline,
            from_address=swap_request.from_address,
            private_key=swap_request.private_key
        )
        return SwapResponse(
            transaction_hash=receipt['transactionHash'].hex(),
            status=receipt['status'],
            gas_used=receipt['gasUsed']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error swapping tokens for ETH: {str(e)}")


# ==================== Token Approval Functions ====================

@router.post("/approve-token", response_model=ApprovalResponse)
async def approve_token(
    approval_request: ApprovalRequest,
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Approve a spender to spend tokens on behalf of the owner."""
    try:
        receipt = await service.approve_token(
            token_address=approval_request.token_address,
            spender_address=approval_request.spender_address,
            amount=approval_request.amount,
            from_address=approval_request.from_address,
            private_key=approval_request.private_key
        )
        return ApprovalResponse(
            transaction_hash=receipt['transactionHash'].hex(),
            status=receipt['status'],
            gas_used=receipt['gasUsed'],
            token_address=approval_request.token_address,
            spender_address=approval_request.spender_address,
            amount=approval_request.amount
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving token: {str(e)}")


@router.post("/approve-router", response_model=ApprovalResponse)
async def approve_router_for_token(
    token_address: str = Query(..., description="ERC-20 token contract address"),
    amount: int = Query(..., description="Amount to approve in wei/smallest unit"),
    from_address: str = Query(..., description="Token owner address"),
    private_key: str = Query(..., description="Private key for signing"),
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Approve the router contract to spend tokens (convenience endpoint)."""
    try:
        receipt = await service.approve_router_for_token(
            token_address=token_address,
            amount=amount,
            from_address=from_address,
            private_key=private_key
        )
        return ApprovalResponse(
            transaction_hash=receipt['transactionHash'].hex(),
            status=receipt['status'],
            gas_used=receipt['gasUsed'],
            token_address=token_address,
            spender_address=service.contract_address,  # Router address
            amount=amount
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving router for token: {str(e)}")
