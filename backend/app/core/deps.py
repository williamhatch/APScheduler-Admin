from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.schemas.token import TokenPayload
from app.core.config import settings
from app.utils.security import ALGORITHM

# OAuth2密码承载依赖项
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_db() -> Generator:
    """
    获取数据库会话依赖项
    """
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前用户依赖项
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if token_data.sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(select(User).where(User.id == token_data.sub))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    
    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃的超级用户依赖项
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="权限不足"
        )
    return current_user
