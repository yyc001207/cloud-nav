from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
from app.core.logger import logger


engine = None
async_session_factory = None


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    global engine, async_session_factory
    engine = create_async_engine(
        settings.MYSQL_URL,
        pool_size=settings.MYSQL_POOL_SIZE,
        max_overflow=settings.MYSQL_MAX_OVERFLOW,
        pool_pre_ping=True,
        echo=settings.DEBUG,
    )
    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("MySQL 数据库连接成功，数据表已创建")


async def close_db() -> None:
    global engine
    if engine:
        await engine.dispose()
        logger.info("MySQL 数据库连接已关闭")


def get_session() -> AsyncSession:
    if async_session_factory is None:
        raise RuntimeError("数据库未初始化")
    return async_session_factory()
