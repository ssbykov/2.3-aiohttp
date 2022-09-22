from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from pydantic import BaseModel


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

engine = create_async_engine(f"postgresql+asyncpg://"
                             f"{os.getenv('DB_USER')}"
                             f":{os.getenv('DB_PASS')}"
                             f"@{os.getenv('DB_HOST')}"
                             f":{os.getenv('DB_PORT')}"
                             f"/{os.getenv('DB_BASE')}", echo=True)
Base = declarative_base()
Session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Advertisement(Base):
    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True)
    heading = Column(String(200), nullable=False)
    description = Column(String())
    creation_date = Column(DateTime(), server_default=func.now())
    owner = Column(String(100))


class CreateAdvSchema(BaseModel):
    heading: str
    description: str
    owner: str

