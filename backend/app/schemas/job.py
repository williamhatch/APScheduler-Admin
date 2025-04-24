from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel
from datetime import datetime


# 共享属性
class JobBase(BaseModel):
    """
    任务基础模式
    """
    name: str
    func: str
    args: Optional[List[Any]] = None
    kwargs: Optional[Dict[str, Any]] = None
    trigger: str  # cron, interval, date
    trigger_args: Dict[str, Any]
    max_instances: Optional[int] = 1
    misfire_grace_time: Optional[int] = 60
    coalesce: Optional[bool] = False
    description: Optional[str] = None


# 创建任务时的属性
class JobCreate(JobBase):
    """
    创建任务的模式
    """
    pass


# 更新任务时的属性
class JobUpdate(BaseModel):
    """
    更新任务的模式
    """
    name: Optional[str] = None
    func: Optional[str] = None
    args: Optional[List[Any]] = None
    kwargs: Optional[Dict[str, Any]] = None
    trigger: Optional[str] = None
    trigger_args: Optional[Dict[str, Any]] = None
    max_instances: Optional[int] = None
    misfire_grace_time: Optional[int] = None
    coalesce: Optional[bool] = None
    description: Optional[str] = None
    status: Optional[str] = None


# 数据库中的任务属性
class JobInDBBase(JobBase):
    """
    数据库中任务的基础模式
    """
    id: int
    next_run_time: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: int

    class Config:
        from_attributes = True


# 返回给API的任务属性
class Job(JobInDBBase):
    """
    返回给API的任务模式
    """
    pass


# 任务状态更新
class JobStatusUpdate(BaseModel):
    """
    更新任务状态的模式
    """
    status: str  # running, paused


# 任务执行
class JobExecution(BaseModel):
    """
    执行任务的模式
    """
    job_id: int
