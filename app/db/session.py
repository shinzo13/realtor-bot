from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import config

engine = create_async_engine(config.db_url, echo=False)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)