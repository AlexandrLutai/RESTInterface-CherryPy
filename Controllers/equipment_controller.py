import logging
from typing import Dict, List, Union
import cherrypy
from Services.equipment_service import EquipmentService
from Utils.decorators import log_and_handle_errors 

logger = logging.getLogger(__name__)


@cherrypy.expose
class EquipmentController:
    """
    Контроллер для управления оборудованием и типами оборудования.
    Использует MethodDispatcher для маршрутизации HTTP-методов.
    """

    def __init__(self, config):
        self.service = EquipmentService(config)

    @cherrypy.tools.json_out()
    @cherrypy.tools.auth()
    @log_and_handle_errors("Handling GET equipment request")
    def GET(self, id: int = None, page: int = 1, limit: int = 10, **kwargs):
        """
        Получение списка оборудования или конкретной записи по ID.
        """
        if id:
            return self.service.get_equipment_by_id(int(id))
        # Формируем фильтры из query-параметров
        filters = {}
        for key in ("type_id", "serial_number", "note"):
            value = kwargs.get(key)
            if value is not None:
                filters[key] = value
        return self.service.get_all_equipment(int(page), int(limit), filters)

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.tools.auth()
    @log_and_handle_errors("Handling POST equipment request")
    def POST(self, **kwargs):
        """
        Добавление нового оборудования.
        """
        input_data = cherrypy.request.json
        success, message = self.service.add_equipment(input_data)
        if not success:
            raise cherrypy.HTTPError(400, message)
        return {"success": success, "message": message}

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.tools.auth()
    @log_and_handle_errors("Handling PUT equipment request")
    def PUT(self, id: int = None, **kwargs):
        """
        Обновление существующего оборудования.
        """
        if not id:
            raise cherrypy.HTTPError(400, "ID is required for updating equipment.")
        input_data = cherrypy.request.json
        success, message = self.service.update_equipment(int(id), input_data)
        if not success:
            raise cherrypy.HTTPError(400, message)
        return {"success": success, "message": message}

    @cherrypy.tools.json_out()
    @cherrypy.tools.auth()
    @log_and_handle_errors("Handling DELETE equipment request")
    def DELETE(self, id: int = None, **kwargs):
        """
        Удаление оборудования.
        """
        if not id:
            raise cherrypy.HTTPError(400, "ID is required for deleting equipment.")
        success, message = self.service.soft_delete_equipment(int(id))
        if not success:
            raise cherrypy.HTTPError(400, message)
        return {"success": success, "message": message}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=['GET'])
    @log_and_handle_errors("Handling GET equipment types request")
    def equipment_type(self, page: int = 1, limit: int = 10, **kwargs) -> List[Dict[str, Union[int, str]]]:
        """
        GET /api/equipment-type - Получение списка типов оборудования.
        """
        return self.service.get_all_equipment_types(int(page), int(limit))


