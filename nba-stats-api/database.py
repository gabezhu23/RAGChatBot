from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./nba_stats.db"

# create connection to SQLite file, nba_stats.db gets created automatically when app is first ran
engine = create_engine(
    # Allows multipel requests to use same connection
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# creates individual database sessions for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

# automatically opens and closes DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()