import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import CriteriaSet
from src.services.datasets import require
from src.utils.time import now
from src.utils.serialization import serialize
def create(db,payload):
 dataset=require(db,payload.dataset_id)
 if {c.code for c in payload.criteria}!={c["code"] for c in dataset.columns}:raise HTTPException(422,"指标方向集合必须与方案集指标完全相同")
 if db.scalar(select(CriteriaSet).where(CriteriaSet.name==payload.name)):raise HTTPException(409,"指标口径名称已存在")
 item=CriteriaSet(id=str(uuid.uuid4()),name=payload.name,dataset_id=payload.dataset_id,criteria=[c.model_dump() for c in payload.criteria],created_at=now());db.add(item);db.commit();return serialize(item)
