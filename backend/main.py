from fastapi import FastAPI, Form, HTTPException, Depends, Header, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
from datetime import datetime

from database import get_db, User, Job, Log, Setting, create_tables, init_db

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

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    create_tables()
    init_db()

# 验证token
def verify_token(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        # 在实际应用中，这里应该验证JWT token
        return token
    return None

# 登录API - 支持JSON格式
@app.post("/api/v1/auth/login")
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    print(f"登录尝试: {login_data.username}, {login_data.password}")
    # 只允许用户名为admin，密码为admin的用户登录
    user = db.query(User).filter(User.username == login_data.username).first()
    if user and user.hashed_password == login_data.password:  # 实际应用中应该验证加密密码
        # 生成token，这里简化处理
        token = "mock_token"
        return {
            "access_token": token, 
            "token_type": "bearer", 
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser
            }
        }
    raise HTTPException(status_code=401, detail="用户名或密码错误")

# 登录API - 支持Form格式（保留兼容性）
@app.post("/api/v1/auth/login-form")
async def login_form(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    print(f"Form登录尝试: {username}, {password}")
    user = db.query(User).filter(User.username == username).first()
    if user and user.hashed_password == password:  # 实际应用中应该验证加密密码
        # 生成token，这里简化处理
        token = "mock_token"
        return {
            "access_token": token, 
            "token_type": "bearer", 
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser
            }
        }
    raise HTTPException(status_code=401, detail="用户名或密码错误")

# 获取用户信息
@app.get("/api/v1/users/me")
async def get_user_info(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    # 在实际应用中，应该从token中获取用户ID
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser
    }

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
    status: Optional[str] = Query(None, description="任务状态"),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 构建查询
    query = db.query(Job)
    
    # 根据状态过滤任务
    if status:
        query = query.filter(Job.status == status)
    
    # 获取总数
    total = query.count()
    
    # 分页
    jobs = query.offset(offset).limit(limit).all()
    
    # 转换为字典列表
    job_list = []
    for job in jobs:
        job_dict = {
            "id": job.id,
            "name": job.name,
            "func": job.func,
            "trigger": job.trigger,
            "args": job.args,
            "kwargs": job.kwargs,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "status": job.status
        }
        job_list.append(job_dict)
    
    # 直接返回数组
    return job_list

# 获取任务详情
@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: int, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 查找任务
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 转换为字典
    job_dict = {
        "id": job.id,
        "name": job.name,
        "func": job.func,
        "trigger": job.trigger,
        "args": job.args,
        "kwargs": job.kwargs,
        "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
        "status": job.status
    }
    
    return job_dict

