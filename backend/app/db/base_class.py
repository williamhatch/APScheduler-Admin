from typing import Any
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime


class Base(DeclarativeBase):
    """
    SQLAlchemy 基础类
    """
    id = Column(Integer, primary_key=True, index=True)
    
    # 生成表名
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
