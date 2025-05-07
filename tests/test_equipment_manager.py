import unittest
from unittest.mock import MagicMock, patch
from Database.equipment_manager import EquipmentManager

class TestEquipmentManager(unittest.TestCase):
    @patch("Database.equipment_manager.DatabaseBase")
    def setUp(self, MockDatabaseBase):
        self.mock_db = MockDatabaseBase.return_value
        mock_config = {
            "user": "mock_user",
            "password": "mock_password",
            "host": "mock_host",
            "database": "mock_db"
        }
        self.manager = EquipmentManager(config=mock_config)

    def test_get_all_equipment_types(self):
        self.mock_db.execute.return_value = [{"id": 1, "name": "Type1", "serial_mask": "XXX"}]
        result = self.manager.get_all_equipment_types(page=1, limit=10)
        self.mock_db.execute.assert_called_once_with(
            "SELECT id, name, serial_mask FROM equipment_type LIMIT %s OFFSET %s", (10, 0), fetchall=True
        )
        self.assertEqual(result, [{"id": 1, "name": "Type1", "serial_mask": "XXX"}])

    def test_add_equipment_success(self):
        equipment_list = [{"serial_number": "123ABC", "note": "Test Note"}]
        self.manager._validate_and_get_type_id = MagicMock(return_value=(True, 1))
        self.mock_db.begin_transaction.return_value.__enter__.return_value.cursor.return_value = MagicMock()
        result = self.manager.add_equipment(equipment_list)
        self.assertTrue(result[0])
        self.mock_db.begin_transaction.return_value.__enter__.return_value.cursor.return_value.execute.assert_called_once()

    def test_add_equipment_validation_error(self):
        equipment_list = [{"serial_number": "123ABC", "note": "Test Note"}]
        self.manager._validate_and_get_type_id = MagicMock(return_value=(False, "Invalid serial number"))
        result = self.manager.add_equipment(equipment_list)
        self.assertFalse(result[0])
        self.assertIn("Invalid serial number", result[1])

if __name__ == "__main__":
    unittest.main()