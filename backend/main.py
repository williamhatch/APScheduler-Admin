from fastapi import FastAPI, Form, HTTPException, Depends, Header, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, List, Any
from pydantic import BaseModel
import json

# 定义登录请求模型
class LoginRequest(BaseModel):
    username: str
    password: str

app = FastAPI(
    title="APScheduler管理系统",
    description="APScheduler管理系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟数据
mock_user = {"id": 1, "username": "admin", "email": "admin@example.com", "is_active": True, "is_superuser": True}
mock_token = "mock_token"
mock_jobs = [
    {"id": 1, "name": "测试任务", "func": "test_job", "trigger": "interval", "args": [], "kwargs": {}, "next_run_time": "2025-04-24T15:00:00", "status": "running"},
    {"id": 2, "name": "示例任务", "func": "example_job", "trigger": "cron", "args": [], "kwargs": {}, "next_run_time": "2025-04-24T16:00:00", "status": "paused"}
]
mock_logs = [
    {"id": 1, "job_id": 1, "status": "success", "message": "任务执行成功", "created_at": "2025-04-24T14:00:00", "start_time": "2025-04-24T14:00:00", "duration": 1.5},
    {"id": 2, "job_id": 2, "status": "failed", "message": "任务执行失败", "created_at": "2025-04-24T13:00:00", "start_time": "2025-04-24T13:00:00", "duration": 0.8}
]
mock_settings = {"timezone": "Asia/Shanghai", "job_misfire_grace_time": 60, "job_coalesce": True, "job_max_instances": 3}

# 验证token
def verify_token(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        if token == mock_token:
            return token
    return None

# 登录API - 支持JSON格式
@app.post("/api/v1/auth/login")
async def login(login_data: LoginRequest):
    print(f"登录尝试: {login_data.username}, {login_data.password}")
    # 只允许用户名为admin，密码为admin的用户登录
    if login_data.username == "admin" and login_data.password == "admin":
        return {"access_token": mock_token, "token_type": "bearer", "user": mock_user}
    raise HTTPException(status_code=401, detail="用户名或密码错误")

# 登录API - 支持Form格式（保留兼容性）
@app.post("/api/v1/auth/login-form")
async def login_form(username: str = Form(...), password: str = Form(...)):
    print(f"Form登录尝试: {username}, {password}")
    if username == "admin" and password == "admin":
        return {"access_token": mock_token, "token_type": "bearer", "user": mock_user}
    raise HTTPException(status_code=401, detail="用户名或密码错误")

# 获取用户信息
@app.get("/api/v1/users/me")
async def get_user_info(token: str = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    return mock_user

# 测试token
@app.post("/api/v1/auth/test-token")
async def test_token(token: str = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    return {"status": "success", "message": "Token有效"}

# 获取任务列表
@app.get("/api/v1/jobs")
async def get_jobs(
    token: str = Depends(verify_token),
    limit: int = Query(10, description="每页数量"),
    offset: int = Query(0, description="偏移量"),
    status: Optional[str] = Query(None, description="任务状态")
):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 根据状态过滤任务
    filtered_jobs = mock_jobs
    if status:
        filtered_jobs = [job for job in mock_jobs if job["status"] == status]
    
    # 分页
    paginated_jobs = filtered_jobs[offset:offset+limit]
    
    # 直接返回数组，而不是包含 items 和 total 的对象
    return paginated_jobs

# 获取任务详情
@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: int, token: str = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 查找任务
    for job in mock_jobs:
        if job["id"] == job_id:
            return job
    
    raise HTTPException(status_code=404, detail="任务不存在")

# 创建任务
@app.post("/api/v1/jobs")
async def create_job(token: str = Depends(verify_token), job_data: Dict[str, Any] = Body(...)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 创建新任务
    new_job = {
        "id": len(mock_jobs) + 1,
        "name": job_data.get("name", "新建任务"),
        "func": job_data.get("func", "new_job"),
        "trigger": job_data.get("trigger", "interval"),
        "args": job_data.get("args", []),
        "kwargs": job_data.get("kwargs", {}),
        "next_run_time": "2025-04-24T17:00:00",
        "status": "running"
    }
    
    # 在实际应用中，这里会将新任务添加到数据库
    mock_jobs.append(new_job)
    
    return new_job

# 更新任务
@app.put("/api/v1/jobs/{job_id}")
async def update_job(job_id: int, token: str = Depends(verify_token), job_data: Dict[str, Any] = Body(...)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 查找任务
    for i, job in enumerate(mock_jobs):
        if job["id"] == job_id:
            # 更新任务
            updated_job = {**job, **job_data}
            mock_jobs[i] = updated_job
            return updated_job
    
    raise HTTPException(status_code=404, detail="任务不存在")

# 删除任务
@app.delete("/api/v1/jobs/{job_id}")
async def delete_job(job_id: int, token: str = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 查找任务
    for i, job in enumerate(mock_jobs):
        if job["id"] == job_id:
            # 删除任务
            del mock_jobs[i]
            return {"status": "success", "message": "任务已删除"}
    
    raise HTTPException(status_code=404, detail="任务不存在")

# 更新任务状态
@app.post("/api/v1/jobs/{job_id}/{action}")
async def update_job_status(job_id: int, action: str, token: str = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 检查操作是否有效
    valid_actions = ["pause", "resume", "run"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail="无效的操作")
    
    # 查找任务
    for i, job in enumerate(mock_jobs):
        if job["id"] == job_id:
            # 更新任务状态
            if action == "pause":
                mock_jobs[i]["status"] = "paused"
            elif action == "resume":
                mock_jobs[i]["status"] = "running"
            
            return {"status": "success", "message": f"任务已{action}"}
    
    raise HTTPException(status_code=404, detail="任务不存在")

# 获取日志列表
@app.get("/api/v1/logs")
async def get_logs(
    token: str = Depends(verify_token),
    limit: int = Query(10, description="每页数量"),
    offset: int = Query(0, description="偏移量"),
    job_id: Optional[int] = Query(None, description="任务ID"),
    status: Optional[str] = Query(None, description="日志状态")
):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 根据任务ID和状态过滤日志
    filtered_logs = mock_logs
    if job_id:
        filtered_logs = [log for log in mock_logs if log["job_id"] == job_id]
    if status:
        filtered_logs = [log for log in filtered_logs if log["status"] == status]
    
    # 分页
    paginated_logs = filtered_logs[offset:offset+limit]
    
    # 直接返回数组，而不是包含 items 和 total 的对象
    return paginated_logs

# 获取日志详情
@app.get("/api/v1/logs/{log_id}")
async def get_log(log_id: int, token: str = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 查找日志
    for log in mock_logs:
        if log["id"] == log_id:
            return log
    
    raise HTTPException(status_code=404, detail="日志不存在")

# 删除日志
@app.delete("/api/v1/logs/{log_id}")
async def delete_log(log_id: int, token: str = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 查找日志
    for i, log in enumerate(mock_logs):
        if log["id"] == log_id:
            # 删除日志
            del mock_logs[i]
            return {"status": "success", "message": "日志已删除"}
    
    raise HTTPException(status_code=404, detail="日志不存在")

# 删除任务的所有日志
@app.delete("/api/v1/logs/job/{job_id}")
async def delete_job_logs(job_id: int, token: str = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 删除任务的所有日志
    global mock_logs
    mock_logs = [log for log in mock_logs if log["job_id"] != job_id]
    
    return {"status": "success", "message": "任务日志已删除"}

# 获取系统设置
@app.get("/api/v1/settings")
async def get_settings(token: str = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    return {"settings": mock_settings}

# 更新系统设置
@app.put("/api/v1/settings")
async def update_settings(token: str = Depends(verify_token), settings_data: Dict[str, Any] = Body(...)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 更新设置
    global mock_settings
    mock_settings = {**mock_settings, **settings_data.get("settings", {})}
    
    return {"settings": mock_settings}

# 首页
@app.get("/")
async def root():
    return {"message": "APScheduler管理系统API服务"}
