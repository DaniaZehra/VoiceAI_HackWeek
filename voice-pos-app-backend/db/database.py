from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables from the nearest .env (works regardless of CWD)
load_dotenv(find_dotenv())

# Prefer DATABASE_URL from environment, fallback to legacy hardcoded URL
_url = os.getenv("DATABASE_URL") or "postgresql://postgres:tILHebFZFIqqlZcxmsFMgcxMcsRkTZfj@yamanote.proxy.rlwy.net:46383/railway"

# Ensure Railway SSL requirement
if _url and "sslmode=" not in _url:
    connector = "&" if "?" in _url else "?"
    _url = f"{_url}{connector}sslmode=require"

DATABASE_URL = _url

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
