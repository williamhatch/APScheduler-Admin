from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base
from app.models.user import User
from app.utils.security import get_password_hash
import logging

# 根据配置选择数据库连接字符串
if settings.DATABASE_TYPE == "mysql":
    SQLALCHEMY_DATABASE_URL = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_SERVER}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
else:
    SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# 创建异步数据库引擎
async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=async_engine, 
    class_=AsyncSession
)

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """
    初始化数据库
    """
    try:
        # 创建所有表
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # 创建初始超级用户
        async with AsyncSessionLocal() as session:
            # 检查是否已存在超级用户
            result = await session.execute(
                "SELECT id FROM user WHERE username = :username",
                {"username": settings.FIRST_SUPERUSER}
            )
            user = result.first()
            
            if not user:
                # 创建超级用户
                db_user = User(
                    username=settings.FIRST_SUPERUSER,
                    email=settings.FIRST_SUPERUSER_EMAIL,
                    hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                    is_active=True,
                    is_superuser=True
                )
                session.add(db_user)
                await session.commit()
                logger.info(f"已创建初始超级用户: {settings.FIRST_SUPERUSER}")
            else:
                logger.info(f"超级用户已存在: {settings.FIRST_SUPERUSER}")
    except Exception as e:
        logger.error(f"初始化数据库时出错: {e}")
        raise
