from typing import Optional
from pydantic import BaseModel
from datetime import datetime


# 共享属性
class JobLogBase(BaseModel):
    """
    任务日志基础模式
    """
    job_id: int
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    output: Optional[str] = None


# 创建任务日志时的属性
class JobLogCreate(JobLogBase):
    """
    创建任务日志的模式
    """
    pass


# 数据库中的任务日志属性
class JobLogInDBBase(JobLogBase):
    """
    数据库中任务日志的基础模式
    """
    id: int

    class Config:
        from_attributes = True


# 返回给API的任务日志属性
class JobLog(JobLogInDBBase):
    """
    返回给API的任务日志模式
    """
    pass


# 任务日志查询参数
class JobLogQuery(BaseModel):
    """
    任务日志查询参数
    """
    job_id: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
