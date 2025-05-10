import mysql.connector
from typing import Any, Optional, Union, Tuple, List, Dict
from Database.transaction_manager import TransactionManager
import logging

logger = logging.getLogger(__name__)

class QueryExecutor:
    """
    Класс для выполнения SQL-запросов.
    """

    def __init__(self, db_config: dict[str, Union[str, int]], pool_config: Optional[dict[str, Union[str, int]]] = None):
        """
        Инициализация QueryExecutor.

        :param transaction_manager: Экземпляр TransactionManager для управления транзакциями.
        """
        self.transaction_manager = TransactionManager(db_config, pool_config)

    def execute(
        self,
        query: str,
        params: Optional[Tuple[Any, ...]] = None,
        fetchone: bool = False,
        fetchall: bool = False,
        commit: bool = False
    ) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Выполняет SQL-запрос.

        :param query: SQL-запрос.
        :param params: Параметры для подстановки в запрос.
        :param fetchone: Если True, возвращает одну запись.
        :param fetchall: Если True, возвращает все записи.
        :param commit: Если True, фиксирует изменения в базе данных.
        :return: Результат запроса (если fetchone или fetchall указаны).
        """
        if not query:
            raise ValueError("Query cannot be empty.")

        with self.transaction_manager.transaction_context() as connection:
            with connection.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute(query, params)
                    result = None
                    if fetchone:
                        result = cursor.fetchone()
                    elif fetchall:
                        result = cursor.fetchall()

                    if commit:
                        connection.commit()

                    return result
                except mysql.connector.Error as e:
                    logger.error(f"Error executing query: {e}")
                    raise
