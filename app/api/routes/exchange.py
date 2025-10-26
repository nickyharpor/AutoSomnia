from fastapi import APIRouter, HTTPException, Depends, Query
from web3 import AsyncWeb3
from app.models.exchange_models import *
from app.core.backend_config import settings
from app.services.somnia_exchange_service import SomniaExchangeService

router = APIRouter(prefix="/exchange", tags=["exchange"])

# ==================== Dependency ====================

async def get_exchange_service() -> SomniaExchangeService:
    """Get SomniaExchangeService instance."""
    try:
        w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.RPC_URL))
        return SomniaExchangeService(w3, settings.ROUTER_ADDRESS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize exchange service: {str(e)}")


# ==================== View Functions ====================

@router.get("/weth-address")
async def get_weth_address(service: SomniaExchangeService = Depends(get_exchange_service)):
    """Get WETH token address."""
    try:
        weth = await service.get_weth_address()
        return {"weth_address": weth}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting WETH address: {str(e)}")


@router.get("/factory-address")
async def get_factory_address(service: SomniaExchangeService = Depends(get_exchange_service)):
    """Get factory contract address."""
    try:
        factory = await service.get_factory_address()
        return {"factory_address": factory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting factory address: {str(e)}")


@router.post("/amount-out", response_model=AmountOutResponse)
async def get_amount_out(
    request: AmountOutRequest,
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Calculate output amount for given input amount."""
    try:
        amount_out = await service.get_amount_out(
            request.amount_in,
            request.reserve_in,
            request.reserve_out
        )
        return AmountOutResponse(amount_out=amount_out)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating amount out: {str(e)}")


@router.post("/amounts-out", response_model=AmountsOutResponse)
async def get_amounts_out(
    request: AmountsOutRequest,
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Get output amounts for a swap path."""
    try:
        amounts = await service.get_amounts_out(request.amount_in, request.path)
        return AmountsOutResponse(amounts=amounts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting amounts out: {str(e)}")


@router.post("/quote", response_model=QuoteResponse)
async def get_quote(
    request: QuoteRequest,
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Get quote for token pair."""
    try:
        quote = await service.quote(request.amount_a, request.reserve_a, request.reserve_b)
        return QuoteResponse(amount_b=quote)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting quote: {str(e)}")


# ==================== Swap Functions ====================

@router.post("/swap-exact-tokens-for-tokens", response_model=SwapResponse)
async def swap_exact_tokens_for_tokens(
    request: SwapRequest,
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Swap exact tokens for tokens."""
    try:
        receipt = await service.swap_exact_tokens_for_tokens(
            amount_in=request.amount_in,
            amount_out_min=request.amount_out_min,
            path=request.path,
            to=request.to,
            deadline=request.deadline,
            from_address=request.from_address,
            private_key=request.private_key
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
    request: SwapRequest,
    eth_value: int = Query(..., description="ETH value to send in wei"),
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Swap exact ETH for tokens."""
    try:
        receipt = await service.swap_exact_eth_for_tokens(
            amount_out_min=request.amount_out_min,
            path=request.path,
            to=request.to,
            deadline=request.deadline,
            from_address=request.from_address,
            private_key=request.private_key,
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
    request: SwapRequest,
    service: SomniaExchangeService = Depends(get_exchange_service)
):
    """Swap exact tokens for ETH."""
    try:
        receipt = await service.swap_exact_tokens_for_eth(
            amount_in=request.amount_in,
            amount_out_min=request.amount_out_min,
            path=request.path,
            to=request.to,
            deadline=request.deadline,
            from_address=request.from_address,
            private_key=request.private_key
        )
        return SwapResponse(
            transaction_hash=receipt['transactionHash'].hex(),
            status=receipt['status'],
            gas_used=receipt['gasUsed']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error swapping tokens for ETH: {str(e)}")
