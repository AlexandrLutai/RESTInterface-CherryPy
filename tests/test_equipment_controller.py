import unittest
from unittest.mock import MagicMock, patch
import cherrypy
from Controllers.equipment_controller import EquipmentController

class TestEquipmentController(unittest.TestCase):
    def setUp(self):
        self.mock_service = MagicMock()
        self.controller = EquipmentController(config={})
        self.controller.service = self.mock_service

    @patch("cherrypy.request")
    def test_get_equipment_by_id(self, mock_request):
        mock_request.method = "GET"
        self.mock_service.get_equipment_by_id.return_value = {"id": 1, "name": "Test Equipment"}
        response = self.controller._handle_get_equipment(id=1, page=1, limit=10)
        self.mock_service.get_equipment_by_id.assert_called_once_with(1)
        self.assertEqual(response, {"id": 1, "name": "Test Equipment"})

    @patch("cherrypy.request")
    def test_get_all_equipment(self, mock_request):
        mock_request.method = "GET"
        self.mock_service.get_all_equipment.return_value = [{"id": 1, "name": "Test Equipment"}]
        response = self.controller._handle_get_equipment(id=None, page=1, limit=10)
        self.mock_service.get_all_equipment.assert_called_once_with(1, 10)
        self.assertEqual(response, [{"id": 1, "name": "Test Equipment"}])

    @patch("cherrypy.request")
    def test_post_equipment(self, mock_request):
        mock_request.method = "POST"
        mock_request.json = {"name": "New Equipment"}
        self.mock_service.add_equipment.return_value = (True, "Equipment added successfully")
        response = self.controller._handle_post_equipment()
        self.mock_service.add_equipment.assert_called_once_with({"name": "New Equipment"})
        self.assertEqual(response, {"success": True, "message": "Equipment added successfully"})

    @patch("cherrypy.request")
    def test_put_equipment(self, mock_request):
        mock_request.method = "PUT"
        mock_request.json = {"name": "Updated Equipment"}
        self.mock_service.update_equipment.return_value = (True, "Equipment updated successfully")
        response = self.controller._handle_put_equipment(id=1)
        self.mock_service.update_equipment.assert_called_once_with(1, {"name": "Updated Equipment"})
        self.assertEqual(response, {"success": True, "message": "Equipment updated successfully"})

    @patch("cherrypy.request")
    def test_delete_equipment(self, mock_request):
        mock_request.method = "DELETE"
        self.mock_service.soft_delete_equipment.return_value = (True, "Equipment deleted successfully")
        response = self.controller._handle_delete_equipment(id=1)
        self.mock_service.soft_delete_equipment.assert_called_once_with(1)
        self.assertEqual(response, {"success": True, "message": "Equipment deleted successfully"})

    @patch("cherrypy.request")
    def test_get_equipment_type(self, mock_request):
        mock_request.method = "GET"
        self.mock_service.get_all_equipment_types.return_value = [{"id": 1, "type": "Type A"}]
        response = self.controller.equipment_type(page=1, limit=10)
        self.mock_service.get_all_equipment_types.assert_called_once_with(1, 10)
        self.assertEqual(response, [{"id": 1, "type": "Type A"}])

if __name__ == "__main__":
    unittest.main()