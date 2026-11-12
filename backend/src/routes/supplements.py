from fastapi import APIRouter,Depends
from src.config.database import db_session
from src.controllers.auth import current_user,writer
from src.schemas.supplement import SupplementInput
from src.services import supplements as service
router=APIRouter(prefix="/datasets")
@router.post("/supplements")
def submit(payload:SupplementInput,db=Depends(db_session),user=Depends(writer)):return service.submit(db,payload,user)
@router.get("/{dataset_id}/versions")
def versions(dataset_id:str,db=Depends(db_session),user=Depends(current_user)):return service.list_versions(db,dataset_id)
@router.get("/{dataset_id}/versions/{version_no}")
def version_detail(dataset_id:str,version_no:int,db=Depends(db_session),user=Depends(current_user)):return service.get_version(db,dataset_id,version_no)
@router.get("/{dataset_id}/supplements")
def supplements(dataset_id:str,db=Depends(db_session),user=Depends(current_user)):return service.list_supplements(db,dataset_id)
