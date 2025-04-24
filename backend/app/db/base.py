# 导入所有模型，以便Alembic可以创建迁移
from app.db.base_class import Base
from app.models.user import User
from app.models.job import Job
from app.models.job_log import JobLog
