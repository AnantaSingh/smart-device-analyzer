from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API configurations
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # AI Model configurations
    MODEL_PATH: str = "models/"
    
    # Data pipeline configurations
    BATCH_SIZE: int = 1000
    MAX_WORKERS: int = 4
    
    class Config:
        env_file = ".env"

settings = Settings() 