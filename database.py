from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from config import Config

DATABASE_URL = Config.DATABASE_URL.replace("postgres://", "postgresql://")#For production
#DATABASE_URL = Config.DATABASE_URL

engine = create_engine(DATABASE_URL,pool_pre_ping=True)#To ensure connection with production db
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()