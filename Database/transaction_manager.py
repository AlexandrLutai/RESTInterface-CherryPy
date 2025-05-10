import mysql.connector
from contextlib import contextmanager
from mysql.connector.connection import MySQLConnection
from Database.connection_pool_manager import ConnectionPoolManager
import logging
from typing import Any, Optional
logger = logging.getLogger(__name__)

class TransactionManager:
    """
    Класс для управления транзакциями в базе данных.
    """

    def __init__(self,DbConfig: dict[str, str], pool_config: Optional[dict[str, str]] = None):
        """
        Инициализация менеджера транзакций.

        :param connection_pool: Экземпляр ConnectionPoolManager для получения соединений.
        """
        self.connection_pool = ConnectionPoolManager(DbConfig, pool_config)

    @contextmanager
    def transaction_context(self):
        """
        Контекстный менеджер для работы с транзакцией.
        Гарантирует откат транзакции в случае ошибки и закрытие соединения.
        """
        connection: MySQLConnection = self.connection_pool.get_connection()
        try:
            connection.start_transaction()
            yield connection
            connection.commit()
        except mysql.connector.Error as e:
            logger.error(f"Transaction failed: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
