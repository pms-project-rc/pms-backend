"""
Integration tests for RegisterParkingEntryUseCase.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.application.parking.register_parking_entry import RegisterParkingEntryUseCase
from app.domain.parking.value_objects.vehicle_type import VehicleType


@pytest.mark.asyncio
class TestRegisterParkingEntryUseCase:
    """Test suite for RegisterParkingEntryUseCase."""
    
    async def test_successful_motorcycle_entry(self):
        """Test successful registration of a motorcycle with helmets."""
        # Mocks
        parking_repo = AsyncMock()
        vehicle_repo = AsyncMock()
        rate_repo = AsyncMock()
        
        # Setup mocks
        vehicle_repo.find_by_plate.return_value = None  # New vehicle
        vehicle_repo.create_vehicle.return_value = 1
        parking_repo.find_active_by_vehicle.return_value = None  # Not parked
        
        rate_repo.find_active_rate.return_value = {
            "id": 1,
            "vehicle_type": "MOTORCYCLE",
            "price": 2000,
            "helmet_fee": 100000
        }
        
        parking_repo.create_parking_entry.return_value = 100
        
        # Use case
        use_case = RegisterParkingEntryUseCase(
            parking_repo=parking_repo,
            vehicle_repo=vehicle_repo,
            rate_repo=rate_repo
        )
        
        # Execute
        result = await use_case.execute(
            plate="ABC123D",
            helmet_count=2,
            owner_name="Juan",
            owner_phone="123"
        )
        
        # Verify
        assert result["parking_id"] == 100
        assert result["vehicle_type"] == "MOTORCYCLE"
        assert result["helmet_count"] == 2
        assert result["helmet_charge"] == 200000  # 2 * 100000
        
        # Verify repository calls
        vehicle_repo.create_vehicle.assert_called_once()
        parking_repo.create_parking_entry.assert_called_once()
    
    async def test_duplicate_entry_prevention(self):
        """Test prevention of duplicate parking entries."""
        # Mocks
        parking_repo = AsyncMock()
        vehicle_repo = AsyncMock()
        rate_repo = AsyncMock()
        
        # Setup mocks
        vehicle_repo.find_by_plate.return_value = {"id": 1, "vehicle_type": "CAR"}
        parking_repo.find_active_by_vehicle.return_value = {"id": 99}  # Already parked
        
        # Use case
        use_case = RegisterParkingEntryUseCase(
            parking_repo=parking_repo,
            vehicle_repo=vehicle_repo,
            rate_repo=rate_repo
        )
        
        # Execute and expect error
        with pytest.raises(ValueError) as exc:
            await use_case.execute(plate="ABC123")
            
        assert "ya se encuentra en el parqueadero" in str(exc.value)
