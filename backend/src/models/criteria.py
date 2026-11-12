from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,Boolean
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class CriteriaSet(Base):
 __tablename__="criteria_sets"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 name:Mapped[str]=mapped_column(String(160),unique=True)
 dataset_id:Mapped[str]=mapped_column(ForeignKey("alternative_datasets.id"))
 criteria:Mapped[list]=mapped_column(JSON)
 created_at:Mapped[str]=mapped_column(String(64))
