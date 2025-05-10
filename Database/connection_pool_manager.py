import mysql.connector
from mysql.connector import pooling
from typing import Union, Optional
import logging

logger = logging.getLogger(__name__)

class ConnectionPoolManager:
    """
    Класс для управления пулом соединений с базой данных.
    """

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
        logger.info(f"Connection pool initialized with pool_name={pool_name}, pool_size={pool_size}, connection_timeout={connection_timeout}.")

    def get_connection(self):
        """
        Получает соединение из пула.

        :return: Объект соединения MySQL.
        """
        try:
            return self.pool.get_connection()
        except mysql.connector.Error as e:
            logger.error(f"Failed to get connection from pool: {e}")
            raise
