from pathlib import Path
import redis,traceback
from sqlalchemy import select
from src.config.settings import REDIS_URL
from src.config.database import Session
from src.models import DecisionRun,JudgmentMatrix,CriteriaSet,DatasetVersion
from src.services.analysis import analyze
client=redis.Redis.from_url(REDIS_URL);heartbeat=Path("/artifacts/worker-heartbeat")
def execute(id):
 with Session() as db:
  run=db.get(DecisionRun,id)
  if not run or run.status not in ("queued","running"):return
  run.status="running";db.commit()
  try:
   judgment=db.get(JudgmentMatrix,run.judgment_id);criteria=db.get(CriteriaSet,judgment.criteria_set_id)
   snapshot=db.get(DatasetVersion,run.dataset_version_id)
   if not snapshot:raise ValueError("运行所钉住的方案版本快照已不存在，无法按发起时版本还原")
   run.result=analyze(snapshot,criteria,judgment);run.status="completed"
  except Exception as e:run.error=str(e);run.status="failed";traceback.print_exc()
  db.commit()
with Session() as db:
 for id in db.scalars(select(DecisionRun.id).where(DecisionRun.status.in_(["queued","running"]))):client.lpush("route-criteria:jobs",id)
while True:
 heartbeat.touch();job=client.brpop("route-criteria:jobs",timeout=1)
 if job:execute(job[1].decode())
