from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# 数据库连接配置
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./apscheduler.db")

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 用户模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    jobs = relationship("Job", back_populates="user")

# 任务模型
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    func = Column(String)
    trigger = Column(String)
    args = Column(JSON, default=[])
    kwargs = Column(JSON, default={})
    next_run_time = Column(DateTime, nullable=True)
    status = Column(String, default="running")
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="jobs")
    logs = relationship("Log", back_populates="job")

# 日志模型
class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    status = Column(String)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    start_time = Column(DateTime)
    duration = Column(Float)
    
    job = relationship("Job", back_populates="logs")

# 系统设置模型
class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(JSON)

# 创建数据库表
def create_tables():
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库
def init_db():
    db = SessionLocal()
    try:
        # 检查是否已有用户
        user_count = db.query(User).count()
        if user_count == 0:
            # 创建默认管理员用户
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password="admin",  # 实际应用中应该使用加密密码
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # 创建示例任务
            test_job = Job(
                name="测试任务",
                func="test_job",
                trigger="interval",
                args=[],
                kwargs={},
                next_run_time=datetime.now(),
                status="running",
                user_id=admin_user.id
            )
            db.add(test_job)
            
            example_job = Job(
                name="示例任务",
                func="example_job",
                trigger="cron",
                args=[],
                kwargs={},
                next_run_time=datetime.now(),
                status="paused",
                user_id=admin_user.id
            )
            db.add(example_job)
            db.commit()
            
            # 创建示例日志
            success_log = Log(
                job_id=test_job.id,
                status="success",
                message="任务执行成功",
                created_at=datetime.now(),
                start_time=datetime.now(),
                duration=1.5
            )
            db.add(success_log)
            
            failed_log = Log(
                job_id=example_job.id,
                status="failed",
                message="任务执行失败",
                created_at=datetime.now(),
                start_time=datetime.now(),
                duration=0.8
            )
            db.add(failed_log)
            
            # 创建默认设置
            timezone_setting = Setting(
                key="timezone",
                value="Asia/Shanghai"
            )
            db.add(timezone_setting)
            
            grace_time_setting = Setting(
                key="job_misfire_grace_time",
                value=60
            )
            db.add(grace_time_setting)
            
            coalesce_setting = Setting(
                key="job_coalesce",
                value=True
            )
            db.add(coalesce_setting)
            
            max_instances_setting = Setting(
                key="job_max_instances",
                value=3
            )
            db.add(max_instances_setting)
            
            db.commit()
    finally:
        db.close()
