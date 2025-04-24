from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.db.base import Base
from app.core.config import settings

# 导入所有模型，以便Alembic可以创建迁移
from app.models.user import User
from app.models.job import Job
from app.models.job_log import JobLog

# 这是Alembic配置对象，可以从env.py中的其他位置访问
config = context.config

# 解析配置文件中的section
fileConfig(config.config_file_name)

# 添加MetaData对象，用于'autogenerate'支持
target_metadata = Base.metadata

# 根据配置选择数据库连接字符串
if settings.DATABASE_TYPE == "mysql":
    config.set_main_option(
        "sqlalchemy.url",
        f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_SERVER}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
    )
else:
    config.set_main_option(
        "sqlalchemy.url",
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


def run_migrations_offline() -> None:
    """
    在"离线"模式下运行迁移。

    这种模式下不需要网络连接，只需要加载一个数据库URL
    并传递给context.configure()。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    在"在线"模式下运行迁移。

    在这种模式下，可以使用Engine
    并且连接会在每个迁移脚本中自动建立。
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
