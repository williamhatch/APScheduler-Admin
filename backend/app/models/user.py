from sqlalchemy import Boolean, Column, String, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class User(Base):
    """
    用户模型
    """
    username = Column(String(32), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    hashed_password = Column(String(100), nullable=False, comment="哈希后的密码")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_superuser = Column(Boolean, default=False, comment="是否为超级用户")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
