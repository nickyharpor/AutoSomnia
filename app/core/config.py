from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Blockchain RPC Configuration
    RPC_URL: str = "https://rpc.ankr.com/somnia_testnet"
    
    # Contract Addresses
    ROUTER_ADDRESS: str = "0xb98c15a0dC1e271132e341250703c7e94c059e8D"

    # Account Addresses
    PRIVATE_KEY: str = "0x0000000000000000000000000000000000000000000000000000000000000001"
    ADDRESS: str = "0x7e5f4552091a69125d5dfcb7b8c2659029395bdf"

    # Token Addresses
    WSTT: str = "0xF22eF0085f6511f70b01a68F360dCc56261F768a"
    SUSDT: str = "0x65296738D4E5edB1515e40287B6FDf8320E6eE04"
    PING: str = "0x33E7fAB0a8a5da1A923180989bD617c9c2D1C493"
    PONG: str = "0x9beaA0016c22B646Ac311Ab171270B0ECf23098F"
    NIA: str = "0xF2F773753cEbEFaF9b68b841d80C083b18C69311"

    # Other configurations
    GAS_LIMIT: int = 300000

    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()