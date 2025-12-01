from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.application.dto.parking.rate_dtos import RateRequest, RateResponse
from app.application.parking.manage_rates_use_case import ManageRatesUseCase
from app.infrastructure.repositories.parking.rate_repository_impl import RateRepositoryImpl
from app.api.dependencies.auth import get_current_global_admin
from app.infrastructure.database.models.users import GlobalAdmin

router = APIRouter(prefix="/rates", tags=["Rates"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RateResponse)
async def create_rate(
    request: RateRequest,
    current_admin: GlobalAdmin = Depends(get_current_global_admin)
):
    """
    Create a new parking rate. Only Global Admin.
    """
    try:
        rate_repo = RateRepositoryImpl()
        use_case = ManageRatesUseCase(rate_repo)
        
        rate = await use_case.create_rate(
            vehicle_type=request.vehicle_type,
            rate_type=request.rate_type,
            price=request.price,
            description=request.description,
            is_active=request.is_active
        )
        
        return RateResponse(
            id=rate.id,
            vehicle_type=rate.vehicle_type,
            rate_type=rate.rate_type,
            price=rate.price,
            description=rate.description,
            is_active=rate.is_active
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating rate: {str(e)}"
        )

@router.get("/", response_model=List[RateResponse])
async def list_rates(
    current_admin: GlobalAdmin = Depends(get_current_global_admin)
):
    """
    List all active rates.
    """
    try:
        rate_repo = RateRepositoryImpl()
        use_case = ManageRatesUseCase(rate_repo)
        
        rates = await use_case.list_rates()
        
        return [
            RateResponse(
                id=r.id,
                vehicle_type=r.vehicle_type,
                rate_type=r.rate_type,
                price=r.price,
                description=r.description,
                is_active=r.is_active
            )
            for r in rates
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing rates: {str(e)}"
        )

@router.put("/{rate_id}", response_model=RateResponse)
async def update_rate(
    rate_id: int,
    request: RateRequest,
    current_admin: GlobalAdmin = Depends(get_current_global_admin)
):
    """
    Update an existing rate. Only Global Admin.
    """
    try:
        rate_repo = RateRepositoryImpl()
        use_case = ManageRatesUseCase(rate_repo)
        
        rate = await use_case.update_rate(
            rate_id=rate_id,
            vehicle_type=request.vehicle_type,
            rate_type=request.rate_type,
            price=request.price,
            description=request.description,
            is_active=request.is_active
        )
        
        return RateResponse(
            id=rate.id,
            vehicle_type=rate.vehicle_type,
            rate_type=rate.rate_type,
            price=rate.price,
            description=rate.description,
            is_active=rate.is_active
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating rate: {str(e)}"
        )

@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rate(
    rate_id: int,
    current_admin: GlobalAdmin = Depends(get_current_global_admin)
):
    """
    Delete a rate. Only Global Admin.
    """
    try:
        rate_repo = RateRepositoryImpl()
        use_case = ManageRatesUseCase(rate_repo)
        
        await use_case.delete_rate(rate_id)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting rate: {str(e)}"
        )
