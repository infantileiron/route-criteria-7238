from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer
from src.models import DecisionRun
from src.schemas.run import RunInput
from src.services import runs as service
from src.utils.serialization import rows,serialize
router=APIRouter(prefix="/runs")
@router.get("")
def listing(db=Depends(db_session),user=Depends(current_user)):return rows(db.scalars(select(DecisionRun).order_by(DecisionRun.created_at.desc())))
@router.post("")
def create(payload:RunInput,db=Depends(db_session),user=Depends(writer)):return service.create(db,payload.judgment_id)
@router.get("/{id}")
def detail(id:str,db=Depends(db_session),user=Depends(current_user)):
 item=db.get(DecisionRun,id)
 if not item:raise HTTPException(404,"运行不存在")
 return serialize(item)
