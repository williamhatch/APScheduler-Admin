from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.job_log import JobLog
from app.schemas.job_log import JobLog as JobLogSchema, JobLogQuery

router = APIRouter()


@router.get("/", response_model=List[JobLogSchema])
async def read_job_logs(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    job_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取任务日志列表，支持分页和筛选
    """
    query = select(JobLog).order_by(desc(JobLog.start_time))
    
    # 添加筛选条件
    if job_id:
        query = query.where(JobLog.job_id == job_id)
    if status:
        query = query.where(JobLog.status == status)
    if start_date:
        query = query.where(JobLog.start_time >= start_date)
    if end_date:
        query = query.where(JobLog.start_time <= end_date)
    
    # 添加分页
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    return logs


@router.get("/{log_id}", response_model=JobLogSchema)
async def read_job_log(
    *,
    db: AsyncSession = Depends(get_db),
    log_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取指定任务日志信息
    """
    result = await db.execute(select(JobLog).where(JobLog.id == log_id))
    log = result.scalars().first()
    
    if not log:
        raise HTTPException(status_code=404, detail="任务日志不存在")
    
    return log


@router.delete("/{log_id}", response_model=JobLogSchema)
async def delete_job_log(
    *,
    db: AsyncSession = Depends(get_db),
    log_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    删除指定任务日志
    """
    result = await db.execute(select(JobLog).where(JobLog.id == log_id))
    log = result.scalars().first()
    
    if not log:
        raise HTTPException(status_code=404, detail="任务日志不存在")
    
    # 从数据库中删除任务日志
    await db.delete(log)
    await db.commit()
    
    return log


@router.delete("/job/{job_id}", response_model=int)
async def delete_job_logs(
    *,
    db: AsyncSession = Depends(get_db),
    job_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    删除指定任务的所有日志
    """
    # 查询指定任务的所有日志
    result = await db.execute(select(JobLog).where(JobLog.job_id == job_id))
    logs = result.scalars().all()
    
    if not logs:
        return 0
    
    # 从数据库中删除任务日志
    count = 0
    for log in logs:
        await db.delete(log)
        count += 1
    
    await db.commit()
    
    return count
