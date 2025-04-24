from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, jobs, job_logs

# 创建API路由器
api_router = APIRouter()

# 包含各个端点的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["任务"])
api_router.include_router(job_logs.router, prefix="/logs", tags=["日志"])
