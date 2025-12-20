from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables before class definition
load_dotenv(verbose=True)

if os.getenv("ENV") is None:
    os.environ["ENV"] = "development"
    print("RPC: ",os.getenv("STARKNET_RPC_URL"))


class Settings(BaseSettings):

    # Database settings
    # database_url: str = os.getenv("DATABASE_URL")
    database_url: str

    
    # StarkNet settings
    starknet_rpc_url: str = os.getenv("STARKNET_RPC_URL") or "http://localhost:5050"
    contract_address: str = os.getenv("JOB_REGISTRY_CONTRACT_ADDRESS") or "0x0315980c7693d042ed612f84cd513f1751688170cd29ed04f4eaa51ec1c26381"
    contract_abi_path: str = "./galaxyrend_job_registry_JobRegistry.contract_class.json"
    # contract_abi_path: str = "./contracts/job_registry/target/dev/galaxyrend_job_registry.contract_class.json"
    
    network: str = os.getenv("STARKNET_NETWORK") or "dev_net" #"devnet"
    
    # Event indexing settings
    enable_event_indexing: bool = os.getenv("ENABLE_EVENT_INDEXING") or True
    start_block: int = os.getenv("START_BLOCK") or 0
    indexer_poll_interval: int = os.getenv("INDEXER_POLL_INTERVAL") or 10

    # The Graph settings
    use_graph: bool = not enable_event_indexing or False  # Use The Graph instead of direct indexing
    graph_endpoint: str = os.getenv("STARKNET_GRAPHQL_URL") or "http://localhost:8000/subgraphs/name/galaxyrend/galaxyrend-subgraph"
    # graph_endpoint: str = "http://localhost:8000/subgraphs/name/galaxyrend/galaxyrend-subgraph"
    
    # Redis settings
    redis_url: str = os.getenv("REDIS_URL") or "redis://localhost:6379"
    
    # IPFS settings
    ipfs_url: str = os.getenv("IPFS_API_URL") or "http://localhost:5001"
    ipfs_gateway_url: str = os.getenv("IPFS_GATEWAY_URL") or "http://localhost:8080"

    # API settings
    api_host: str = os.getenv("HOST") or "0.0.0.0"
    api_port: int = os.getenv("PORT") or 8000
    cors_origins: List[str] = os.getenv("CORS_ORIGINS").split(",") if os.getenv("CORS_ORIGINS") else ["http://localhost:3000", "http://localhost:8080"]

    # Security
    secret_key: str = os.getenv("SECRET_KEY") or "r48turi58847362819SAS"
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY") or "rieo3928IUHJ23455623"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 60
    jwt_refresh_token_expire_days: int = os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS") or 7

    # Logging
    log_level: str = os.getenv("LOG_LEVEL") or "INFO"
    debug: bool = os.getenv("DEBUG") or False
    
    # Additional fields from existing .env (optional)
    # job_registry_contract_address: str = ""  # Legacy field
    # starknet_network: str = "dev_net"  # Legacy field
    # ipfs_api_url: str = "http://127.0.0.1:5001"
    # ipfs_gateway_url: str = "http://127.0.0.1:8080"
    # access_token_expire_minutes: int = 60
    # algorithm: str = "HS256"
    # event_polling_interval: int = 5
    # max_retries: int = 3
    # batch_size: int = 100
    # log_format: str = "json"
    # celery_broker_url: str = "redis://localhost:6379/1"
    # celery_result_backend: str = "redis://localhost:6379/2"
    
    model_config = {"env_file": ".env", "extra": "ignore"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convert DATABASE_URL to async format for asyncpg
        if self.database_url:
            if self.database_url.startswith("postgres://"):
                self.database_url = self.database_url.replace(
                    "postgres://", "postgresql+asyncpg://", 1
                )
            elif self.database_url.startswith("postgresql://") and "asyncpg" not in self.database_url:
                self.database_url = self.database_url.replace(
                    "postgresql://", "postgresql+asyncpg://", 1
                )

# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get global settings instance (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# def get_settings() -> Settings:
#     global _settings
#     if _settings is None:
#         _settings = Settings()
#     return _settings
