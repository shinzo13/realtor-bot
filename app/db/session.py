
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import env

engine = create_async_engine(env.db.db_url, echo=False)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    from app.db.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)