import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "https://888starz.bet/service-api/LiveFeed")
    API_ENDPOINT = os.getenv("API_ENDPOINT", "Get1x2_VZip")
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    API_RETRY_COUNT = int(os.getenv("API_RETRY_COUNT", "3"))
    API_RETRY_BACKOFF_SECONDS = float(os.getenv("API_RETRY_BACKOFF_SECONDS", "2"))
    API_USER_AGENT = os.getenv("API_USER_AGENT", "match-saver/1.0")
    API_ACCEPT_ENCODING = os.getenv("API_ACCEPT_ENCODING", "gzip, deflate")
    
    # Default parameters
    DEFAULT_SPORTS = int(os.getenv("API_SPORTS", "85"))  # FIFA
    DEFAULT_COUNT = int(os.getenv("API_COUNT", "100"))
    DEFAULT_LNG = os.getenv("API_LANGUAGE", "fr")
    DEFAULT_MODE = int(os.getenv("API_MODE", "4"))
    API_GROUP = os.getenv("API_GROUP")
    API_COUNTRY = os.getenv("API_COUNTRY")
    API_PARTNER = os.getenv("API_PARTNER")
    API_GET_EMPTY = os.getenv("API_GET_EMPTY", "false").lower() == "true"
    API_VIRTUAL_SPORTS = os.getenv("API_VIRTUAL_SPORTS", "false").lower() == "true"
    API_NO_FILTER_BLOCK_EVENT = os.getenv("API_NO_FILTER_BLOCK_EVENT", "false").lower() == "true"
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DATABASE_URL")
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "match_history")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    SQLITE_PATH = os.getenv("SQLITE_PATH", "match_history.db")
    
    # Cron Configuration
    CRON_SCHEDULE = os.getenv("CRON_SCHEDULE", "*/5 * * * *")
    SCHEDULE_EVERY_MINUTES = int(os.getenv("SCHEDULE_EVERY_MINUTES", "5"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "match_saver.log")
    
    # Webhook
    WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "")
    
    @classmethod
    def get_database_url(cls):
        if cls.DATABASE_URL:
            return cls.DATABASE_URL
        if cls.DB_TYPE == "postgresql":
            return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        else:
            return f"sqlite:///{cls.SQLITE_PATH}"
    
    @classmethod
    def get_api_url(cls):
        return f"{cls.API_BASE_URL.rstrip('/')}/{cls.API_ENDPOINT.lstrip('/')}"
    
    @classmethod
    def get_api_headers(cls):
        return {
            "Accept": "application/json",
            "User-Agent": cls.API_USER_AGENT,
            "Accept-Encoding": cls.API_ACCEPT_ENCODING
        }
    
    @classmethod
    def get_api_params(cls):
        params = {
            "sports": cls.DEFAULT_SPORTS,
            "count": cls.DEFAULT_COUNT,
            "lng": cls.DEFAULT_LNG,
            "mode": cls.DEFAULT_MODE
        }
        optional_params = {
            "gr": cls.API_GROUP,
            "country": cls.API_COUNTRY,
            "partner": cls.API_PARTNER
        }
        
        for key, value in optional_params.items():
            if value not in (None, ""):
                params[key] = value
        
        if cls.API_GET_EMPTY:
            params["getEmpty"] = "true"
        if cls.API_VIRTUAL_SPORTS:
            params["virtualSports"] = "true"
        if cls.API_NO_FILTER_BLOCK_EVENT:
            params["noFilterBlockEvent"] = "true"
        
        return params
