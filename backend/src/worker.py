from pathlib import Path
import redis,traceback
from sqlalchemy import select
from src.config.settings import REDIS_URL
from src.config.database import Session
from src.models import DecisionRun,JudgmentMatrix,CriteriaSet,AlternativeDataset
from src.services.analysis import analyze
client=redis.Redis.from_url(REDIS_URL);heartbeat=Path("/artifacts/worker-heartbeat")
def execute(id):
 with Session() as db:
  run=db.get(DecisionRun,id)
  if not run or run.status not in ("queued","running"):return
  run.status="running";db.commit()
  try:
   judgment=db.get(JudgmentMatrix,run.judgment_id);criteria=db.get(CriteriaSet,judgment.criteria_set_id);dataset=db.get(AlternativeDataset,criteria.dataset_id)
   run.result=analyze(dataset,criteria,judgment);run.status="completed"
  except Exception as e:run.error=str(e);run.status="failed";traceback.print_exc()
  db.commit()
with Session() as db:
 for id in db.scalars(select(DecisionRun.id).where(DecisionRun.status.in_(["queued","running"]))):client.lpush("route-criteria:jobs",id)
while True:
 heartbeat.touch();job=client.brpop("route-criteria:jobs",timeout=1)
 if job:execute(job[1].decode())
