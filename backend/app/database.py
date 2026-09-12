import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# On Vercel (serverless read-only filesystem), write SQLite DB to /tmp
default_db = "/tmp/gossipnet.db" if os.getenv("VERCEL") else "./gossipnet.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_db}")

# Add connect_args for SQLite
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
