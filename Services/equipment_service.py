import logging
from typing import List, Dict, Tuple, Union
from pydantic import ValidationError
from Models.models import EquipmentListInput, EquipmentUpdateInput
from Database.equipment_manager import EquipmentManager
from Utils.decorators import log_and_handle_errors  # Импорт декоратора

# Настройка логгера
logger = logging.getLogger(__name__)


class EquipmentService:
    """
    Сервисный слой для управления оборудованием.
    """

    def __init__(self, config):
        """
        Инициализация сервиса оборудования.

        :param config: Конфигурация базы данных.
        """
        self.manager = EquipmentManager(config)
        logger.info("EquipmentService initialized with database configuration.")

    def _validate_pagination_params(self, page: int, limit: int):
        """
        Проверяет параметры пагинации на корректность.
        :param page: Номер страницы.
        :param limit: Лимит записей на странице.
        """
        if page < 1 or limit < 1:
            logger.error("Page and limit must be greater than 0.")
            raise ValueError("Page and limit must be greater than 0.")

    def _log_operation_result(self, operation: str, result: Union[Dict, List, Tuple]):
        """
        Логирует результат операции.
        :param operation: Название операции.
        :param result: Результат операции.
        """
        logger.info(f"{operation} result: {result}")

    @log_and_handle_errors("Adding equipment")
    def add_equipment(self, equipment_list: List[Dict[str, str]]) -> Tuple[bool, str]:
        """
        Добавляет несколько записей в таблицу equipment.

        :param equipment_list: Список словарей с серийными номерами и примечаниями.
        :return: Кортеж (True, сообщение) если добавление успешно, иначе (False, сообщение об ошибке).
        """
        logger.info(f"Adding equipment: {equipment_list}")
        if not equipment_list:
            logger.error("Equipment list is empty.")
            return False, "Equipment list is empty."

        try:
            validated_data = EquipmentListInput.parse_obj(equipment_list).root
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return False, "Validation error: Invalid input data."

        result = self.manager.add_equipment([item.dict() for item in validated_data])
        self._log_operation_result("Add equipment", result)
        return result

    @log_and_handle_errors("Fetching all equipment")
    def get_all_equipment(self, page: int, limit: int) -> List[Dict[str, Union[int, str]]]:
        """
        Получает список оборудования с пагинацией.

        :param page: Номер страницы (начиная с 1).
        :param limit: Лимит записей на странице.
        :return: Список словарей с данными оборудования.
        """
        logger.info(f"Fetching all equipment with page={page}, limit={limit}")
        self._validate_pagination_params(page, limit)
        result = self.manager.get_all_equipment(page, limit)
        self._log_operation_result("Fetch all equipment", result)
        return result

    @log_and_handle_errors("Fetching equipment by ID")
    def get_equipment_by_id(self, equipment_id: int) -> Dict[str, Union[int, str]]:
        """
        Получает запись оборудования по ID.

        :param equipment_id: ID оборудования.
        :return: Словарь с данными оборудования.
        """
        logger.info(f"Fetching equipment with id={equipment_id}")
        equipment = self.manager.get_equipment_by_id(equipment_id)
        if not equipment:
            logger.error(f"Equipment with ID {equipment_id} not found.")
            raise ValueError(f"Equipment with ID {equipment_id} not found.")
        self._log_operation_result("Fetch equipment by ID", equipment)
        return equipment

    @log_and_handle_errors("Updating equipment")
    def update_equipment(self, equipment_id: int, data: Dict[str, Union[int, str]]) -> Tuple[bool, str]:
        """
        Обновляет запись оборудования по ID.

        :param equipment_id: ID оборудования.
        :param data: Данные для обновления (ключи — названия столбцов).
        :return: Кортеж (True, сообщение) если обновление успешно, иначе (False, сообщение об ошибке).
        """
        logger.info(f"Updating equipment with id={equipment_id} and data={data}")
        if not data:
            logger.error("No data provided for update.")
            return False, "No data provided for update."

        try:
            validated_data = EquipmentUpdateInput.parse_obj(data)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return False, "Validation error: Invalid input data."

        result = self.manager.update_equipment(equipment_id, validated_data.dict(exclude_unset=True))
        self._log_operation_result("Update equipment", result)
        return result

    @log_and_handle_errors("Soft deleting equipment")
    def soft_delete_equipment(self, equipment_id: int) -> Tuple[bool, str]:
        """
        Мягко удаляет запись оборудования, устанавливая is_deleted = True.

        :param equipment_id: ID оборудования.
        :return: Кортеж (True, сообщение) если удаление успешно, иначе (False, сообщение об ошибке).
        """
        logger.info(f"Soft deleting equipment with id={equipment_id}")
        result = self.manager.soft_delete_equipment(equipment_id)
        self._log_operation_result("Soft delete equipment", result)
        return result

    @log_and_handle_errors("Fetching all equipment types")
    def get_all_equipment_types(self, page: int, limit: int) -> List[Dict[str, Union[int, str]]]:
        """
        Получает список всех типов оборудования с пагинацией.

        :param page: Номер страницы (начиная с 1).
        :param limit: Лимит записей на странице.
        :return: Список словарей с данными типов оборудования.
        """
        logger.info(f"Fetching all equipment types with page={page}, limit={limit}")
        self._validate_pagination_params(page, limit)
        result = self.manager.get_all_equipment_types(page, limit)
        self._log_operation_result("Fetch all equipment types", result)
        return result