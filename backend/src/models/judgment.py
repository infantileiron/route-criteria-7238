from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,Boolean
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class JudgmentMatrix(Base):
 __tablename__="judgment_matrices"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 name:Mapped[str]=mapped_column(String(160),unique=True)
 criteria_set_id:Mapped[str]=mapped_column(ForeignKey("criteria_sets.id"))
 matrix:Mapped[list]=mapped_column(JSON)
 cr_threshold:Mapped[float]=mapped_column(Double)
 perturbation:Mapped[float]=mapped_column(Double)
 created_at:Mapped[str]=mapped_column(String(64))
