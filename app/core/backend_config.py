from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    """Application settings."""
    
    # Blockchain Configuration
    RPC_URL: str = "https://rpc.ankr.com/somnia_testnet"
    CHAIN_ID: int = 50312
    
    # Contract Addresses
    ROUTER_ADDRESS: str = "0xb98c15a0dC1e271132e341250703c7e94c059e8D"

    # Account Addresses
    PRIVATE_KEY: str = "0x0000000000000000000000000000000000000000000000000000000000000001"
    ADDRESS: str = "0x7e5f4552091a69125d5dfcb7b8c2659029395bdf"

    # Tokens
    WSTT: str = "0xF22eF0085f6511f70b01a68F360dCc56261F768a"
    SUSDT: str = "0x65296738D4E5edB1515e40287B6FDf8320E6eE04"
    WSTT_ID: str = 'somnia'
    SUSDT_ID: str = 'tether'

    # Coingecko
    COINGECKO_API_KEY: str = ''

    # AI
    GEMINI_API_KEY: str = ''

    # Database
    MONGODB_URL: str = 'mongodb://localhost:27017'
    DATABASE_NAME: str = 'autosomnia'

    # Server Configuration
    HOST: str = '127.0.0.1'
    PORT: int = 8000
    ENVIRONMENT: str = 'development'

    # Other configurations
    GAS_LIMIT: int = 300000
    LOG_LEVEL: str = 'INFO'

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / '.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'  # Allow extra fields in .env without errors
    )


settings = Settings()