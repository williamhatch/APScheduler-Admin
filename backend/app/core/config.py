from typing import List, Optional, Union, Dict, Any
from pydantic import AnyHttpUrl, EmailStr, validator
from pydantic_settings import BaseSettings
import json
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    系统配置类
    """
    # 基本配置
    PROJECT_NAME: str = "APScheduler-Admin"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 数据库配置
    DATABASE_TYPE: str = "mysql"  # 可选: mysql, postgresql
    # MySQL配置
    MYSQL_SERVER: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str
    MYSQL_PORT: str
    # PostgreSQL配置
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str

    # 初始管理员账号
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_EMAIL: EmailStr

    # APScheduler配置
    APSCHEDULER_JOBSTORES: str
    APSCHEDULER_EXECUTORS: str
    APSCHEDULER_JOB_DEFAULTS: Dict[str, Any]

    @validator("APSCHEDULER_JOB_DEFAULTS", pre=True)
    def parse_job_defaults(cls, v: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(v, str):
            return json.loads(v)
        return v

    class Config:
        env_file = os.path.join(Path(__file__).resolve().parent.parent.parent.parent, ".env")
        case_sensitive = True


settings = Settings()
