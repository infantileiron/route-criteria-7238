from sqlalchemy import String,Integer,JSON,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class MetricSupplement(Base):
 __tablename__="metric_supplements"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 idempotency_key:Mapped[str]=mapped_column(String(120),unique=True)
 dataset_id:Mapped[str]=mapped_column(String(80),index=True)
 base_version:Mapped[int]=mapped_column(Integer)
 items:Mapped[list]=mapped_column(JSON)
 content_fingerprint:Mapped[str]=mapped_column(String(64))
 status:Mapped[str]=mapped_column(String(20))
 dataset_version_id:Mapped[str]=mapped_column(String(80),default="")
 new_version:Mapped[int]=mapped_column(Integer,default=0)
 author:Mapped[str]=mapped_column(String(160),default="")
 created_at:Mapped[str]=mapped_column(String(64))
