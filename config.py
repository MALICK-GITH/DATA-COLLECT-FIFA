import os
from urllib.parse import parse_qsl, urlsplit
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "https://888starz.bet/service-api/LiveFeed")
    API_FALLBACK_BASE_URL = os.getenv("API_FALLBACK_BASE_URL", "").strip()
    API_FALLBACK_URL = os.getenv("API_FALLBACK_URL", "").strip()
    API_ENDPOINT = os.getenv("API_ENDPOINT", "Get1x2_VZip")
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))
    API_RETRY_COUNT = int(os.getenv("API_RETRY_COUNT", "3"))
    API_RETRY_BACKOFF_SECONDS = float(os.getenv("API_RETRY_BACKOFF_SECONDS", "2"))
    API_USER_AGENT = os.getenv("API_USER_AGENT", "match-saver/1.0")
    API_ACCEPT_ENCODING = os.getenv("API_ACCEPT_ENCODING", "gzip, deflate")
    API_USE_BROWSER_HEADERS = os.getenv("API_USE_BROWSER_HEADERS", "false").lower() == "true"
    API_BROWSER_USER_AGENT = os.getenv(
        "API_BROWSER_USER_AGENT",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    )
    API_BROWSER_ACCEPT = os.getenv(
        "API_BROWSER_ACCEPT",
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    )
    API_BROWSER_ACCEPT_LANGUAGE = os.getenv("API_BROWSER_ACCEPT_LANGUAGE", "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7")
    API_BROWSER_CACHE_CONTROL = os.getenv("API_BROWSER_CACHE_CONTROL", "max-age=0")
    API_BROWSER_COOKIE = os.getenv("API_BROWSER_COOKIE", "").strip()
    API_FALLBACK_USE_BROWSER_HEADERS = os.getenv("API_FALLBACK_USE_BROWSER_HEADERS", "false").lower() == "true"
    API_FALLBACK_USER_AGENT = os.getenv(
        "API_FALLBACK_USER_AGENT",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"
    )
    API_FALLBACK_ACCEPT = os.getenv(
        "API_FALLBACK_ACCEPT",
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    )
    API_FALLBACK_ACCEPT_LANGUAGE = os.getenv("API_FALLBACK_ACCEPT_LANGUAGE", "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7")
    API_FALLBACK_CACHE_CONTROL = os.getenv("API_FALLBACK_CACHE_CONTROL", "max-age=0")
    API_FALLBACK_COOKIE = os.getenv("API_FALLBACK_COOKIE", "").strip()
    USE_PLAYWRIGHT_FETCH = os.getenv("USE_PLAYWRIGHT_FETCH", "false").lower() == "true"
    PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
    PLAYWRIGHT_TIMEOUT_MS = int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "90000"))
    PLAYWRIGHT_PRIMARY_PAGE_URL = os.getenv("PLAYWRIGHT_PRIMARY_PAGE_URL", "https://888starz.bet/")
    PLAYWRIGHT_FALLBACK_PAGE_URL = os.getenv("PLAYWRIGHT_FALLBACK_PAGE_URL", "https://1xbet.com/")
    
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
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # sqlite or postgresql
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "match_history")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    
    # SQLite fallback
    SQLITE_PATH = os.getenv("SQLITE_PATH", "match_history.db")
    
    # Cron Configuration
    CRON_SCHEDULE = os.getenv("CRON_SCHEDULE", "*/5 * * * *")  # Every 5 minutes
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
    def get_api_targets(cls):
        targets = [{
            "url": cls.get_api_url(),
            "params": cls.get_api_params(),
            "headers": cls.get_primary_api_headers()
        }]

        if cls.API_FALLBACK_URL:
            parsed = urlsplit(cls.API_FALLBACK_URL)
            fallback_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            fallback_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
            targets.append({
                "url": fallback_url,
                "params": fallback_params or cls.get_api_params(),
                "headers": cls.get_fallback_api_headers()
            })

        if cls.API_FALLBACK_BASE_URL:
            fallback_url = f"{cls.API_FALLBACK_BASE_URL.rstrip('/')}/{cls.API_ENDPOINT.lstrip('/')}"
            if all(target["url"] != fallback_url for target in targets):
                targets.append({
                    "url": fallback_url,
                    "params": cls.get_api_params(),
                    "headers": cls.get_fallback_api_headers()
                })

        return targets
    
    @classmethod
    def get_api_headers(cls):
        return {
            "Accept": "application/json",
            "User-Agent": cls.API_USER_AGENT,
            "Accept-Encoding": cls.API_ACCEPT_ENCODING
        }

    @classmethod
    def get_primary_api_headers(cls):
        if not cls.API_USE_BROWSER_HEADERS:
            return cls.get_api_headers()

        headers = {
            "Accept": cls.API_BROWSER_ACCEPT,
            "Accept-Language": cls.API_BROWSER_ACCEPT_LANGUAGE,
            "Cache-Control": cls.API_BROWSER_CACHE_CONTROL,
            "User-Agent": cls.API_BROWSER_USER_AGENT,
            "Accept-Encoding": cls.API_ACCEPT_ENCODING,
            "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }
        if cls.API_BROWSER_COOKIE:
            headers["Cookie"] = cls.API_BROWSER_COOKIE
        return headers

    @classmethod
    def get_fallback_api_headers(cls):
        if not cls.API_FALLBACK_USE_BROWSER_HEADERS:
            return cls.get_api_headers()

        headers = {
            "Accept": cls.API_FALLBACK_ACCEPT,
            "Accept-Language": cls.API_FALLBACK_ACCEPT_LANGUAGE,
            "Cache-Control": cls.API_FALLBACK_CACHE_CONTROL,
            "User-Agent": cls.API_FALLBACK_USER_AGENT,
            "Accept-Encoding": cls.API_ACCEPT_ENCODING,
            "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }
        if cls.API_FALLBACK_COOKIE:
            headers["Cookie"] = cls.API_FALLBACK_COOKIE
        return headers

    @classmethod
    def get_api_browser_page_url(cls):
        return cls.PLAYWRIGHT_PRIMARY_PAGE_URL

    @classmethod
    def get_fallback_browser_page_url(cls):
        return cls.PLAYWRIGHT_FALLBACK_PAGE_URL
    
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
