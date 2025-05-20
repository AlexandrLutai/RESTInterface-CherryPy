import unittest
from unittest.mock import MagicMock, patch
from Services.equipment_service import EquipmentService

class TestEquipmentService(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.service = EquipmentService(config={})
        self.service.db = self.mock_db

    def test_add_equipment_success(self):
        # Мокаем методы валидации и уникальности
        self.service._validate_serial_by_type = MagicMock(return_value=(True, ""))
        self.service._is_unique_equipment = MagicMock(return_value=True)
        self.mock_db.transaction_manager.transaction_context.return_value.__enter__.return_value = self.mock_db

        equipment_list = [{"type_id": 1, "serial_number": "NAAZXX", "note": "Test Note"}]
        cursor_mock = MagicMock()
        self.mock_db.cursor.return_value = cursor_mock

        result = self.service.add_equipment(equipment_list)
        self.assertTrue(result[0])
        self.assertIn("added", result[1].lower())

    def test_add_equipment_validation_error(self):
        self.service._validate_serial_by_type = MagicMock(return_value=(False, "Validation error"))
        self.service._is_unique_equipment = MagicMock(return_value=True)
        self.mock_db.transaction_manager.transaction_context.return_value.__enter__.return_value = self.mock_db

        equipment_list = [{"type_id": 1, "serial_number": "WRONG", "note": "Test Note"}]
        result = self.service.add_equipment(equipment_list)
        self.assertFalse(result[0])
        self.assertIn("validation error", result[1].lower())

    def test_add_equipment_duplicate(self):
        self.service._validate_serial_by_type = MagicMock(return_value=(True, ""))
        self.service._is_unique_equipment = MagicMock(return_value=False)
        self.mock_db.transaction_manager.transaction_context.return_value.__enter__.return_value = self.mock_db

        equipment_list = [{"type_id": 1, "serial_number": "NAAZXX", "note": "Test Note"}]
        result = self.service.add_equipment(equipment_list)
        self.assertFalse(result[0])
        self.assertIn("already exists", result[1].lower())

    def test_get_all_equipment(self):
        self.mock_db.execute.return_value = [{"id": 1, "type_id": 1, "serial_number": "NAAZXX", "note": "Test Note"}]
        result = self.service.get_all_equipment(page=1, limit=10)
        self.assertIsInstance(result, list)
        self.mock_db.execute.assert_called()

    def test_get_equipment_by_id_success(self):
        self.mock_db.execute.return_value = {"id": 1, "type_id": 1, "serial_number": "NAAZXX", "note": "Test Note"}
        result = self.service.get_equipment_by_id(equipment_id=1)
        self.assertEqual(result["id"], 1)

    def test_get_equipment_by_id_not_found(self):
        self.mock_db.execute.return_value = None
        result = self.service.get_equipment_by_id(equipment_id=1)
        self.assertIsNone(result)

    def test_update_equipment_success(self):
        self.service._check_equipment_exists = MagicMock(return_value=True)
        self.mock_db.execute.side_effect = [
            {"type_id": 1, "serial_number": "NAAZXX"},  # current
            None,  # _is_unique_equipment
            None   # update
        ]
        self.service._validate_serial_by_type = MagicMock(return_value=(True, ""))
        self.service._is_unique_equipment = MagicMock(return_value=True)

        result = self.service.update_equipment(equipment_id=1, data={"type_id": 1, "serial_number": "NAAZXX"})
        self.assertTrue(result[0])
        self.assertIn("updated", result[1].lower())

    def test_update_equipment_validation_error(self):
        self.service._check_equipment_exists = MagicMock(return_value=True)
        self.mock_db.execute.side_effect = [
            {"type_id": 1, "serial_number": "NAAZXX"},  # current
        ]
        self.service._validate_serial_by_type = MagicMock(return_value=(False, "Validation error"))
        result = self.service.update_equipment(equipment_id=1, data={"type_id": 1, "serial_number": "BAD"})
        self.assertFalse(result[0])
        self.assertIn("validation error", result[1].lower())

    def test_update_equipment_duplicate(self):
        self.service._check_equipment_exists = MagicMock(return_value=True)
        self.mock_db.execute.side_effect = [
            {"type_id": 1, "serial_number": "NAAZXX"},  # current
        ]
        self.service._validate_serial_by_type = MagicMock(return_value=(True, ""))
        self.service._is_unique_equipment = MagicMock(return_value=False)
        result = self.service.update_equipment(equipment_id=1, data={"type_id": 1, "serial_number": "NAAZXX"})
        self.assertFalse(result[0])
        self.assertIn("already exists", result[1].lower())

    def test_soft_delete_equipment_success(self):
        self.service._check_equipment_exists = MagicMock(return_value=True)
        self.mock_db.execute.return_value = None
        result = self.service.soft_delete_equipment(equipment_id=1)
        self.assertTrue(result[0])
        self.assertIn("soft deleted", result[1].lower())

    def test_get_all_equipment_types(self):
        self.mock_db.execute.return_value = [{"id": 1, "name": "Type A", "serial_mask": "NAAZXX"}]
        result = self.service.get_all_equipment_types(page=1, limit=10)
        self.assertIsInstance(result, list)
        self.mock_db.execute.assert_called()

if __name__ == "__main__":
    unittest.main()