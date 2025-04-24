from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


# 共享属性
class UserBase(BaseModel):
    """
    用户基础模式
    """
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    username: Optional[str] = None


# 创建用户时的属性
class UserCreate(UserBase):
    """
    创建用户的模式
    """
    username: str
    email: EmailStr
    password: str


# 更新用户时的属性
class UserUpdate(UserBase):
    """
    更新用户的模式
    """
    password: Optional[str] = None


# 数据库中的用户属性
class UserInDBBase(UserBase):
    """
    数据库中用户的基础模式
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 返回给API的用户属性
class User(UserInDBBase):
    """
    返回给API的用户模式
    """
    pass


# 存储在数据库中的用户属性（包含密码）
class UserInDB(UserInDBBase):
    """
    存储在数据库中的用户模式
    """
    hashed_password: str
