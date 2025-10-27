from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Config(BaseSettings):
    API_ID: int = 0
    API_HASH: str = ''
    BOT_TOKEN: str = ''
    SESSION_NAME: str = 'autosomnia_session'
    ADMIN_IDS: str = '0'
    API_BASE_URL: str = 'http://localhost:8000'
    LOG_LEVEL: str = 'INFO'
    
    @field_validator('ADMIN_IDS')
    @classmethod
    def parse_admin_ids(cls, v: str) -> list[int]:
        return [int(x) for x in v.split(',') if x.strip()]
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / '.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'  # Allow extra fields in .env without errors
    )