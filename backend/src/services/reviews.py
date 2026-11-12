import uuid
from fastapi import HTTPException
from src.models import ChoiceReview
from src.services.runs import require_completed
from src.utils.time import now
from src.utils.serialization import serialize
def create(db,payload,user):
 run=require_completed(db,payload.run_id)
 if payload.decision=="accepted" and run.result["ahp"]["cr_warning"] and not payload.accept_warning:raise HTTPException(422,"本次CR高于阈值，请明确确认已阅读一致性警告")
 item=ChoiceReview(id=str(uuid.uuid4()),created_at=now(),author=user["email"],**payload.model_dump());db.add(item);db.commit();return serialize(item)
