from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from web3 import AsyncWeb3
from decimal import Decimal

from app.models.account_models import (
    EVMAccount,
    TokenBalance,
    AccountPortfolio,
    AccountCreateRequest,
    AccountCreateResponse,
    BalanceUpdateRequest
)
from app.services.account_service import AccountService
from app.core.backend_config import settings
from app.core.mongodb import MongoDBManager

router = APIRouter(prefix="/account", tags=["account"])

# ==================== Dependencies ====================

async def get_account_service() -> AccountService:
    """Get AccountService instance."""
    try:
        w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.RPC_URL))
        return AccountService(w3, settings.CHAIN_ID)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize account service: {str(e)}")


def get_db() -> MongoDBManager:
    """Get MongoDB connection."""
    try:
        # You'll need to add MongoDB connection string to your settings
        # For now using a default local connection
        connection_string = getattr(settings, 'MONGODB_URL', 'mongodb://localhost:27017')
        database_name = getattr(settings, 'DATABASE_NAME', 'web3_accounts')
        
        db_manager = MongoDBManager(connection_string, database_name)
        return db_manager
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to database: {str(e)}")


# ==================== Account Creation/Import ====================

@router.post("/create", response_model=AccountCreateResponse)
async def create_account(
    request: AccountCreateRequest,
    service: AccountService = Depends(get_account_service),
    db: MongoDBManager = Depends(get_db)
):
    """Create a new EVM account or import existing one."""
    try:
        # Create account using service
        response = await service.create_account(request)
        
        account_data = {
            "user_id": request.user_id,
            "address": response.account.address,
            "private_key": response.account.private_key,
            "is_imported": bool(request.import_private_key)
        }
        
        # Check if account already exists
        existing = db.find_one("accounts", {"address": response.account.address})
        if not existing:
            db.insert_one("accounts", account_data)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating account: {str(e)}")


@router.post("/import-mnemonic", response_model=AccountCreateResponse)
async def import_account_from_mnemonic(
    user_id: int,
    mnemonic: str,
    chain_id: int = 1,
    service: AccountService = Depends(get_account_service),
    db: MongoDBManager = Depends(get_db)
):
    """Import account from mnemonic phrase."""
    try:
        # Import account using service
        response = await service.import_account_from_mnemonic(mnemonic, chain_id)
        
        # Store account in database
        account_data = {
            "user_id": user_id,
            "address": response.account.address,
            "private_key": response.account.private_key,
            "is_imported": True
        }
        
        # Check if account already exists
        existing = db.find_one("accounts", {"address": response.account.address})
        if not existing:
            db.insert_one("accounts", account_data)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing account from mnemonic: {str(e)}")


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


# ==================== Database Operations ====================

@router.get("/list")
async def list_accounts(
    limit: int = 50,
    skip: int = 0,
    db: MongoDBManager = Depends(get_db)
):
    """List all accounts stored in database."""
    try:
        accounts = db.find_many(
            "accounts",
            filter_dict={},
            sort=("created_at", -1),
            limit=limit,
            skip=skip
        )
        
        total_count = db.count_documents("accounts")
        
        return {
            "accounts": accounts,
            "total_count": total_count,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing accounts: {str(e)}")


@router.get("/details/{address}")
async def get_account_details(
    address: str,
    db: MongoDBManager = Depends(get_db)
):
    """Get account details from database."""
    try:
        account = db.find_one("accounts", {"address": address})
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return account
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting account details: {str(e)}")


@router.delete("/remove/{address}")
async def remove_account(
    address: str,
    db: MongoDBManager = Depends(get_db)
):
    """Remove account from database."""
    try:
        deleted_count = db.delete_one("accounts", {"address": address})
        
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return {
            "message": f"Account {address} removed successfully",
            "deleted_count": deleted_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing account: {str(e)}")


# ==================== Utility Endpoints ====================

@router.post("/validate-private-key")
async def validate_private_key(
    private_key: str,
    service: AccountService = Depends(get_account_service)
):
    """Validate private key format."""
    try:
        is_valid = service.validate_private_key(private_key)

        if is_valid:
            address_from_pk = service.get_address_from_private_key(private_key)
            result = {"is_valid": is_valid,
                      "address": address_from_pk}
        else:
            result = {"is_valid": is_valid}

        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating private key: {str(e)}")


@router.get("/is-contract/{address}")
async def is_contract_address(
    address: str,
    service: AccountService = Depends(get_account_service)
):
    """Check if an address is a contract."""
    try:
        is_contract = await service.is_contract_address(address)
        return {
            "address": address,
            "is_contract": is_contract
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking contract address: {str(e)}")


# ==================== Health Check ====================

@router.get("/health")
async def health_check(
    service: AccountService = Depends(get_account_service),
    db: MongoDBManager = Depends(get_db)
):
    """Health check for account service and database."""
    try:
        # Check Web3 connection
        w3_health = {"status": "unknown"}
        try:
            latest_block = await service.w3.eth.get_block('latest')
            w3_health = {
                "status": "healthy",
                "latest_block": latest_block['number'],
                "chain_id": service.chain_id
            }
        except Exception as e:
            w3_health = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check database connection
        db_health = db.health_check()
        
        return {
            "web3": w3_health,
            "database": db_health,
            "overall_status": "healthy" if w3_health["status"] == "healthy" and db_health["status"] == "healthy" else "unhealthy"
        }
        
    except Exception as e:
        return {
            "web3": {"status": "unknown"},
            "database": {"status": "unknown"},
            "overall_status": "unhealthy",
            "error": str(e)
        }