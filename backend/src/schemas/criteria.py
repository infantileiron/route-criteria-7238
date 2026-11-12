from pydantic import BaseModel,Field,model_validator
from typing import Literal
class Criterion(BaseModel):
 code:str=Field(min_length=1,max_length=30)
 direction:Literal["cost","benefit"]
class CriteriaInput(BaseModel):
 name:str=Field(min_length=2,max_length=120)
 dataset_id:str
 criteria:list[Criterion]=Field(min_length=3,max_length=6)
 @model_validator(mode="after")
 def unique(self):
  if len({c.code for c in self.criteria})!=len(self.criteria):raise ValueError("指标不能重复")
  return self
