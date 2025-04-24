from typing import Dict, Any, Optional, List, Union
import logging
import json
from datetime import datetime
import importlib

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.models.job import Job
from app.models.job_log import JobLog

# 配置日志
logger = logging.getLogger(__name__)

# 创建调度器
jobstores = {
    'default': SQLAlchemyJobStore(url=f"sqlite:///jobs.sqlite")
}

executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}

job_defaults = settings.APSCHEDULER_JOB_DEFAULTS

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
)


async def log_job_execution(job_id: int, db: AsyncSession, func_result: Any = None, error: Exception = None) -> None:
    """
    记录任务执行日志
    """
    try:
        # 查询任务
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalars().first()
        
        if not job:
            logger.error(f"任务不存在: {job_id}")
            return
        
        # 创建日志记录
        end_time = datetime.now()
        job_log = JobLog(
            job_id=job_id,
            status="success" if error is None else "failed",
            start_time=datetime.now(),  # 这里应该是任务开始时间，但为简化，使用当前时间
            end_time=end_time,
            duration=0,  # 这里应该计算实际持续时间
            error_message=str(error) if error else None,
            output=str(func_result) if func_result else None
        )
        
        db.add(job_log)
        await db.commit()
        
    except Exception as e:
        logger.error(f"记录任务执行日志时出错: {e}")


async def import_function(func_path: str) -> callable:
    """
    导入函数
    """
    try:
        module_path, func_name = func_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, func_name)
    except (ImportError, AttributeError) as e:
        logger.error(f"导入函数失败: {e}")
        raise ValueError(f"无法导入函数: {func_path}")


async def add_job(
    db: AsyncSession,
    job_id: int,
    func: str,
    trigger: str,
    trigger_args: Dict[str, Any],
    args: Optional[List] = None,
    kwargs: Optional[Dict] = None,
    job_name: str = None,
    max_instances: int = 1,
    misfire_grace_time: int = 60,
    coalesce: bool = False,
) -> str:
    """
    添加任务
    """
    try:
        # 导入函数
        func_obj = await import_function(func)
        
        # 添加任务
        job = scheduler.add_job(
            func_obj,
            trigger=trigger,
            args=args or [],
            kwargs=kwargs or {},
            id=str(job_id),
            name=job_name,
            max_instances=max_instances,
            misfire_grace_time=misfire_grace_time,
            coalesce=coalesce,
            **trigger_args
        )
        
        return job.id
    except Exception as e:
        logger.error(f"添加任务失败: {e}")
        raise


async def remove_job(job_id: Union[str, int]) -> None:
    """
    移除任务
    """
    try:
        scheduler.remove_job(str(job_id))
    except Exception as e:
        logger.error(f"移除任务失败: {e}")
        raise


async def pause_job(job_id: Union[str, int]) -> None:
    """
    暂停任务
    """
    try:
        scheduler.pause_job(str(job_id))
    except Exception as e:
        logger.error(f"暂停任务失败: {e}")
        raise


async def resume_job(job_id: Union[str, int]) -> None:
    """
    恢复任务
    """
    try:
        scheduler.resume_job(str(job_id))
    except Exception as e:
        logger.error(f"恢复任务失败: {e}")
        raise


async def get_job(job_id: Union[str, int]) -> Optional[Dict[str, Any]]:
    """
    获取任务信息
    """
    try:
        job = scheduler.get_job(str(job_id))
        if job:
            return {
                "id": job.id,
                "name": job.name,
                "func": job.func_ref.__name__,
                "args": job.args,
                "kwargs": job.kwargs,
                "trigger": str(job.trigger),
                "next_run_time": job.next_run_time,
            }
        return None
    except Exception as e:
        logger.error(f"获取任务信息失败: {e}")
        raise


async def get_jobs() -> List[Dict[str, Any]]:
    """
    获取所有任务信息
    """
    try:
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "func": job.func_ref.__name__,
                "args": job.args,
                "kwargs": job.kwargs,
                "trigger": str(job.trigger),
                "next_run_time": job.next_run_time,
            })
        return jobs
    except Exception as e:
        logger.error(f"获取所有任务信息失败: {e}")
        raise


def start_scheduler():
    """
    启动调度器
    """
    try:
        scheduler.start()
        logger.info("调度器已启动")
    except Exception as e:
        logger.error(f"启动调度器失败: {e}")
        raise


def shutdown_scheduler():
    """
    关闭调度器
    """
    try:
        scheduler.shutdown()
        logger.info("调度器已关闭")
    except Exception as e:
        logger.error(f"关闭调度器失败: {e}")
        raise
