import time
import asyncio
from app.core.backend_config import settings
from web3 import AsyncWeb3
from app.services.somnia_exchange_service import SomniaExchangeService


async def example_usage():
    """Example of how to use the SomniaExchangeService."""
    
    # Initialize Web3 connection
    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.RPC_URL))

    # Initialize service
    exchange_service = SomniaExchangeService(w3, settings.ROUTER_ADDRESS)
    
    # ==================== View Functions ====================
    
    # Get WETH address
    weth_address = await exchange_service.get_weth_address()
    print(f"WETH Address: {weth_address}")
    
    # Get factory address
    factory_address = await exchange_service.get_factory_address()
    print(f"Factory Address: {factory_address}")
    
    # Get amount out
    amount_in = 1000000000000000000  # 1 token (18 decimals)
    reserve_in = 1000000000000000000
    reserve_out = 1000000000000000000
    amount_out = await exchange_service.get_amount_out(amount_in, reserve_in, reserve_out)
    print(f"Amount Out: {amount_out}")
    
    # Get amounts out for a swap path (skip if tokens not configured)
    try:
        if hasattr(settings, 'WSTT') and hasattr(settings, 'SUSDT'):
            path = [settings.WSTT, settings.SUSDT]  # Use simple 2-token path
            amounts = await exchange_service.get_amounts_out(amount_in, path)
            print(f"Amounts Out: {amounts}")
        else:
            print("Token addresses not configured, skipping amounts out test")
    except Exception as e:
        print(f"Amounts out failed (likely no liquidity): {e}")
    
    # Get quote
    quote = await exchange_service.quote(amount_in, reserve_in, reserve_out)
    print(f"Quote: {quote}")
    
    # ==================== Swap Functions ====================
    
    # Swap exact tokens for tokens (skip if not configured)
    if not (hasattr(settings, 'WSTT') and hasattr(settings, 'SUSDT') and hasattr(settings, 'ADDRESS') and hasattr(settings, 'PRIVATE_KEY')):
        print("Wallet settings not configured, skipping swap tests")
        return
        
    token_a = settings.WSTT
    token_b = settings.SUSDT
    amount_in = 1000000000000000000
    amount_out_min = 900000000000000000
    path = [token_a, token_b]
    to = settings.ADDRESS
    deadline = int(time.time()) + 3600  # 1 hour from now
    from_address = settings.ADDRESS
    private_key = settings.PRIVATE_KEY
    
    receipt = await exchange_service.swap_exact_tokens_for_tokens(
        amount_in=amount_in,
        amount_out_min=amount_out_min,
        path=path,
        to=to,
        deadline=deadline,
        from_address=from_address,
        private_key=private_key
    )
    print(f"Swap Transaction: {receipt['transactionHash'].hex()}")
    
    # Swap exact ETH for tokens
    eth_value = 1000000000000000000  # 1 ETH
    path = [weth_address, token_b]
    
    receipt = await exchange_service.swap_exact_eth_for_tokens(
        amount_out_min=amount_out_min,
        path=path,
        to=to,
        deadline=deadline,
        from_address=from_address,
        private_key=private_key,
        eth_value=eth_value
    )
    print(f"Swap ETH for Tokens Transaction: {receipt['transactionHash'].hex()}")
    
    # Swap exact tokens for ETH
    receipt = await exchange_service.swap_exact_tokens_for_eth(
        amount_in=amount_in,
        amount_out_min=amount_out_min,
        path=path,
        to=to,
        deadline=deadline,
        from_address=from_address,
        private_key=private_key
    )
    print(f"Swap Tokens for ETH Transaction: {receipt['transactionHash'].hex()}")
    
    # ==================== Liquidity Functions ====================
    
    # Add liquidity
    amount_a_desired = 1000000000000000000
    amount_b_desired = 1000000000000000000
    amount_a_min = 900000000000000000
    amount_b_min = 900000000000000000
    
    receipt = await exchange_service.add_liquidity(
        token_a=token_a,
        token_b=token_b,
        amount_a_desired=amount_a_desired,
        amount_b_desired=amount_b_desired,
        amount_a_min=amount_a_min,
        amount_b_min=amount_b_min,
        to=to,
        deadline=deadline,
        from_address=from_address,
        private_key=private_key
    )
    print(f"Add Liquidity Transaction: {receipt['transactionHash'].hex()}")
    
    # Remove liquidity
    liquidity = 1000000000000000000
    
    receipt = await exchange_service.remove_liquidity(
        token_a=token_a,
        token_b=token_b,
        liquidity=liquidity,
        amount_a_min=amount_a_min,
        amount_b_min=amount_b_min,
        to=to,
        deadline=deadline,
        from_address=from_address,
        private_key=private_key
    )
    print(f"Remove Liquidity Transaction: {receipt['transactionHash'].hex()}")


if __name__ == "__main__":
    asyncio.run(example_usage())
    print("Application finished.")
