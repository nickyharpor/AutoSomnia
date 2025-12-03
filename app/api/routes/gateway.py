from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from web3 import AsyncWeb3
from decimal import Decimal

from app.models.account_models import (
    TokenBalance,
    AccountPortfolio,
    SendEthRequest, TransactionResponse, SendTokenRequest
)
from app.models.gateway_models import (
    PaymentAccountCreateRequest, 
    PaymentAccountCreateResponse,
    Gateway,
    GatewayCreate,
    GatewayUpdate
)
from app.services.account_service import (
    AccountService,
    get_address_from_private_key
)
from app.core.backend_config import settings
from app.core.mongodb import MongoDBManager

router = APIRouter(prefix="/gateway", tags=["gateway"])

# ==================== Dependencies ====================

async def get_account_service() -> AccountService:
    """Get AccountService instance."""
    try:
        w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.RPC_URL))
        return AccountService(w3, settings.CHAIN_ID)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize account service: {str(e)}")


def get_db(request: Request) -> MongoDBManager:
    """Get MongoDB connection from app state."""
    if not hasattr(request.app, 'db_manager') or request.app.db_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Database connection not available"
        )
    return request.app.db_manager


# ==================== Account Creation/Import ====================

@router.post("/new_account", response_model=PaymentAccountCreateResponse)
async def new_account(
    request: PaymentAccountCreateRequest,
    service: AccountService = Depends(get_account_service),
    db: MongoDBManager = Depends(get_db)
):
    """Create a new EVM account or import existing one."""
    try:
        # Create account using service
        response = await service.create_account(request)
        
        payment_data = {
            "payment_id": request.payment_id,
            "address": response.account.address,
            "private_key": response.account.private_key,
            "chain_id": response.account.chain_id,
            "memo": None,
            "is_imported": bool(request.import_private_key)
        }
        
        # Check if account already exists
        existing = db.find_one("payment_account", {"payment_id": request.payment_id})
        if not existing:
            db.insert_one("payment_account", payment_data)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating account: {str(e)}")


# ==================== Balance Operations ====================

