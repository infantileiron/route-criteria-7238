import random,json
from sqlalchemy import select,func
from src.config.database import Base,engine,Session
from src.models import User,AlternativeDataset,DatasetVersion,MetricSupplement,CriteriaSet,JudgmentMatrix,DecisionRun,ChoiceReview,Report
from src.services.analysis import analyze
from src.services.supplements import initial_snapshot
from src.utils.security import hash_password
from src.utils.time import now
def seed():
 Base.metadata.create_all(engine)
 with Session() as db:
  for role in ("admin","analyst","viewer"):
   if not db.get(User,role):db.add(User(id=role,email=role+"@yanzhou.demo",password=hash_password("Route2026!"),role=role))
  columns=[{"code":"cost","label":"模拟费用","unit":"万元"},{"code":"hours","label":"时长","unit":"小时"},{"code":"punctuality","label":"准班率","unit":"%"},{"code":"capacity","label":"可用舱位","unit":"TEU"}]
  rng=random.Random(2304);alternatives=[]
  for i in range(12):alternatives.append({"alternative_id":f"YZ-{i+1:02}","name":f"模拟备选航段 {chr(65+i)}","values":{"cost":round(rng.uniform(18,42),2),"hours":round(rng.uniform(18,40),2),"punctuality":round(rng.uniform(82,98),2),"capacity":rng.randint(80,220)}})
  criteria=[{"code":c["code"],"direction":"cost" if i<2 else "benefit"} for i,c in enumerate(columns)]
  if not db.get(AlternativeDataset,"demo-data"):db.add(AlternativeDataset(id="demo-data",name="岩舟航册·12条模拟备选航段",source="yanzhou_alternatives_202611.json",columns=columns,alternatives=alternatives,current_version=1,created_at=now()));db.flush()
  dataset=db.get(AlternativeDataset,"demo-data")
  if not db.scalar(select(DatasetVersion).where(DatasetVersion.dataset_id=="demo-data",DatasetVersion.version_no==1)):
   initial_snapshot(db,dataset,author="seed2304");db.flush()
  snapshot=db.scalar(select(DatasetVersion).where(DatasetVersion.dataset_id=="demo-data",DatasetVersion.version_no==1))
  if not db.get(CriteriaSet,"demo-criteria"):db.add(CriteriaSet(id="demo-criteria",name="费用与时长成本 / 准班与舱位收益",dataset_id="demo-data",criteria=criteria,created_at=now()));db.flush()
  weights=[.35,.25,.25,.15];matrix=[[a/b for b in weights] for a in weights]
  if not db.get(JudgmentMatrix,"demo-matrix"):db.add(JudgmentMatrix(id="demo-matrix",name="一致性基线·4指标成对判断",criteria_set_id="demo-criteria",matrix=matrix,cr_threshold=.1,perturbation=.1,created_at=now()));db.flush()
  bad=[[1,9,1/9,3],[1/9,1,9,2],[9,1/9,1,2],[1/3,1/2,1/2,1]]
  if not db.get(JudgmentMatrix,"warning-matrix"):db.add(JudgmentMatrix(id="warning-matrix",name="循环矛盾·保留原值警告示例",criteria_set_id="demo-criteria",matrix=bad,cr_threshold=.1,perturbation=.1,created_at=now()));db.flush()
  if not db.get(DecisionRun,"demo-run"):db.add(DecisionRun(id="demo-run",judgment_id="demo-matrix",dataset_version_id=snapshot.id,status="completed",result=analyze(snapshot,db.get(CriteriaSet,"demo-criteria"),db.get(JudgmentMatrix,"demo-matrix")),error="",created_at=now()));db.flush()
  old_run=db.get(DecisionRun,"demo-run")
  if old_run and not old_run.dataset_version_id:old_run.dataset_version_id=snapshot.id
  if not db.get(ChoiceReview,"demo-review"):db.add(ChoiceReview(id="demo-review",run_id="demo-run",note="已核对成本/收益方向、原矩阵与CR。权重扰动仅为单因素情景，模拟航段排名不能作为实际航行指令。",decision="accepted",accept_warning=False,author="analyst@yanzhou.demo",created_at=now()));db.flush()
  if not db.get(Report,"demo-report"):db.add(Report(id="demo-report",run_id="demo-run",title="岩舟模拟航段·多指标权衡复核",published_by="admin@yanzhou.demo",created_at=now()))
  db.commit();return {m.__tablename__:db.scalar(select(func.count()).select_from(m)) for m in (User,AlternativeDataset,DatasetVersion,MetricSupplement,CriteriaSet,JudgmentMatrix,DecisionRun,ChoiceReview,Report)}
if __name__=="__main__":print(json.dumps(seed(),ensure_ascii=False))
