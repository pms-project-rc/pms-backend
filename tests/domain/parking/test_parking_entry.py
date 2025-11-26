"""
Unit tests for ParkingEntry entity.
"""
import pytest
from datetime import datetime
from app.domain.parking.entities.parking_entry import ParkingEntry
from app.domain.parking.value_objects.vehicle_plate import VehiclePlate
from app.domain.parking.value_objects.vehicle_type import VehicleType


class TestParkingEntry:
    """Test suite for ParkingEntry entity."""
    
    def test_motorcycle_helmet_charge(self):
        """Test helmet charge calculation for motorcycles."""
        plate = VehiclePlate("ABC123D")  # Motorcycle
        entry = ParkingEntry(
            plate=plate,
            entry_time=datetime.now(),
            helmet_count=2,
            helmet_unit_price=100000
        )
        
        assert entry.vehicle_type == VehicleType.MOTORCYCLE
        assert entry.helmet_count == 2
        assert entry.helmet_charge == 200000  # 2 * 100000 cents
        assert entry.has_helmet_charge is True
    
    def test_car_no_helmet_charge(self):
        """Test cars cannot have helmet charges."""
        plate = VehiclePlate("ABC123")  # Car
        
        # Should raise error if trying to add helmets to car
        with pytest.raises(ValueError):
            ParkingEntry(
                plate=plate,
                entry_time=datetime.now(),
                helmet_count=1
            )
            
        # Valid car entry
        entry = ParkingEntry(
            plate=plate,
            entry_time=datetime.now(),
            helmet_count=0
        )
        
        assert entry.vehicle_type == VehicleType.CAR
        assert entry.helmet_count == 0
        assert entry.helmet_charge == 0
        assert entry.has_helmet_charge is False
    
    def test_helmet_count_validation(self):
        """Test helmet count validation limits."""
        plate = VehiclePlate("ABC123D")
        
        # Negative helmets
        with pytest.raises(ValueError):
            ParkingEntry(plate=plate, entry_time=datetime.now(), helmet_count=-1)
            
        # Too many helmets
        with pytest.raises(ValueError):
            ParkingEntry(plate=plate, entry_time=datetime.now(), helmet_count=4)
