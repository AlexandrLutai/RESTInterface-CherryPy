import logging
from typing import Dict, List, Union
import cherrypy
from Services.equipment_service import EquipmentService
from Utils.decorators import log_and_handle_errors 

logger = logging.getLogger(__name__)


class EquipmentController:
    """
    Контроллер для управления оборудованием и типами оборудования.
    Обрабатывает HTTP-запросы и взаимодействует с сервисным слоем.
    """

    def __init__(self, config):
        """
        Инициализация контроллера оборудования.

        :param config: Конфигурация базы данных.
        """
        self.service = EquipmentService(config)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.tools.auth() 
    @log_and_handle_errors("Handling equipment request")
    def equipment(self, id: int = None, page: int = 1, limit: int = 10, **kwargs):
        """
        Основной маршрут для управления оборудованием.

        Обрабатывает следующие HTTP-методы:
        - GET: Получение списка оборудования или конкретной записи по ID.
        - POST: Добавление нового оборудования.
        - PUT: Обновление существующего оборудования.
        - DELETE: Удаление оборудования.

        :param id: ID оборудования (для методов GET, PUT, DELETE).
        :param page: Номер страницы (для метода GET списка оборудования).
        :param limit: Лимит записей на странице (для метода GET списка оборудования).
        :param kwargs: Дополнительные параметры.
        :return: JSON-ответ с результатом операции.
        """
        method = cherrypy.request.method

        if method == 'GET':
            return self._handle_get_equipment(id, page, limit)
        elif method == 'POST':
            return self._handle_post_equipment()
        elif method == 'PUT':
            return self._handle_put_equipment(id)
        elif method == 'DELETE':
            return self._handle_delete_equipment(id)
        else:
            raise cherrypy.HTTPError(405, "Method not allowed.")

    @log_and_handle_errors("Handling GET equipment request")
    def _handle_get_equipment(self, id: int, page: int, limit: int):
        """
        Обрабатывает GET-запросы для оборудования.
        """
        try:
            if id:
                return self.service.get_equipment_by_id(int(id))
            return self.service.get_all_equipment(page, limit)
        except Exception as e:
            logger.error(f"Failed to retrieve equipment data: {e}")
            raise cherrypy.HTTPError(500, "Failed to retrieve equipment data.")

    @log_and_handle_errors("Handling POST equipment request")
    def _handle_post_equipment(self):
        """
        Обрабатывает POST-запросы для добавления оборудования.
        """
        input_data = cherrypy.request.json
        success, message = self.service.add_equipment(input_data)
        if not success:
            raise cherrypy.HTTPError(400, message)
        return {"success": success, "message": message}

    @log_and_handle_errors("Handling PUT equipment request")
    def _handle_put_equipment(self, id: int):
        """
        Обрабатывает PUT-запросы для обновления оборудования.
        """
        if not id:
            raise cherrypy.HTTPError(400, "ID is required for updating equipment.")
        input_data = cherrypy.request.json
        success, message = self.service.update_equipment(int(id), input_data)
        if not success:
            raise cherrypy.HTTPError(400, message)
        return {"success": success, "message": message}

    @log_and_handle_errors("Handling DELETE equipment request")
    def _handle_delete_equipment(self, id: int):
        """
        Обрабатывает DELETE-запросы для удаления оборудования.
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

        :param page: Номер страницы (начиная с 1).
        :param limit: Лимит записей на странице.
        :param kwargs: Дополнительные параметры.
        :return: Список типов оборудования в формате JSON.
        """
        return self.service.get_all_equipment_types(page, limit)


