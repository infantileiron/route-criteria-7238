import uuid,csv,io
from sqlalchemy import select
from fastapi import HTTPException
from src.models import Report,ChoiceReview
from src.services.runs import require_completed
from src.utils.time import now
from src.utils.serialization import serialize
from src.utils.csv import safe_cell
def create(db,payload,user):
 require_completed(db,payload.run_id)
 review=db.scalar(select(ChoiceReview).where(ChoiceReview.run_id==payload.run_id).order_by(ChoiceReview.created_at.desc()))
 if not review or review.decision!="accepted":raise HTTPException(409,"最新复核须为接受后才能归档")
 if db.scalar(select(Report).where(Report.run_id==payload.run_id)):raise HTTPException(409,"本次运行已归档")
 item=Report(id=str(uuid.uuid4()),published_by=user["email"],created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
def export(db,id):
 report=db.get(Report,id)
 if not report:raise HTTPException(404,"报告不存在")
 result=require_completed(db,report.run_id).result;buf=io.StringIO();fields=["alternative_id","name","rank","score","d_plus","d_minus","min_rank","max_rank","cr","ranking_available","reason"]
 writer=csv.DictWriter(buf,fields);writer.writeheader()
 for a in result["alternatives"]:writer.writerow({**{k:safe_cell(a[k]) for k in fields[:8]},"cr":result["ahp"]["cr"],"ranking_available":result["topsis"]["available"],"reason":result["topsis"]["reason"]})
 return "\ufeff"+buf.getvalue()