# 创建任务
@app.post("/api/v1/jobs")
async def create_job(token: str = Depends(verify_token), job_data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 创建新任务
    new_job = Job(
        name=job_data.get("name", "新建任务"),
        func=job_data.get("func", "new_job"),
        trigger=job_data.get("trigger", "interval"),
        args=job_data.get("args", []),
        kwargs=job_data.get("kwargs", {}),
        next_run_time=datetime.now(),
        status="running",
        user_id=1  # 在实际应用中，应该从token中获取用户ID
    )
    
    # 添加到数据库
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    # 转换为字典
    job_dict = {
        "id": new_job.id,
        "name": new_job.name,
        "func": new_job.func,
        "trigger": new_job.trigger,
        "args": new_job.args,
        "kwargs": new_job.kwargs,
        "next_run_time": new_job.next_run_time.isoformat() if new_job.next_run_time else None,
        "status": new_job.status
    }
    
    return job_dict

# 更新任务
@app.put("/api/v1/jobs/{job_id}")
async def update_job(job_id: int, token: str = Depends(verify_token), job_data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 查找任务
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 更新任务
    if "name" in job_data:
        job.name = job_data["name"]
    if "func" in job_data:
        job.func = job_data["func"]
    if "trigger" in job_data:
        job.trigger = job_data["trigger"]
    if "args" in job_data:
        job.args = job_data["args"]
    if "kwargs" in job_data:
        job.kwargs = job_data["kwargs"]
    if "status" in job_data:
        job.status = job_data["status"]
    
    # 保存到数据库
    db.commit()
    db.refresh(job)
    
    # 转换为字典
    job_dict = {
        "id": job.id,
        "name": job.name,
        "func": job.func,
        "trigger": job.trigger,
        "args": job.args,
        "kwargs": job.kwargs,
        "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
        "status": job.status
    }
    
    return job_dict

# 删除任务
@app.delete("/api/v1/jobs/{job_id}")
async def delete_job(job_id: int, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 查找任务
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 删除任务
    db.delete(job)
    db.commit()
    
    return {"status": "success", "message": "任务已删除"}

# 更新任务状态
@app.post("/api/v1/jobs/{job_id}/{action}")
async def update_job_status(job_id: int, action: str, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 检查操作是否有效
    valid_actions = ["pause", "resume", "run"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail="无效的操作")
    
    # 查找任务
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 更新任务状态
    if action == "pause":
        job.status = "paused"
    elif action == "resume":
        job.status = "running"
    
    # 保存到数据库
    db.commit()
    
    return {"status": "success", "message": f"任务已{action}"}

# 获取日志列表
@app.get("/api/v1/logs")
async def get_logs(
    token: str = Depends(verify_token),
    limit: int = Query(10, description="每页数量"),
    offset: int = Query(0, description="偏移量"),
    job_id: Optional[int] = Query(None, description="任务ID"),
    status: Optional[str] = Query(None, description="日志状态"),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 构建查询
    query = db.query(Log)
    
    # 根据任务ID和状态过滤日志
    if job_id:
        query = query.filter(Log.job_id == job_id)
    if status:
        query = query.filter(Log.status == status)
    
    # 获取总数
    total = query.count()
    
    # 分页
    logs = query.offset(offset).limit(limit).all()
    
    # 转换为字典列表
    log_list = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "job_id": log.job_id,
            "status": log.status,
            "message": log.message,
            "created_at": log.created_at.isoformat(),
            "start_time": log.start_time.isoformat() if log.start_time else None,
            "duration": log.duration
        }
        log_list.append(log_dict)
    
    # 直接返回数组
    return log_list

# 获取日志详情
@app.get("/api/v1/logs/{log_id}")
async def get_log(log_id: int, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 查找日志
    log = db.query(Log).filter(Log.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    # 转换为字典
    log_dict = {
        "id": log.id,
        "job_id": log.job_id,
        "status": log.status,
        "message": log.message,
        "created_at": log.created_at.isoformat(),
        "start_time": log.start_time.isoformat() if log.start_time else None,
        "duration": log.duration
    }
    
    return log_dict

# 删除日志
@app.delete("/api/v1/logs/{log_id}")
async def delete_log(log_id: int, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 查找日志
    log = db.query(Log).filter(Log.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    # 删除日志
    db.delete(log)
    db.commit()
    
    return {"status": "success", "message": "日志已删除"}

# 删除任务的所有日志
@app.delete("/api/v1/logs/job/{job_id}")
async def delete_job_logs(job_id: int, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 删除任务的所有日志
    db.query(Log).filter(Log.job_id == job_id).delete()
    db.commit()
    
    return {"status": "success", "message": "任务日志已删除"}

# 获取系统设置
@app.get("/api/v1/settings")
async def get_settings(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 获取所有设置
    settings = db.query(Setting).all()
    
    # 转换为字典
    settings_dict = {}
    for setting in settings:
        settings_dict[setting.key] = setting.value
    
    return {"settings": settings_dict}

# 更新系统设置
@app.put("/api/v1/settings")
async def update_settings(token: str = Depends(verify_token), settings_data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 更新设置
    for key, value in settings_data.get("settings", {}).items():
        # 查找设置
        setting = db.query(Setting).filter(Setting.key == key).first()
        if setting:
            # 更新设置
            setting.value = value
        else:
            # 创建新设置
            new_setting = Setting(key=key, value=value)
            db.add(new_setting)
    
    # 保存到数据库
    db.commit()
    
    # 获取更新后的设置
    settings = db.query(Setting).all()
    
    # 转换为字典
    settings_dict = {}
    for setting in settings:
        settings_dict[setting.key] = setting.value
    
    return {"settings": settings_dict}

# 获取用户列表
@app.get("/api/v1/users")
async def get_users(
    token: str = Depends(verify_token),
    limit: int = Query(10, description="每页数量"),
    skip: int = Query(0, description="偏移量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 构建查询
    query = db.query(User)
    
    # 根据搜索关键词过滤用户
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) | 
            (User.email.ilike(f"%{search}%"))
        )
    
    # 获取总数
    total = query.count()
    
    # 分页
    users = query.offset(skip).limit(limit).all()
    
    # 转换为字典列表
    user_list = []
    for user in users:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser
        }
        user_list.append(user_dict)
    
    # 直接返回数组
    return user_list

# 获取用户详情
@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: int, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 转换为字典
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser
    }
    
    return user_dict

# 创建用户
@app.post("/api/v1/users")
async def create_user(token: str = Depends(verify_token), user_data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 检查用户是否已存在
    existing_user = db.query(User).filter(User.username == user_data.get("username")).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建新用户
    new_user = User(
        username=user_data.get("username", ""),
        email=user_data.get("email", ""),
        hashed_password=user_data.get("password", ""),  # 实际应用中应该加密密码
        is_active=user_data.get("is_active", True),
        is_superuser=user_data.get("is_superuser", False)
    )
    
    # 添加到数据库
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 转换为字典
    user_dict = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "is_active": new_user.is_active,
        "is_superuser": new_user.is_superuser
    }
    
    return user_dict

# 更新用户
@app.put("/api/v1/users/{user_id}")
async def update_user(user_id: int, token: str = Depends(verify_token), user_data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户信息
    if "username" in user_data:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400, detail="用户名已存在")
        user.username = user_data["username"]
    
    if "email" in user_data:
        user.email = user_data["email"]
    
    if "password" in user_data:
        user.hashed_password = user_data["password"]  # 实际应用中应该加密密码
    
    if "is_active" in user_data:
        user.is_active = user_data["is_active"]
    
    if "is_superuser" in user_data:
        user.is_superuser = user_data["is_superuser"]
    
    # 保存到数据库
    db.commit()
    db.refresh(user)
    
    # 转换为字典
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser
    }
    
    return user_dict

# 删除用户
@app.delete("/api/v1/users/{user_id}")
async def delete_user(user_id: int, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 删除用户
    db.delete(user)
    db.commit()
    
    return {"status": "success", "message": "用户已删除"}

# 首页
@app.get("/")
async def root():
    return {"message": "APScheduler管理系统API服务"}
