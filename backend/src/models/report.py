from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,Boolean
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class Report(Base):
 __tablename__="decision_reports"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 run_id:Mapped[str]=mapped_column(ForeignKey("decision_runs.id"),unique=True)
 title:Mapped[str]=mapped_column(String(160))
 published_by:Mapped[str]=mapped_column(String(160))
 created_at:Mapped[str]=mapped_column(String(64))
