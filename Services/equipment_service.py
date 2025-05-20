import logging
import re
from typing import List, Dict, Tuple, Union, Optional
from pydantic import ValidationError
from Models.models import EquipmentListInput, EquipmentUpdateInput
from Database.query_executor import QueryExecutor
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
        self.db = QueryExecutor(config)
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

    @log_and_handle_errors("Paginating query")
    def _paginate_query(self, query: str, page: int, limit: int, params: Optional[Tuple] = ()) -> List[Dict[str, Union[int, str]]]:
        """
        Выполняет запрос с пагинацией.

        :param query: SQL-запрос.
        :param page: Номер страницы (начиная с 1).
        :param limit: Лимит записей на странице.
        :param params: Дополнительные параметры для SQL-запроса.
        :return: Список записей.
        """
        if page < 1:
            logger.error("Page number must be 1 or greater")
            raise ValueError("Page number must be 1 or greater")
        
        offset = limit * (page - 1)
        paginated_query = f"{query} LIMIT %s OFFSET %s"
        return self.db.execute(paginated_query, params + (limit, offset), fetchall=True)

    @log_and_handle_errors("Fetching all equipment types")
    def get_all_equipment_types(self, page: int, limit: int) -> List[Dict[str, Union[int, str]]]:
        """
        Получение списка всех типов оборудования с пагинацией.

        :param page: Номер страницы (начиная с 1).
        :param limit: Лимит записей на странице.
        :return: Список типов оборудования.
        """
        query = "SELECT id, name, serial_mask FROM equipment_type"
        return self._paginate_query(query, page, limit)

    @log_and_handle_errors("Validating serial number")
    def _validate_and_get_type_id(self, serial_number: str) -> Tuple[bool, Union[int, str]]:
        """
        Валидация серийного номера и получение type_id.

        :param serial_number: Серийный номер для проверки.
        :return: Кортеж (True, type_id) при успешной валидации, иначе (False, сообщение об ошибке).
        """
        # Получаем все маски и id типов оборудования
        query = "SELECT id, serial_mask FROM equipment_type"
        types = self.db.execute(query, fetchall=True)
        for t in types:
            serial_mask = t["serial_mask"]
            # Преобразуем маску в регулярное выражение
            mask_regex = serial_mask \
                .replace('N', '[0-9]') \
                .replace('A', '[A-Z]') \
                .replace('a', '[a-z]') \
                .replace('X', '[A-Z0-9]') \
                .replace('Z', '[-_@]')
            if re.fullmatch(mask_regex, serial_number):
                return True, t["id"]
        return False, f"Serial number '{serial_number}' does not match any mask"

    @log_and_handle_errors("Adding equipment")
    def add_equipment(self, equipment_list: List[Dict[str, str]]) -> Tuple[bool, str]:
        """
        Добавление нового оборудования в базу данных.

        :param equipment_list: Список словарей с данными оборудования.
        :return: Кортеж (True, сообщение) при успешном добавлении, иначе (False, сообщение об ошибке).
        """
        errors = []
        success_count = 0

        with self.db.transaction_manager.transaction_context() as connection:
            for equipment in equipment_list:
                try:
                    validated_data = EquipmentListInput.parse_obj(equipment).root
                except ValidationError as e:
                    errors.append(f"Validation error: {e}")
                    continue

                type_id = getattr(validated_data, "type_id", None)
                serial_number = getattr(validated_data, "serial_number", None)
                note = getattr(validated_data, "note", "")

                if type_id is None or serial_number is None:
                    errors.append("type_id and serial_number are required fields.")
                    continue

                # Валидация серийного номера по маске типа оборудования
                is_valid, msg = self._validate_serial_by_type(type_id, serial_number)
                if not is_valid:
                    errors.append(msg)
                    continue

                # Проверка уникальности связки type_id + serial_number
                if not self._is_unique_equipment(type_id, serial_number):
                    errors.append(f"Serial number '{serial_number}' already exists for type_id {type_id}")
                    continue

                # Добавление записи
                insert_query = "INSERT INTO equipment (type_id, serial_number, note, is_deleted) VALUES (%s, %s, %s, %s)"
                connection.cursor().execute(insert_query, (type_id, serial_number, note, False))
                success_count += 1

        if errors and success_count == 0:
            return False, f"All records failed to add: {', '.join(errors)}"
        elif errors:
            return True, f"Added {success_count} equipment(s), but some records failed: {', '.join(errors)}"
        else:
            return True, "All equipment records added successfully"

    @log_and_handle_errors("Fetching all equipment")
    def get_all_equipment(
        self,
        page: int,
        limit: int,
        filters: Optional[Dict[str, Union[str, int]]] = None
    ) -> List[Dict[str, Union[int, str]]]:
        """
        Получение списка оборудования с пагинацией и поиском по фильтрам.

        :param page: Номер страницы (начиная с 1).
        :param limit: Лимит записей на странице.
        :param filters: Словарь с фильтрами (type_id, serial_number, note).
        :return: Список оборудования.
        """
        base_query = "SELECT id, type_id, serial_number, note, is_deleted FROM equipment WHERE is_deleted = 0"
        params = []

        if filters:
            if "type_id" in filters:
                base_query += " AND type_id = %s"
                params.append(filters["type_id"])
            if "serial_number" in filters:
                base_query += " AND serial_number LIKE %s"
                params.append(f"%{filters['serial_number']}%")
            if "note" in filters:
                base_query += " AND note LIKE %s"
                params.append(f"%{filters['note']}%")

        return self._paginate_query(base_query, page, limit, tuple(params))

    @log_and_handle_errors("Fetching equipment by ID")
    def get_equipment_by_id(self, equipment_id: int) -> Optional[Dict[str, Union[int, str]]]:
        """
        Получение оборудования по ID.

        :param equipment_id: ID оборудования.
        :return: Словарь с данными оборудования или None, если запись не найдена.
        """
        query = "SELECT id, type_id, serial_number, note, is_deleted FROM equipment WHERE id = %s"
        return self.db.execute(query, (equipment_id,), fetchone=True)

    @log_and_handle_errors("Checking if equipment exists")
    def _check_equipment_exists(self, equipment_id: int, check_deleted: bool = False) -> bool:
        """
        Проверяет, существует ли запись оборудования в базе данных.

        :param equipment_id: ID оборудования.
        :param check_deleted: Если True, проверяет, что запись помечена как удалённая.
        :return: True, если запись существует (и соответствует параметру check_deleted), иначе False.
        """
        query = "SELECT id FROM equipment WHERE id = %s AND is_deleted = %s"
        result = self.db.execute(query, (equipment_id, check_deleted), fetchone=True)
        return bool(result)

    @log_and_handle_errors("Updating equipment")
    def update_equipment(self, equipment_id: int, data: Dict[str, Union[int, str]]) -> Tuple[bool, str]:
        """
        Обновление данных оборудования по ID с валидацией.

        :param equipment_id: ID оборудования.
        :param data: Словарь с данными для обновления.
        :return: Кортеж (True, сообщение) при успешном обновлении.
        """
        if not self._check_equipment_exists(equipment_id, check_deleted=False):
            logger.error(f"Equipment with ID '{equipment_id}' does not exist or has been deleted.")
            return False, f"Equipment with ID '{equipment_id}' does not exist or has been deleted."

        # Получаем текущие значения type_id и serial_number
        current = self.db.execute(
            "SELECT type_id, serial_number FROM equipment WHERE id = %s", (equipment_id,), fetchone=True
        )
        if not current:
            return False, f"Equipment with ID '{equipment_id}' not found."

        # Определяем новые значения для проверки
        new_type_id = data.get("type_id", current["type_id"])
        new_serial_number = data.get("serial_number", current["serial_number"])

        # Валидация серийного номера по маске типа оборудования
        is_valid, msg = self._validate_serial_by_type(new_type_id, new_serial_number)
        if not is_valid:
            return False, msg

        # Проверка уникальности связки type_id + serial_number (исключая текущую запись)
        if not self._is_unique_equipment(new_type_id, new_serial_number, exclude_id=equipment_id):
            return False, f"Serial number '{new_serial_number}' already exists for type_id {new_type_id}"

        # Формируем запрос на обновление только разрешённых полей
        allowed_fields = {"type_id", "serial_number", "note"}
        update_fields = {k: v for k, v in data.items() if k in allowed_fields}
        if not update_fields:
            return False, "No valid fields to update."

        set_clause = ", ".join([f"{key} = %s" for key in update_fields.keys()])
        query = f"UPDATE equipment SET {set_clause} WHERE id = %s"
        params = tuple(update_fields.values()) + (equipment_id,)
        self.db.execute(query, params, commit=True)

        return True, f"Equipment with ID '{equipment_id}' updated successfully"

    @log_and_handle_errors("Soft deleting equipment")
    def soft_delete_equipment(self, equipment_id: int) -> Tuple[bool, str]:
        """
        Мягкое удаление оборудования (установка is_deleted = True).

        :param equipment_id: ID оборудования.
        :return: Кортеж (True, сообщение) при успешном удалении.
        """
        if not self._check_equipment_exists(equipment_id, check_deleted=False):
            logger.error(f"Equipment with ID '{equipment_id}' does not exist or has been deleted.")
            return False, f"Equipment with ID '{equipment_id}' does not exist или has been deleted."

        query = "UPDATE equipment SET is_deleted = %s WHERE id = %s"
        self.db.execute(query, (True, equipment_id), commit=True)

        return True, f"Equipment with ID '{equipment_id}' soft deleted successfully"

    def _validate_serial_by_type(self, type_id: int, serial_number: str) -> Tuple[bool, str]:
        """
        Валидация серийного номера по маске типа оборудования.

        :param type_id: ID типа оборудования.
        :param serial_number: Серийный номер.
        :return: (True, '') если валидно, иначе (False, сообщение об ошибке).
        """
        mask_result = self.db.execute(
            "SELECT serial_mask FROM equipment_type WHERE id = %s", (type_id,), fetchone=True
        )
        if not mask_result:
            return False, f"type_id '{type_id}' does not exist"
        serial_mask = mask_result["serial_mask"]
        mask_regex = serial_mask \
            .replace('N', '[0-9]') \
            .replace('A', '[A-Z]') \
            .replace('a', '[a-z]') \
            .replace('X', '[A-Z0-9]') \
            .replace('Z', '[-_@]')
        if not re.fullmatch(mask_regex, serial_number):
            return False, f"Serial number '{serial_number}' does not match mask '{serial_mask}' for type_id {type_id}"
        return True, ""

    def _is_unique_equipment(self, type_id: int, serial_number: str, exclude_id: Optional[int] = None) -> bool:
        """
        Проверяет уникальность связки type_id + serial_number.

        :param type_id: ID типа оборудования.
        :param serial_number: Серийный номер.
        :param exclude_id: Исключить этот ID из проверки (для обновления).
        :return: True, если уникально, иначе False.
        """
        query = "SELECT id FROM equipment WHERE type_id = %s AND serial_number = %s AND is_deleted = 0"
        params = [type_id, serial_number]
        if exclude_id:
            query += " AND id != %s"
            params.append(exclude_id)
        result = self.db.execute(query, tuple(params), fetchone=True)
        return result is None