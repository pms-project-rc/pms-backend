from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import date

from app.application.dto.subscriptions.subscription_dtos import SubscriptionRequest, SubscriptionResponse
from app.application.subscriptions.create_subscription_use_case import CreateSubscriptionUseCase
from app.application.subscriptions.check_active_subscription_use_case import CheckActiveSubscriptionUseCase
from app.infrastructure.repositories.subscriptions.subscription_repository_impl import SubscriptionRepositoryImpl
from app.infrastructure.repositories.parking.vehicle_repository_impl import VehicleRepositoryImpl
from app.api.dependencies.auth import get_current_operational_admin
from app.infrastructure.database.models.users import OperationalAdmin

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SubscriptionResponse)
async def create_subscription(
    request: SubscriptionRequest,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Create a new monthly subscription.
    """
    try:
        sub_repo = SubscriptionRepositoryImpl()
        vehicle_repo = VehicleRepositoryImpl()
        use_case = CreateSubscriptionUseCase(sub_repo, vehicle_repo)
        
        subscription = await use_case.execute(
            plate=request.plate,
            vehicle_type=request.vehicle_type,
            owner_name=request.owner_name,
            owner_phone=request.owner_phone,
            monthly_fee=request.monthly_fee,
            start_date=request.start_date,
            duration_days=request.duration_days,
            notes=request.notes
        )
        
        # Calculate days remaining
        days_remaining = (subscription.end_date - date.today()).days
        
        return SubscriptionResponse(
            id=subscription.id,
            vehicle_id=subscription.vehicle_id,
            plate=request.plate,
            start_date=subscription.start_date,
            end_date=subscription.end_date,
            monthly_fee=subscription.monthly_fee,
            payment_status=subscription.payment_status,
            days_remaining=max(0, days_remaining)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating subscription: {str(e)}"
        )

@router.get("/check/{plate}", response_model=SubscriptionResponse)
async def check_subscription(
    plate: str,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Check if a vehicle has an active subscription.
    """
    try:
        sub_repo = SubscriptionRepositoryImpl()
        vehicle_repo = VehicleRepositoryImpl()
        use_case = CheckActiveSubscriptionUseCase(sub_repo, vehicle_repo)
        
        subscription = await use_case.execute(plate)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active subscription found for vehicle {plate}"
            )
            
        days_remaining = (subscription.end_date - date.today()).days
        
        return SubscriptionResponse(
            id=subscription.id,
            vehicle_id=subscription.vehicle_id,
            plate=plate.upper(),
            start_date=subscription.start_date,
            end_date=subscription.end_date,
            monthly_fee=subscription.monthly_fee,
            payment_status=subscription.payment_status,
            days_remaining=max(0, days_remaining)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking subscription: {str(e)}"
        )

@router.get("/active", response_model=List[SubscriptionResponse])
async def list_active_subscriptions(
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    List all active subscriptions.
    """
    try:
        sub_repo = SubscriptionRepositoryImpl()
        vehicle_repo = VehicleRepositoryImpl()
        
        subscriptions = await sub_repo.list_active(date.today())
        
        response = []
        for sub in subscriptions:
            vehicle = await vehicle_repo.get_by_id(sub.vehicle_id)
            plate = vehicle.plate if vehicle else "UNKNOWN"
            days_remaining = (sub.end_date - date.today()).days
            
            response.append(SubscriptionResponse(
                id=sub.id,
                vehicle_id=sub.vehicle_id,
                plate=plate,
                start_date=sub.start_date,
                end_date=sub.end_date,
                monthly_fee=sub.monthly_fee,
                payment_status=sub.payment_status,
                days_remaining=max(0, days_remaining)
            ))
            
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing subscriptions: {str(e)}"
        )
