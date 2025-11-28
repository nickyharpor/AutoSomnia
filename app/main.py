import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.backend_config import settings
from app.core.mongodb import MongoDBManager
from app.api.routes import account, exchange, user, auth, gateway

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(fast_api: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting FastAPI application...")
    
    try:
        # Initialize database connection and store in app state
        fast_api.db_manager = MongoDBManager(settings.MONGODB_URL, settings.DATABASE_NAME)
        fast_api.db_manager.connect()
        
        # Initialize AsyncWeb3 instance for exchange operations
        from web3 import AsyncWeb3
        fast_api.web3_instance = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(settings.RPC_URL))
        
        # Test Web3 connection
        try:
            is_connected = await fast_api.web3_instance.is_connected()
            if is_connected:
                latest_block = await fast_api.web3_instance.eth.get_block('latest')
                logger.info(f"Web3 connected successfully, latest block: {latest_block['number']}")
            else:
                logger.warning("Web3 connection test failed")
        except Exception as e:
            logger.warning(f"Web3 connection test error: {e}")
        
        # Create indexes for better performance
        try:
            # Account indexes
            fast_api.db_manager.create_index("accounts", "address", unique=True)
            fast_api.db_manager.create_index("accounts", "chain_id")
            fast_api.db_manager.create_index("accounts", "created_at")
            
            # User indexes
            fast_api.db_manager.create_index("users", "user_id", unique=True)
            fast_api.db_manager.create_index("users", "auto_exchange")
            fast_api.db_manager.create_index("users", "created_at")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Index creation failed (may already exist): {e}")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    
    try:
        # Close Web3 provider session
        if hasattr(fast_api, 'web3_instance') and fast_api.web3_instance is not None:
            try:
                # Close the aiohttp session if it exists
                if hasattr(fast_api.web3_instance.provider, '_session') and fast_api.web3_instance.provider._session:
                    await fast_api.web3_instance.provider._session.close()
                elif hasattr(fast_api.web3_instance.provider, 'session') and fast_api.web3_instance.provider.session:
                    await fast_api.web3_instance.provider.session.close()
                logger.info("Web3 provider session closed successfully")
            except Exception as e:
                logger.warning(f"Error closing Web3 provider session: {e}")
        
        # Close database connection
        if hasattr(fast_api, 'db_manager') and fast_api.db_manager is not None:
            fast_api.db_manager.disconnect()
        
        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Web3 Account Management API",
    description="API for managing EVM-compatible Web3 accounts and exchange operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health", response_model=None)
async def health_check(request: Request):
    """
    Health check endpoint for monitoring application status.
    """
    try:
        health_status = {
            "status": "healthy",
            "version": "1.0.0",
            "environment": getattr(settings, 'ENVIRONMENT', 'development'),
            "chain_id": settings.CHAIN_ID,
            "rpc_url": settings.RPC_URL
        }
        
        # Check database health if available
        if hasattr(request.app, 'db_manager') and request.app.db_manager is not None:
            try:
                db_health = request.app.db_manager.health_check()
                health_status["database"] = db_health
            except Exception as e:
                health_status["database"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "AutoSomnia API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": "/auth",
            "accounts": "/account",
            "exchange": "/exchange",
            "users": "/users"
        }
    }


# Include routers
app.include_router(auth.router)
app.include_router(account.router)
app.include_router(exchange.router)
app.include_router(user.router)
app.include_router(gateway.router)


# Dependency for database connection
def get_database(request: Request):
    """
    Dependency to get database connection from app state.
    This can be overridden in tests.
    """
    if not hasattr(request.app, 'db_manager') or request.app.db_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Database connection not available"
        )
    return request.app.db_manager


# Override the database dependency in account routes
account.get_db = get_database


if __name__ == "__main__":
    import uvicorn
    
    # Configuration for development
    uvicorn_config = {
        "host": settings.HOST,
        "port": settings.PORT,
        "reload": settings.ENVIRONMENT == 'development',
        "log_level": "info"
    }
    
    logger.info(f"Starting server on {uvicorn_config['host']}:{uvicorn_config['port']}")
    uvicorn.run("main:app", **uvicorn_config)