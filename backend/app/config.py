"""Configuration objects loaded by the Flask application factory."""
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "uv3tZx,&x$/wM@R<1x-!E4F+i;C35N+-QF[L&N0n||e")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "r9XY63QfNn0KpXOYPND3sL2xBeoecb0xlGGpcFzNXQ6")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLOCKLIST_ENABLED = True
    JWT_BLOCKLIST_TOKEN_CHECKS = ("access", "refresh")
    BCRYPT_LOG_ROUNDS = 12

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + str(BASE_DIR / "ahrip_dev.sqlite3")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ALLOWED_ORIGINS = [
        o.strip()
        for o in os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
        if o.strip()
    ]
    RATE_LIMIT_STORAGE = os.environ.get("RATE_LIMIT_STORAGE", "memory://")
    RATELIMIT_ENABLED = os.environ.get("RATELIMIT_ENABLED", "true").lower() not in (
        "false", "0", "no", "off",
    )
    RATELIMIT_STORAGE_URI = RATE_LIMIT_STORAGE

    # Threat intel feeds
    PHISHSTATS_FEED_URL = os.environ.get(
        "PHISHSTATS_FEED_URL",
        "https://raw.githubusercontent.com/Phishing-Database/Phishing.Database/master/phishing-links-ACTIVE.txt",
    )
    OPENPHISH_FEED_URL = os.environ.get(
        "OPENPHISH_FEED_URL", "https://openphish.com/feed.txt"
    )
    ALIENVAULT_OTX_KEY = os.environ.get("ALIENVAULT_OTX_KEY", "")
    URLSCAN_API_KEY = os.environ.get("URLSCAN_API_KEY", "")
    THREAT_FEED_REFRESH_HOURS = int(os.environ.get("THREAT_FEED_REFRESH_HOURS", "6"))

    # ML
    RF_MODEL_PATH = os.environ.get("RF_MODEL_PATH", "ml_models/risk_rf_model.pkl")
    KMEANS_MODEL_PATH = os.environ.get("KMEANS_MODEL_PATH", "ml_models/user_clusters.pkl")
    MIN_TRAINING_SAMPLES = int(os.environ.get("MIN_TRAINING_SAMPLES", "20"))
    MIN_USERS_FOR_KMEANS = int(os.environ.get("MIN_USERS_FOR_KMEANS", "3"))

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    APP_NAME = os.environ.get("APP_NAME", "AHRID")

    # When truthy, APScheduler auto-starts: threat ingestion + risk recalc.
    ENABLE_SCHEDULER = os.environ.get("ENABLE_SCHEDULER", "false").lower() in (
        "true", "1", "yes", "on",
    )


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = "production"


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    RATELIMIT_ENABLED = False
    BCRYPT_LOG_ROUNDS = 4


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    return CONFIG_MAP.get(env, DevelopmentConfig)
