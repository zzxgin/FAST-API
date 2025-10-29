"""Database connection and session management for FastAPI/SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

load_dotenv()

# 从环境变量拼接数据库连接字符串
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "reward")
MYSQL_USER = os.environ.get("MYSQL_USER", "reward")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "reward")

SQLALCHEMY_DATABASE_URL = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """FastAPI dependency for getting a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
