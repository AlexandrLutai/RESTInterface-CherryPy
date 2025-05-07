import unittest
from unittest.mock import MagicMock, patch
from mysql.connector import Error as MySQLError
from Database.database_base import DatabaseBase

class TestDatabaseBase(unittest.TestCase):
    @patch("Database.database_base.pooling.MySQLConnectionPool")
    def setUp(self, MockMySQLConnectionPool):
        self.mock_pool = MockMySQLConnectionPool.return_value
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_pool.get_connection.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor

        db_config = {
            "user": "mock_user",
            "password": "mock_password",
            "host": "mock_host",
            "database": "mock_db",
        }
        self.db = DatabaseBase(
            db_config=db_config,
            pool_config={"pool_name": "test_pool", "pool_size": 5, "connection_timeout": 10},
        )
        self.db.pool = self.mock_pool

    def test_execute_success(self):
        self.mock_cursor.fetchone.return_value = {"id": 1, "name": "Test"}
        query = "SELECT * FROM test_table WHERE id = %s"
        params = (1,)
        result = self.db.execute(query, params=params, fetchone=True)
        self.mock_connection.cursor.assert_called_once_with(dictionary=True)
        self.mock_cursor.execute.assert_called_once_with(query, params)
        self.assertEqual(result, {"id": 1, "name": "Test"})

    def test_execute_fetchall(self):
        self.mock_cursor.fetchall.return_value = [{"id": 1, "name": "Test"}, {"id": 2, "name": "Test2"}]
        query = "SELECT * FROM test_table"
        result = self.db.execute(query, fetchall=True)
        self.mock_connection.cursor.assert_called_once_with(dictionary=True)
        self.mock_cursor.execute.assert_called_once_with(query, None)
        self.assertEqual(result, [{"id": 1, "name": "Test"}, {"id": 2, "name": "Test2"}])

    def test_execute_commit(self):
        query = "INSERT INTO test_table (name) VALUES (%s)"
        params = ("Test",)
        self.db.execute(query, params=params, commit=True)
        self.mock_connection.cursor.assert_called_once_with(dictionary=True)
        self.mock_cursor.execute.assert_called_once_with(query, params)
        self.mock_connection.commit.assert_called_once()

    def test_execute_error(self):
        self.mock_cursor.execute.side_effect = MySQLError("Test error")
        query = "SELECT * FROM test_table"
        with self.assertRaises(MySQLError):
            self.db.execute(query)
        self.mock_connection.cursor.assert_called_once_with(dictionary=True)
        self.mock_cursor.execute.assert_called_once_with(query, None)

if __name__ == "__main__":
    unittest.main()