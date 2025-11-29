from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.infrastructure.repositories.washers.washer_repository_impl import WasherRepositoryImpl
from app.application.washers.services.create_washer import CreateWasher
from app.application.washers.services.get_washer import GetWasher
from app.application.washers.services.list_washers import ListWashers
from app.application.washers.services.update_washer import UpdateWasher
from app.application.washers.services.delete_washer import DeleteWasher
from app.application.washers.services.update_all_washers_commission import UpdateAllWashersCommission
from app.application.dto.washers.washer_request import WasherCreateRequest, WasherUpdateRequest, WasherBulkUpdateCommissionRequest
from app.application.dto.washers.washer_response import WasherResponse

router = APIRouter(prefix="/washers", tags=["Washers"])

def get_repo():
    return WasherRepositoryImpl()


@router.post("/update-commission-all")
async def update_all_commission(data: WasherBulkUpdateCommissionRequest, repo=Depends(get_repo)):
    uc = UpdateAllWashersCommission(repo)
    await uc.execute(data.percentage)
    return {"message": "All washers updated successfully", "percentage": data.percentage}


@router.post("/", response_model=WasherResponse)
async def create_washer(data: WasherCreateRequest, repo=Depends(get_repo)):

    uc = CreateWasher(repo)
    return await uc.execute(data)


@router.get("/", response_model=List[WasherResponse])
async def list_washers(repo=Depends(get_repo)):
    uc = ListWashers(repo)
    return await uc.execute()


@router.get("/{washer_id}", response_model=WasherResponse)
async def get_washer(washer_id: int, repo=Depends(get_repo)):
    uc = GetWasher(repo)
    washer = await uc.execute(washer_id)
    if not washer:
        raise HTTPException(status_code=404, detail="Washer not found")
    return washer


@router.put("/{washer_id}", response_model=WasherResponse)
async def update_washer(washer_id: int, data: WasherUpdateRequest, repo=Depends(get_repo)):
    uc = UpdateWasher(repo)
    return await uc.execute(washer_id, data)


@router.delete("/{washer_id}")
async def delete_washer(washer_id: int, repo=Depends(get_repo)):
    uc = DeleteWasher(repo)
    await uc.execute(washer_id)
    return {"deleted": True}
