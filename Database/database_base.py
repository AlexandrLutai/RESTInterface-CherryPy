import mysql.connector
from mysql.connector import pooling
from mysql.connector.connection import MySQLConnection
from typing import Any, Optional, Union, Callable
import os
import logging
from contextlib import contextmanager
from Utils.decorators import log_and_handle_errors  

logger = logging.getLogger(__name__)

class DatabaseBase:
    def __init__(self, db_config: dict[str, Union[str, int]], pool_config: Optional[dict[str, Union[str, int]]] = None):
        """
        Инициализация пула соединений с базой данных.
        :param db_config: Словарь с параметрами подключения к базе данных.
        :param pool_config: Словарь с параметрами пула соединений (например, pool_size, pool_name).
        """
        required_keys = ["user", "password", "host", "database"]
        for key in required_keys:
            if key not in db_config:
                raise ValueError(f"Missing required database configuration key: {key}")

        pool_name = pool_config.get("pool_name", "db_pool") if pool_config else "db_pool"
        pool_size = pool_config.get("pool_size", 5) if pool_config else 5
        connection_timeout = pool_config.get("connection_timeout", 10) if pool_config else 10

        self.pool: pooling.MySQLConnectionPool = pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            connection_timeout=connection_timeout,
            **db_config
        )
        logger.info(f"Database connection pool initialized with pool_name={pool_name}, pool_size={pool_size}, connection_timeout={connection_timeout}.")

    @contextmanager
    @log_and_handle_errors("Managing database connection")
    def connection_context(self):
        """
        Контекстный менеджер для работы с подключением к базе данных.
        Гарантирует закрытие соединения после использования.
        """
        connection = self.pool.get_connection()
        try:
            yield connection
        except mysql.connector.Error as e:
            logger.error(f"Error during database operation: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()

    @log_and_handle_errors("Executing SQL query")
    def execute(
        self,
        query: str,
        params: Optional[tuple[Any, ...]] = None,
        fetchone: bool = False,
        fetchall: bool = False,
        commit: bool = False,
    ) -> Optional[Union[dict[str, Any], list[dict[str, Any]]]]:
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

        with self.connection_context() as connection:
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

    @log_and_handle_errors("Managing database transaction")
    def begin_transaction(self):
        """
        Контекстный менеджер для работы с транзакцией.
        """
        @contextmanager
        def transaction_context():
            connection = self.pool.get_connection()
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

        return transaction_context()
