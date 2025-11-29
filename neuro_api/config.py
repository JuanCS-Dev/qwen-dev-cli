# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Neuro API"
    version: str = "0.1.0"
    # Add more configuration settings here (e.g., database connection strings)
    class Config:
        env_file = ".env" #Optional, if using .env file

settings = Settings()