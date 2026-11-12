import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import AlternativeDataset
from src.utils.time import now
from src.utils.serialization import serialize
def create(db,payload):
 if db.scalar(select(AlternativeDataset).where(AlternativeDataset.name==payload.name)):raise HTTPException(409,"方案集名称已存在")
 item=AlternativeDataset(id=str(uuid.uuid4()),name=payload.name,source=payload.source,columns=[c.model_dump() for c in payload.columns],alternatives=[a.model_dump() for a in payload.alternatives],created_at=now());db.add(item);db.commit();return serialize(item)
def require(db,id):
 item=db.get(AlternativeDataset,id)
 if not item:raise HTTPException(404,"方案集不存在")
 return item
