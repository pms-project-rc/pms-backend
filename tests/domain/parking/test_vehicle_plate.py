"""
Unit tests for VehiclePlate value object.
"""
import pytest
from app.domain.parking.value_objects.vehicle_plate import VehiclePlate
from app.domain.parking.value_objects.vehicle_type import VehicleType


class TestVehiclePlate:
    """Test suite for VehiclePlate value object."""
    
    def test_valid_motorcycle_plate(self):
        """Test valid motorcycle plate (ends in letter)."""
        plate = VehiclePlate("ABC123D")
        assert plate.value == "ABC123D"
        assert plate.classified_vehicle_type == VehicleType.MOTORCYCLE
    
    def test_valid_car_plate(self):
        """Test valid car plate (ends in number)."""
        plate = VehiclePlate("ABC123")
        assert plate.value == "ABC123"
        assert plate.classified_vehicle_type == VehicleType.CAR
    
    def test_normalization(self):
        """Test plate normalization (spaces, lowercase)."""
        plate = VehiclePlate(" abc-123 ")
        assert plate.value == "ABC123"
        assert plate.classified_vehicle_type == VehicleType.CAR
        
        plate = VehiclePlate("xyz-789-a")
        assert plate.value == "XYZ789A"
        assert plate.classified_vehicle_type == VehicleType.MOTORCYCLE
    
    def test_invalid_plate_format(self):
        """Test invalid plate formats."""
        with pytest.raises(ValueError):
            VehiclePlate("")
            
        with pytest.raises(ValueError):
            VehiclePlate("A")
            
        with pytest.raises(ValueError):
            VehiclePlate("123456")  # Must start with letters
            
        with pytest.raises(ValueError):
            VehiclePlate("ABC-DEF")  # Must have numbers
