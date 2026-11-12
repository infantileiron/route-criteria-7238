from pydantic import BaseModel,Field
class JudgmentInput(BaseModel):
 name:str=Field(min_length=2,max_length=120)
 criteria_set_id:str
 matrix:list[list[float]]
 cr_threshold:float=Field(default=.1,ge=.01,le=.5,allow_inf_nan=False)
 perturbation:float=Field(default=.1,ge=0,le=.5,allow_inf_nan=False)
