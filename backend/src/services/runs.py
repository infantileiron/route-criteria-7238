import uuid,redis
from fastapi import HTTPException
from sqlalchemy import select
from src.models import DecisionRun,JudgmentMatrix,CriteriaSet
from src.services.supplements import latest_version
from src.config.settings import REDIS_URL
from src.utils.time import now
from src.utils.serialization import serialize
def create(db,judgment_id):
 judgment=db.get(JudgmentMatrix,judgment_id)
 if not judgment:raise HTTPException(404,"判断矩阵不存在")
 criteria=db.get(CriteriaSet,judgment.criteria_set_id)
 snapshot=latest_version(db,criteria.dataset_id)
 if not snapshot:raise HTTPException(409,"方案集尚无版本快照，无法计算")
 item=DecisionRun(id=str(uuid.uuid4()),judgment_id=judgment_id,dataset_version_id=snapshot.id,status="queued",result={},error="",created_at=now());db.add(item);db.commit()
 try:redis.Redis.from_url(REDIS_URL).lpush("route-criteria:jobs",item.id)
 except redis.RedisError:
  item.status="failed";item.error="后台队列不可用，请重试";db.commit();raise HTTPException(503,item.error)
 return serialize(item)
def require_completed(db,id):
 item=db.get(DecisionRun,id)
 if not item:raise HTTPException(404,"运行不存在")
 if item.status!="completed":raise HTTPException(409,"计算尚未完成")
 return item
