"""
Centralized config management for SkyrisReward backend.
Loads environment variables and provides global config constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "reward")
MYSQL_USER = os.environ.get("MYSQL_USER", "reward")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "reward")

SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key")
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)
