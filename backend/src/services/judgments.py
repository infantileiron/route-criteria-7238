import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import JudgmentMatrix,CriteriaSet
from src.services.ahp import validate_matrix
from src.utils.time import now
from src.utils.serialization import serialize
def create(db,payload):
 criteria=db.get(CriteriaSet,payload.criteria_set_id)
 if not criteria:raise HTTPException(404,"指标口径不存在")
 try:validate_matrix(payload.matrix,len(criteria.criteria))
 except (ValueError,ZeroDivisionError) as e:raise HTTPException(422,str(e))
 if db.scalar(select(JudgmentMatrix).where(JudgmentMatrix.name==payload.name)):raise HTTPException(409,"判断矩阵名称已存在")
 item=JudgmentMatrix(id=str(uuid.uuid4()),created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
