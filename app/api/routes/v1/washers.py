from fastapi import APIRouter, Depends, HTTPException

from app.application.dto.washers.washer_request import WasherCreateRequest, WasherUpdateRequest
from app.domain.washers.use_cases.create_washer import CreateWasher
from app.domain.washers.use_cases.delete_washer import DeleteWasher
from app.domain.washers.use_cases.get_washer import GetWasher
from app.domain.washers.use_cases.list_washers import ListWashers
from app.domain.washers.use_cases.update_washer import UpdateWasher
from app.infrastructure.washers.washer_repository_impl import WasherRepositoryImpl

router = APIRouter(prefix="/washers", tags=["Washers"])

def get_repo():
    return WasherRepositoryImpl()


@router.post("/")
async def create_washer(data: WasherCreateRequest, repo=Depends(get_repo)):
    uc = CreateWasher(repo)
    return await uc.execute(data)


@router.get("/")
async def list_washers(repo=Depends(get_repo)):
    uc = ListWashers(repo)
    return await uc.execute()


@router.get("/{washer_id}")
async def get_washer(washer_id: int, repo=Depends(get_repo)):
    uc = GetWasher(repo)
    washer = await uc.execute(washer_id)
    if not washer:
        raise HTTPException(status_code=404, detail="Washer not found")
    return washer


@router.put("/{washer_id}")
async def update_washer(washer_id: int, data: WasherUpdateRequest, repo=Depends(get_repo)):
    uc = UpdateWasher(repo)
    return await uc.execute(washer_id, data)


@router.delete("/{washer_id}")
async def delete_washer(washer_id: int, repo=Depends(get_repo)):
    uc = DeleteWasher(repo)
    await uc.execute(washer_id)
    return {"deleted": True}
