from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """
    访问令牌模式
    """
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """
    令牌载荷模式
    """
    sub: Optional[int] = None
