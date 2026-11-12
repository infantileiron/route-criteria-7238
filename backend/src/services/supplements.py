import copy,uuid,hashlib,json
from fastapi import HTTPException
from sqlalchemy import select
from src.models import AlternativeDataset,DatasetVersion,MetricSupplement
from src.utils.time import now
from src.utils.serialization import serialize
def latest_version(db,dataset_id):
 return db.scalar(select(DatasetVersion).where(DatasetVersion.dataset_id==dataset_id).order_by(DatasetVersion.version_no.desc()))
def require_dataset(db,dataset_id):
 item=db.get(AlternativeDataset,dataset_id)
 if not item:raise HTTPException(404,"方案集不存在")
 return item
def fingerprint(dataset_id,base_version,items):
 payload={"dataset_id":dataset_id,"base_version":base_version,"items":sorted(({"alternative_id":i.alternative_id,"values":dict(sorted(i.values.items()))} for i in items),key=lambda x:x["alternative_id"])}
 return hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def validate_batch(dataset,base_items,payload):
 known={a["alternative_id"] for a in base_items};codes={c["code"] for c in dataset.columns};errors=[];seen=set()
 for item in payload.items:
  if item.alternative_id in seen:errors.append(f"航段{item.alternative_id}在批次内重复")
  seen.add(item.alternative_id)
  if item.alternative_id not in known:errors.append(f"未知航段编号：{item.alternative_id}")
  missing=codes-set(item.values)
  unknown=set(item.values)-codes
  if missing:errors.append(f"航段{item.alternative_id}缺失指标：{''.join(sorted(missing))}")
  if unknown:errors.append(f"航段{item.alternative_id}存在未定义指标：{''.join(sorted(unknown))}")
 if errors:raise HTTPException(422,"补报整批未生效："+"；".join(errors))
def submit(db,payload,user):
 dataset=require_dataset(db,payload.dataset_id)
 existing=db.scalar(select(MetricSupplement).where(MetricSupplement.idempotency_key==payload.idempotency_key))
 if existing:
  if existing.status!="accepted":raise HTTPException(409,"该幂等键对应批次未受理，不能复用")
  if existing.dataset_id!=payload.dataset_id:raise HTTPException(409,"幂等键已用于其他方案集")
  return {"replayed":True,"supplement":serialize(existing),"dataset_version":serialize(db.get(DatasetVersion,existing.dataset_version_id))}
 current=latest_version(db,payload.dataset_id)
 if not current:raise HTTPException(409,"方案集尚无任何版本快照，无法补报")
 fp=fingerprint(payload.dataset_id,payload.base_version,payload.items)
 # 幂等回放优先于过期判断：原样重发（含旧base_version）只回放，不新增版本
 twin=db.scalar(select(MetricSupplement).where(MetricSupplement.dataset_id==payload.dataset_id,MetricSupplement.content_fingerprint==fp,MetricSupplement.status=="accepted"))
 if twin:
  return {"replayed":True,"supplement":serialize(twin),"dataset_version":serialize(db.get(DatasetVersion,twin.dataset_version_id))}
 # 整批内容校验（未知航段/缺失指标/未定义指标），保证整批原子不生效
 validate_batch(dataset,current.alternatives,payload)
 # 乐观并发：基于过期版本的补报拒绝受理，无任何写入
 if current.version_no!=payload.base_version:
  raise HTTPException(409,f"补报基于过期版本v{payload.base_version}，当前最新为v{current.version_no}，请基于最新版本重新提交")
 merged=copy.deepcopy(current.alternatives);patches={i.alternative_id:i.values for i in payload.items}
 for row in merged:
  if row["alternative_id"] in patches:row["values"]=dict(patches[row["alternative_id"]])
 # 补报值与当前版本完全相同（例如同内容换键重投）时不产生空版本
 if merged==current.alternatives:
  return {"replayed":True,"supplement":serialize(twin) if twin else None,"dataset_version":serialize(current)}
 new_no=current.version_no+1
 version=DatasetVersion(id=str(uuid.uuid4()),dataset_id=dataset.id,version_no=new_no,alternatives=merged,columns=copy.deepcopy(dataset.columns),change_note=f"按航段批量补报指标，基于v{current.version_no}生成v{new_no}",supplement_id="",created_by=user["email"],created_at=now())
 supplement=MetricSupplement(id=str(uuid.uuid4()),idempotency_key=payload.idempotency_key,dataset_id=dataset.id,base_version=payload.base_version,items=[i.model_dump() for i in payload.items],content_fingerprint=fp,status="accepted",dataset_version_id="",new_version=new_no,author=user["email"],created_at=now())
 version.supplement_id=supplement.id;supplement.dataset_version_id=version.id
 dataset.alternatives=merged;dataset.current_version=new_no
 db.add(version);db.add(supplement);db.commit()
 return {"replayed":False,"supplement":serialize(supplement),"dataset_version":serialize(version)}
def list_versions(db,dataset_id):
 require_dataset(db,dataset_id)
 return [serialize(v) for v in db.scalars(select(DatasetVersion).where(DatasetVersion.dataset_id==dataset_id).order_by(DatasetVersion.version_no.desc()))]
def get_version(db,dataset_id,version_no):
 require_dataset(db,dataset_id)
 version=db.scalar(select(DatasetVersion).where(DatasetVersion.dataset_id==dataset_id,DatasetVersion.version_no==version_no))
 if not version:raise HTTPException(404,"该方案版本不存在")
 return serialize(version)
def list_supplements(db,dataset_id):
 require_dataset(db,dataset_id)
 return [serialize(s) for s in db.scalars(select(MetricSupplement).where(MetricSupplement.dataset_id==dataset_id).order_by(MetricSupplement.created_at.desc()))]
def initial_snapshot(db,dataset,author="system"):
 version=DatasetVersion(id=str(uuid.uuid4()),dataset_id=dataset.id,version_no=1,alternatives=copy.deepcopy(dataset.alternatives),columns=copy.deepcopy(dataset.columns),change_note="方案集导入，建立v1基线快照",supplement_id="",created_by=author,created_at=now())
 dataset.current_version=1;db.add(version);db.flush();return version
