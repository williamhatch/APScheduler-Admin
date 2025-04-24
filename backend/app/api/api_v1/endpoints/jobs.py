from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.job import Job
from app.schemas.job import Job as JobSchema, JobCreate, JobUpdate, JobStatusUpdate, JobExecution
from app.services.scheduler import add_job, remove_job, pause_job, resume_job, get_job

router = APIRouter()


@router.get("/", response_model=List[JobSchema])
async def read_jobs(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取任务列表，支持分页和筛选
    """
    query = select(Job)
    
    # 添加筛选条件
    if status:
        query = query.where(Job.status == status)
    if name:
        query = query.where(Job.name.contains(name))
    
    # 添加分页
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    return jobs


@router.post("/", response_model=JobSchema)
async def create_job(
    *,
    db: AsyncSession = Depends(get_db),
    job_in: JobCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    创建新任务
    """
    # 创建任务记录
    job = Job(
        name=job_in.name,
        func=job_in.func,
        args=job_in.args,
        kwargs=job_in.kwargs,
        trigger=job_in.trigger,
        trigger_args=job_in.trigger_args,
        max_instances=job_in.max_instances,
        misfire_grace_time=job_in.misfire_grace_time,
        coalesce=job_in.coalesce,
        description=job_in.description,
        status="running",
        created_by=current_user.id
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # 添加到调度器
    try:
        await add_job(
            db=db,
            job_id=job.id,
            func=job.func,
            trigger=job.trigger,
            trigger_args=job.trigger_args,
            args=job.args,
            kwargs=job.kwargs,
            job_name=job.name,
            max_instances=job.max_instances,
            misfire_grace_time=job.misfire_grace_time,
            coalesce=job.coalesce,
        )
    except Exception as e:
        # 如果添加到调度器失败，更新任务状态
        job.status = "error"
        db.add(job)
        await db.commit()
        await db.refresh(job)
        raise HTTPException(status_code=400, detail=f"添加任务到调度器失败: {str(e)}")
    
    return job


@router.get("/{job_id}", response_model=JobSchema)
async def read_job(
    *,
    db: AsyncSession = Depends(get_db),
    job_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取指定任务信息
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return job


@router.put("/{job_id}", response_model=JobSchema)
async def update_job(
    *,
    db: AsyncSession = Depends(get_db),
    job_id: int,
    job_in: JobUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新指定任务信息
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 更新任务信息
    job_data = {k: v for k, v in job_in.dict(exclude_unset=True).items() if v is not None}
    
    for key, value in job_data.items():
        setattr(job, key, value)
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # 如果任务已经在调度器中，先移除再添加
    try:
        await remove_job(job_id)
    except Exception:
        pass
    
    # 如果任务状态为运行中，添加到调度器
    if job.status == "running":
        try:
            await add_job(
                db=db,
                job_id=job.id,
                func=job.func,
                trigger=job.trigger,
                trigger_args=job.trigger_args,
                args=job.args,
                kwargs=job.kwargs,
                job_name=job.name,
                max_instances=job.max_instances,
                misfire_grace_time=job.misfire_grace_time,
                coalesce=job.coalesce,
            )
        except Exception as e:
            # 如果添加到调度器失败，更新任务状态
            job.status = "error"
            db.add(job)
            await db.commit()
            await db.refresh(job)
            raise HTTPException(status_code=400, detail=f"添加任务到调度器失败: {str(e)}")
    
    return job


@router.delete("/{job_id}", response_model=JobSchema)
async def delete_job(
    *,
    db: AsyncSession = Depends(get_db),
    job_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    删除指定任务
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 从调度器中移除任务
    try:
        await remove_job(job_id)
    except Exception:
        pass
    
    # 从数据库中删除任务
    await db.delete(job)
    await db.commit()
    
    return job


@router.post("/{job_id}/status", response_model=JobSchema)
async def update_job_status(
    *,
    db: AsyncSession = Depends(get_db),
    job_id: int,
    status_in: JobStatusUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新任务状态（暂停/恢复）
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 更新任务状态
    if status_in.status == "paused":
        # 暂停任务
        try:
            await pause_job(job_id)
            job.status = "paused"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"暂停任务失败: {str(e)}")
    elif status_in.status == "running":
        # 恢复任务
        try:
            await resume_job(job_id)
            job.status = "running"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"恢复任务失败: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="无效的状态值")
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    return job


@router.post("/{job_id}/execute", response_model=JobSchema)
async def execute_job(
    *,
    db: AsyncSession = Depends(get_db),
    job_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    立即执行任务
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 获取调度器中的任务
    scheduler_job = await get_job(job_id)
    if not scheduler_job:
        raise HTTPException(status_code=400, detail="任务未在调度器中")
    
    # 立即执行任务
    try:
        scheduler_job.func(*scheduler_job.args, **scheduler_job.kwargs)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"执行任务失败: {str(e)}")
    
    return job
