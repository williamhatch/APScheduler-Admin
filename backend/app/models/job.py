from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base


class Job(Base):
    """
    任务模型
    """
    name = Column(String(100), index=True, nullable=False, comment="任务名称")
    func = Column(String(255), nullable=False, comment="任务函数")
    args = Column(JSON, nullable=True, comment="任务参数")
    kwargs = Column(JSON, nullable=True, comment="任务关键字参数")
    trigger = Column(String(20), nullable=False, comment="触发器类型")
    trigger_args = Column(JSON, nullable=False, comment="触发器参数")
    max_instances = Column(Integer, default=1, comment="最大实例数")
    next_run_time = Column(DateTime, nullable=True, index=True, comment="下次运行时间")
    misfire_grace_time = Column(Integer, default=60, comment="错过执行时间的宽限期")
    coalesce = Column(Integer, default=0, comment="是否合并执行")
    status = Column(String(20), default="running", comment="任务状态")
    description = Column(Text, nullable=True, comment="任务描述")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(Integer, ForeignKey("user.id"), comment="创建者ID")
