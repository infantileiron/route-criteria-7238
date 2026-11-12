from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,Boolean
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class ChoiceReview(Base):
 __tablename__="choice_reviews"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 run_id:Mapped[str]=mapped_column(ForeignKey("decision_runs.id"))
 note:Mapped[str]=mapped_column(Text)
 decision:Mapped[str]=mapped_column(String(30))
 accept_warning:Mapped[bool]=mapped_column(Boolean)
 author:Mapped[str]=mapped_column(String(160))
 created_at:Mapped[str]=mapped_column(String(64))
