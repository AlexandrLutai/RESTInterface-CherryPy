import unittest
from unittest.mock import MagicMock, patch
from Services.equipment_service import EquipmentService

class TestEquipmentService(unittest.TestCase):
    @patch("Services.equipment_service.EquipmentManager")
    def setUp(self, MockEquipmentManager):
        self.mock_manager = MockEquipmentManager.return_value
        self.service = EquipmentService(config={})
        self.service.manager = self.mock_manager

    def test_add_equipment_success(self):
        equipment_list = [{"serial_number": "123ABC", "note": "Test Note"}]
        self.mock_manager.add_equipment.return_value = (True, "Equipment added successfully")
        result = self.service.add_equipment(equipment_list)
        self.mock_manager.add_equipment.assert_called_once_with(equipment_list)
        self.assertEqual(result, (True, "Equipment added successfully"))

    def test_add_equipment_validation_error(self):
        equipment_list = [{"serial_number": "", "note": "Test Note"}]
        result = self.service.add_equipment(equipment_list)
        self.assertFalse(result[0])
        self.assertIn("Validation error", result[1])

    def test_get_all_equipment(self):
        self.mock_manager.get_all_equipment.return_value = [{"id": 1, "serial_number": "123ABC", "note": "Test Note"}]
        result = self.service.get_all_equipment(page=1, limit=10)
        self.mock_manager.get_all_equipment.assert_called_once_with(1, 10)
        self.assertEqual(result, [{"id": 1, "serial_number": "123ABC", "note": "Test Note"}])

    def test_get_equipment_by_id_success(self):
        self.mock_manager.get_equipment_by_id.return_value = {"id": 1, "serial_number": "123ABC", "note": "Test Note"}
        result = self.service.get_equipment_by_id(equipment_id=1)
        self.mock_manager.get_equipment_by_id.assert_called_once_with(1)
        self.assertEqual(result, {"id": 1, "serial_number": "123ABC", "note": "Test Note"})

    def test_get_equipment_by_id_not_found(self):
        self.mock_manager.get_equipment_by_id.return_value = None
        with self.assertRaises(ValueError):
            self.service.get_equipment_by_id(equipment_id=1)

    def test_update_equipment_success(self):
        self.mock_manager.update_equipment.return_value = (True, "Equipment updated successfully")
        result = self.service.update_equipment(equipment_id=1, data={"note": "Updated Note"})
        self.mock_manager.update_equipment.assert_called_once_with(1, {"note": "Updated Note"})
        self.assertEqual(result, (True, "Equipment updated successfully"))

    def test_update_equipment_no_data(self):
        result = self.service.update_equipment(equipment_id=1, data={})
        self.assertFalse(result[0])
        self.assertEqual(result[1], "No data provided for update.")

    def test_soft_delete_equipment_success(self):
        self.mock_manager.soft_delete_equipment.return_value = (True, "Equipment deleted successfully")
        result = self.service.soft_delete_equipment(equipment_id=1)
        self.mock_manager.soft_delete_equipment.assert_called_once_with(1)
        self.assertEqual(result, (True, "Equipment deleted successfully"))

    def test_get_all_equipment_types(self):
        self.mock_manager.get_all_equipment_types.return_value = [{"id": 1, "type": "Type A"}]
        result = self.service.get_all_equipment_types(page=1, limit=10)
        self.mock_manager.get_all_equipment_types.assert_called_once_with(1, 10)
        self.assertEqual(result, [{"id": 1, "type": "Type A"}])

if __name__ == "__main__":
    unittest.main()