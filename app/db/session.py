
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import env

engine = create_async_engine(env.db.db_url, echo=False)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    """
    Инициализация базы данных.
    Теперь используем Alembic для миграций.
    Для создания новой схемы используйте: alembic upgrade head
    """
    # Больше не используем create_all, используем Alembic
    pass