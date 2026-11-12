from sqlalchemy import String,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class DatasetVersion(Base):
 __tablename__="dataset_versions"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 dataset_id:Mapped[str]=mapped_column(ForeignKey("alternative_datasets.id"),index=True)
 version_no:Mapped[int]=mapped_column(Integer)
 alternatives:Mapped[list]=mapped_column(JSON)
 columns:Mapped[list]=mapped_column(JSON)
 change_note:Mapped[str]=mapped_column(Text,default="")
 supplement_id:Mapped[str]=mapped_column(String(80),default="")
 created_by:Mapped[str]=mapped_column(String(160),default="")
 created_at:Mapped[str]=mapped_column(String(64))
 __table_args__=(UniqueConstraint("dataset_id","version_no",name="uq_dataset_version_no"),)
