"""
Configuration settings for the Irado Chatbot Dashboard
"""
import os
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables (supports local development)
load_dotenv()


def _parse_pg_connection_string(conn_str: str) -> dict:
    """Parse common PostgreSQL connection string formats into a dict."""
    if not conn_str:
        return {}

    conn_str = conn_str.strip()
    parsed: dict[str, str] = {}

    # URL style: postgres://user:password@host:port/dbname?sslmode=require
    if conn_str.startswith(("postgres://", "postgresql://")):
        url = urlparse(conn_str)
        parsed["host"] = url.hostname or ""
        if url.port:
            parsed["port"] = str(url.port)
        parsed["database"] = url.path.lstrip("/")
        parsed["user"] = url.username or ""
        parsed["password"] = url.password or ""

        query = parse_qs(url.query)
        if "sslmode" in query and query["sslmode"]:
            parsed["sslmode"] = query["sslmode"][0]
        return parsed

    # Key/value style: Host=...;Username=...;Password=...;Database=...;Port=...;Ssl Mode=Require;
    normalized_pairs = {}
    delimiter = ";" if ";" in conn_str else " "
    tokens = conn_str.replace("\n", delimiter).split(delimiter)

    for token in tokens:
        token = token.strip()
        if not token or "=" not in token:
            continue
        key, value = token.split("=", 1)
        normalized_key = key.strip().lower().replace(" ", "")
        normalized_pairs[normalized_key] = value.strip()

    translation_map = {
        "host": "host",
        "hostname": "host",
        "server": "host",
        "address": "host",
        "addr": "host",
        "username": "user",
        "user": "user",
        "userid": "user",
        "uid": "user",
        "password": "password",
        "pwd": "password",
        "pass": "password",
        "database": "database",
        "dbname": "database",
        "db": "database",
        "initialcatalog": "database",
        "port": "port",
        "sslmode": "sslmode",
        "ssl": "sslmode",
        "enablessl": "sslmode",
    }

    for key, value in normalized_pairs.items():
        mapped_key = translation_map.get(key)
        if mapped_key:
            parsed[mapped_key] = value

    return parsed


def _first_set_connection_string() -> str | None:
    """Find the first available connection string from known environment variable patterns."""
    candidates = [
        os.getenv("POSTGRES_CONNECTION_STRING"),
        os.getenv("AZURE_POSTGRESQL_CONNECTIONSTRING"),
        os.getenv("DATABASE_URL"),
    ]

    # Azure app service stores connection strings as POSTGRESQLCONNSTR_* or CUSTOMCONNSTR_*
    for key, value in os.environ.items():
        key_upper = key.upper()
        if value and (
            key_upper.startswith("POSTGRESQLCONNSTR_")
            or (key_upper.startswith("CUSTOMCONNSTR_") and "POSTGRES" in key_upper)
        ):
            candidates.append(value)

    for candidate in candidates:
        if candidate:
            return candidate
    return None


def _build_database_url(user: str | None, password: str | None, host: str | None, port: str | None, database: str | None) -> str | None:
    """Construct a SQLAlchemy/Postgres DSN if all parts are available."""
    if not all([user, password, host, port, database]):
        return None
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


class Config:
    """Dashboard configuration object populated from environment variables."""

    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')
    OPENAI_TEMPERATURE = 1.0
    OPENAI_MAX_TOKENS = 2000

    # Base PostgreSQL configuration (explicit app settings win)
    POSTGRES_HOST = os.getenv('POSTGRES_HOST') or os.getenv('CHAT_DB_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB') or os.getenv('CHAT_DB_NAME', 'irado_chat')
    POSTGRES_USER = os.getenv('POSTGRES_USER') or os.getenv('CHAT_DB_USER', 'irado')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD') or os.getenv('CHAT_DB_PASSWORD')
    POSTGRES_SSL_MODE = os.getenv('POSTGRES_SSL_MODE') or os.getenv('POSTGRES_SSLMODE') or 'require'
    APP_TIMEZONE = os.getenv('APP_TIMEZONE', 'Europe/Amsterdam')

    # Allow Azure connection strings to override individual settings
    _RAW_CONNECTION = _first_set_connection_string()
    _PARSED_CONNECTION = _parse_pg_connection_string(_RAW_CONNECTION) if _RAW_CONNECTION else {}

    if _PARSED_CONNECTION:
        POSTGRES_HOST = _PARSED_CONNECTION.get('host', POSTGRES_HOST)
        POSTGRES_PORT = _PARSED_CONNECTION.get('port', POSTGRES_PORT)
        POSTGRES_DB = _PARSED_CONNECTION.get('database', POSTGRES_DB)
        POSTGRES_USER = _PARSED_CONNECTION.get('user', POSTGRES_USER)
        POSTGRES_PASSWORD = _PARSED_CONNECTION.get('password', POSTGRES_PASSWORD)
        POSTGRES_SSL_MODE = _PARSED_CONNECTION.get('sslmode', POSTGRES_SSL_MODE)

    # Normalise port and defaults
    POSTGRES_PORT = str(POSTGRES_PORT or '5432')
    POSTGRES_SSL_MODE = POSTGRES_SSL_MODE or 'require'

    DATABASE_URL = _build_database_url(POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB) or os.getenv('DATABASE_URL')

    # Email Configuration
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # Chat Configuration
    CHAT_BASIC_AUTH_USER = os.getenv('CHAT_BASIC_AUTH_USER', 'irado')
    CHAT_BASIC_AUTH_PASSWORD = os.getenv('CHAT_BASIC_AUTH_PASSWORD')

    # Allowed municipalities
    ALLOWED_MUNICIPALITIES = ['Vlaardingen', 'Capelle aan den IJssel', 'Schiedam']

    # Address validation configuration
    OPEN_POSTCODE_API_BASE_URL = 'https://openpostcode.nl/api'
    ADDRESS_VALIDATION_ENABLED = True
    SERVICE_AREA_VALIDATION_ENABLED = True

    # Service area postcode ranges
    SERVICE_AREAS = {
        'Capelle aan den IJssel': ['2900', '2901', '2902', '2903', '2904', '2905', '2906', '2907', '2908', '2909'],
        'Schiedam': ['3100', '3101', '3102', '3103', '3104', '3105', '3106', '3107', '3108', '3109',
                    '3110', '3111', '3112', '3113', '3114', '3115', '3116', '3117', '3118', '3119',
                    '3120', '3121', '3122', '3123', '3124', '3125'],
        'Vlaardingen': ['3130', '3131', '3132', '3133', '3134', '3135', '3136', '3137', '3138']
    }

    # Email addresses
    INTERNAL_EMAIL = 'a.jonker@mainfact.ai'
    FROM_EMAIL = 'irado@mainfact.ai'
    NOREPLY_EMAIL = 'noreply@mainfact.ai'