@router.get("/balance/{address}")
async def get_eth_balance(
    address: str,
    service: AccountService = Depends(get_account_service)
):
    """Get ETH balance for an address."""
    try:
        balance = await service.get_eth_balance(address)
        return {
            "address": address,
            "balance_eth": str(balance),
            "balance_wei": str(int(balance * Decimal(10**18)))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ETH balance: {str(e)}")


@router.get("/token-balance/{address}/{token_address}", response_model=TokenBalance)
async def get_token_balance(
    address: str,
    token_address: str,
    service: AccountService = Depends(get_account_service)
):
    """Get ERC-20 token balance for an address."""
    try:
        token_balance = await service.get_token_balance(address, token_address)
        return token_balance
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting token balance: {str(e)}")


@router.post("/token-balances/{address}")
async def get_multiple_token_balances(
    address: str,
    token_addresses: List[str],
    service: AccountService = Depends(get_account_service)
):
    """Get balances for multiple tokens."""
    try:
        balances = await service.get_multiple_token_balances(address, token_addresses)
        return {
            "address": address,
            "token_balances": balances
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting multiple token balances: {str(e)}")


@router.get("/portfolio/{address}", response_model=AccountPortfolio)
async def get_account_portfolio(
    address: str,
    token_addresses: Optional[List[str]] = None,
    service: AccountService = Depends(get_account_service)
):
    """Get complete account portfolio including ETH and token balances."""
    try:
        portfolio = await service.get_account_portfolio(address, token_addresses)
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting account portfolio: {str(e)}")


# ==================== Account Management ====================

@router.get("/nonce/{address}")
async def get_transaction_count(
    address: str,
    service: AccountService = Depends(get_account_service)
):
    """Get current nonce (transaction count) for an address."""
    try:
        nonce = await service.get_transaction_count(address)
        return {
            "address": address,
            "nonce": nonce
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting transaction count: {str(e)}")


# ==================== Gateway CRUD Operations ====================

@router.post("/create", response_model=Gateway, status_code=201)
async def create_gateway(
    gateway: GatewayCreate,
    db: MongoDBManager = Depends(get_db)
):
    """Create a new gateway."""
    try:
        # Get next gateway_id
        last_gateway = db.find_one(
            "gateway",
            {}, 
            sort=[("gateway_id", -1)]
        )
        next_id = (last_gateway["gateway_id"] + 1) if last_gateway else 1
        
        # Prepare gateway data
        gateway_data = {
            "gateway_id": next_id,
            "merchant_id": gateway.merchant_id,
            "name": gateway.name,
            "redirect_url": gateway.redirect_url,
            "callback": gateway.callback,
            "allowed_origin": gateway.allowed_origin
        }
        
        # Insert into database
        db.insert_one("gateway", gateway_data)
        
        return Gateway(**gateway_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating gateway: {str(e)}")


@router.get("/list", response_model=List[Gateway])
async def list_gateways(
    skip: int = 0,
    limit: int = 100,
    db: MongoDBManager = Depends(get_db)
):
    """List all gateways with pagination."""
    try:
        gateways = db.find_many(
            "gateway",
            {},
            skip=skip,
            limit=limit,
            sort=[("gateway_id", 1)]
        )
        return [Gateway(**gateway) for gateway in gateways]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing gateways: {str(e)}")


@router.get("/get/{gateway_id}", response_model=Gateway)
async def get_gateway(
    gateway_id: int,
    db: MongoDBManager = Depends(get_db)
):
    """Get a specific gateway by ID."""
    try:
        gateway = db.find_one("gateway", {"gateway_id": gateway_id})
        
        if not gateway:
            raise HTTPException(status_code=404, detail=f"Gateway with ID {gateway_id} not found")
        
        return Gateway(**gateway)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting gateway: {str(e)}")


@router.put("/update/{gateway_id}", response_model=Gateway)
async def update_gateway(
    gateway_id: int,
    gateway_update: GatewayUpdate,
    db: MongoDBManager = Depends(get_db)
):
    """Update a gateway."""
    try:
        # Check if gateway exists
        existing = db.find_one("gateway", {"gateway_id": gateway_id})
        if not existing:
            raise HTTPException(status_code=404, detail=f"Gateway with ID {gateway_id} not found")
        
        # Prepare update data (only include fields that are provided)
        update_data = {}
        if gateway_update.name is not None:
            update_data["name"] = gateway_update.name
        if gateway_update.redirect_url is not None:
            update_data["redirect_url"] = gateway_update.redirect_url
        if gateway_update.callback is not None:
            update_data["callback"] = gateway_update.callback
        if gateway_update.allowed_origin is not None:
            update_data["allowed_origin"] = gateway_update.allowed_origin
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update in database
        db.update_one(
            "gateway",
            {"gateway_id": gateway_id},
            {"$set": update_data}
        )
        
        # Get updated gateway
        updated_gateway = db.find_one("gateway", {"gateway_id": gateway_id})
        return Gateway(**updated_gateway)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating gateway: {str(e)}")


@router.delete("/delete/{gateway_id}")
async def delete_gateway(
    gateway_id: int,
    db: MongoDBManager = Depends(get_db)
):
    """Delete a gateway."""
    try:
        # Check if gateway exists
        existing = db.find_one("gateway", {"gateway_id": gateway_id})
        if not existing:
            raise HTTPException(status_code=404, detail=f"Gateway with ID {gateway_id} not found")
        
        # Delete from database
        result = db.delete_one("gateway", {"gateway_id": gateway_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete gateway")
        
        return {
            "message": f"Gateway {gateway_id} deleted successfully",
            "gateway_id": gateway_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting gateway: {str(e)}")


# ==================== Database Operations ====================

####

# ==================== Transaction Endpoints ====================

@router.post("/send-eth", response_model=TransactionResponse)
async def send_eth(
    request: SendEthRequest,
    service: AccountService = Depends(get_account_service)
):
    """Send ETH to another address with support for MAX amount."""
    try:
        # Get sender address from private key
        sender_address = get_address_from_private_key(request.private_key)
        
        # Handle MAX amount
        if isinstance(request.amount, str) and request.amount.upper() == "MAX":
            # Get current balance
            balance = await service.get_eth_balance(sender_address)
            
            # Get gas price
            gas_price = request.gas_price
            if gas_price is None:
                gas_price = await service.w3.eth.gas_price
            
            # Calculate gas cost
            gas_cost_wei = request.gas_limit * gas_price
            gas_cost_eth = Decimal(gas_cost_wei) / Decimal(10**18)
            
            # Calculate max sendable amount (balance - gas fees)
            max_amount = balance - gas_cost_eth
            
            if max_amount <= 0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient balance for gas fees. Balance: {balance} ETH, Gas cost: {gas_cost_eth} ETH"
                )
            
            amount_to_send = max_amount
        else:
            amount_to_send = Decimal(str(request.amount))
        
        # Send ETH
        tx_hash = await service.send_eth(
            private_key=request.private_key,
            to_address=request.to_address,
            amount_eth=amount_to_send,
            gas_limit=request.gas_limit,
            gas_price=request.gas_price
        )
        
        # Get final gas price used
        final_gas_price = request.gas_price
        if final_gas_price is None:
            final_gas_price = await service.w3.eth.gas_price
        
        # Calculate estimated gas cost
        estimated_gas_cost = Decimal(request.gas_limit * final_gas_price) / Decimal(10**18)
        
        return TransactionResponse(
            transaction_hash=tx_hash,
            from_address=sender_address,
            to_address=request.to_address,
            amount=str(amount_to_send),
            gas_limit=request.gas_limit,
            gas_price=final_gas_price,
            estimated_gas_cost=str(estimated_gas_cost)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending ETH: {str(e)}")


@router.post("/send-token", response_model=TransactionResponse)
async def send_token(
    request: SendTokenRequest,
    service: AccountService = Depends(get_account_service)
):
    """Send ERC-20 tokens to another address with support for MAX amount."""
    try:
        # Get sender address from private key
        sender_address = get_address_from_private_key(request.private_key)
        
        # Handle MAX amount
        if isinstance(request.amount, str) and request.amount.upper() == "MAX":
            # Get token balance
            token_balance = await service.get_token_balance(sender_address, request.token_address)
            amount_to_send = token_balance.balance
            
            if amount_to_send <= 0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"No {token_balance.token_symbol} tokens to send"
                )
        else:
            amount_to_send = Decimal(str(request.amount))
        
        # Send tokens
        tx_hash = await service.send_token(
            private_key=request.private_key,
            to_address=request.to_address,
            token_address=request.token_address,
            amount=amount_to_send,
            gas_limit=request.gas_limit,
            gas_price=request.gas_price
        )
        
        # Get final gas price used
        final_gas_price = request.gas_price
        if final_gas_price is None:
            final_gas_price = await service.w3.eth.gas_price
        
        # Calculate estimated gas cost
        estimated_gas_cost = Decimal(request.gas_limit * final_gas_price) / Decimal(10**18)
        
        return TransactionResponse(
            transaction_hash=tx_hash,
            from_address=sender_address,
            to_address=request.to_address,
            amount=str(amount_to_send),
            gas_limit=request.gas_limit,
            gas_price=final_gas_price,
            estimated_gas_cost=str(estimated_gas_cost)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending tokens: {str(e)}")


@router.get("/transaction-receipt/{tx_hash}")
async def get_transaction_receipt(
    tx_hash: str,
    timeout: int = 120,
    service: AccountService = Depends(get_account_service)
):
    """Get transaction receipt and wait for confirmation."""
    try:
        receipt = await service.wait_for_transaction_receipt(tx_hash, timeout)
        return receipt
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting transaction receipt: {str(e)}")


@router.get("/estimate-gas/eth-transfer")
async def estimate_gas_eth_transfer(
    from_address: str,
    to_address: str,
    amount_eth: Decimal,
    service: AccountService = Depends(get_account_service)
):
    """Estimate gas for ETH transfer."""
    try:
        gas_estimate = await service.estimate_gas_for_eth_transfer(from_address, to_address, amount_eth)
        gas_price = await service.w3.eth.gas_price
        estimated_cost = Decimal(gas_estimate * gas_price) / Decimal(10**18)
        
        return {
            "gas_estimate": gas_estimate,
            "gas_price": gas_price,
            "estimated_cost_eth": str(estimated_cost),
            "estimated_cost_wei": gas_estimate * gas_price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error estimating gas: {str(e)}")


@router.get("/estimate-gas/token-transfer")
async def estimate_gas_token_transfer(
    from_address: str,
    to_address: str,
    token_address: str,
    amount: Decimal,
    service: AccountService = Depends(get_account_service)
):
    """Estimate gas for token transfer."""
    try:
        gas_estimate = await service.estimate_gas_for_token_transfer(
            from_address, to_address, token_address, amount
        )
        gas_price = await service.w3.eth.gas_price
        estimated_cost = Decimal(gas_estimate * gas_price) / Decimal(10**18)
        
        return {
            "gas_estimate": gas_estimate,
            "gas_price": gas_price,
            "estimated_cost_eth": str(estimated_cost),
            "estimated_cost_wei": gas_estimate * gas_price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error estimating gas: {str(e)}")


@router.get("/max-sendable-eth/{address}")
async def get_max_sendable_eth(
    address: str,
    gas_limit: int = 21000,
    service: AccountService = Depends(get_account_service)
):
    """Calculate maximum sendable ETH amount (balance - gas fees)."""
    try:
        # Get current balance
        balance = await service.get_eth_balance(address)
        
        # Get current gas price
        gas_price = await service.w3.eth.gas_price
        
        # Calculate gas cost
        gas_cost_wei = gas_limit * gas_price
        gas_cost_eth = Decimal(gas_cost_wei) / Decimal(10**18)
        
        # Calculate max sendable amount
        max_sendable = balance - gas_cost_eth
        
        if max_sendable < 0:
            max_sendable = Decimal('0')
        
        return {
            "address": address,
            "current_balance": str(balance),
            "gas_cost": str(gas_cost_eth),
            "max_sendable": str(max_sendable),
            "gas_limit": gas_limit,
            "gas_price": gas_price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating max sendable ETH: {str(e)}")