from pydantic import BaseModel,Field,model_validator
import math
class SupplementItem(BaseModel):
 alternative_id:str=Field(min_length=1,max_length=60)
 values:dict[str,float]
class SupplementInput(BaseModel):
 dataset_id:str=Field(min_length=1,max_length=80)
 base_version:int=Field(ge=1)
 idempotency_key:str=Field(min_length=8,max_length=120)
 items:list[SupplementItem]=Field(min_length=1,max_length=1000)
 @model_validator(mode="after")
 def valid(self):
  keys=[i.alternative_id for i in self.items]
  if len(keys)!=len(set(keys)):raise ValueError("同一批次中航段编号不能重复")
  for item in self.items:
   if any(not math.isfinite(v) or abs(v)>1e12 for v in item.values.values()):raise ValueError("补报指标须为有限值且绝对值不超过10的12次方")
  return self
