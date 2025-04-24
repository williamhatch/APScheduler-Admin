from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Float
from sqlalchemy.sql import func
from app.db.base_class import Base


class JobLog(Base):
    """
    任务日志模型
    """
    job_id = Column(Integer, ForeignKey("job.id"), nullable=False, index=True, comment="任务ID")
    status = Column(String(20), default="success", comment="执行状态")
    start_time = Column(DateTime, default=func.now(), comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    duration = Column(Float, nullable=True, comment="执行时长(秒)")
    error_message = Column(Text, nullable=True, comment="错误信息")
    output = Column(Text, nullable=True, comment="输出信息")
