from pydantic import BaseModel,Field,model_validator
import math
class Column(BaseModel):
 code:str=Field(min_length=1,max_length=30)
 label:str=Field(min_length=1,max_length=60)
 unit:str=Field(default="",max_length=30)
class Alternative(BaseModel):
 alternative_id:str=Field(min_length=1,max_length=60)
 name:str=Field(min_length=1,max_length=100)
 values:dict[str,float]
class DatasetInput(BaseModel):
 name:str=Field(min_length=2,max_length=120)
 source:str=Field(default="alternatives.json",max_length=120)
 columns:list[Column]=Field(min_length=3,max_length=6)
 alternatives:list[Alternative]=Field(min_length=2,max_length=1000)
 @model_validator(mode="after")
 def valid(self):
  codes={c.code for c in self.columns}
  if len(codes)!=len(self.columns):raise ValueError("指标代码不能重复")
  if len({a.alternative_id for a in self.alternatives})!=len(self.alternatives):raise ValueError("方案编号不能重复")
  for a in self.alternatives:
   if set(a.values)!=codes:raise ValueError("所有方案的指标集合须与列定义一致")
   if any(not math.isfinite(v) or abs(v)>1e12 for v in a.values.values()):raise ValueError("指标须为有限值且绝对值不超过10的12次方")
  return self
