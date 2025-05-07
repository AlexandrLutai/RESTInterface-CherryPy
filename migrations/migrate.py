import os
import mysql.connector
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIGRATIONS_DIR = os.path.join(BASE_DIR, "migrations")

def get_applied_migrations(connection):
    """
    Получает список уже примененных миграций из таблицы migrations.
    """
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS migrations (id INT AUTO_INCREMENT PRIMARY KEY, migration_name VARCHAR(255) NOT NULL, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("SELECT migration_name FROM migrations")
    applied_migrations = {row[0] for row in cursor.fetchall()}
    cursor.close()
    return applied_migrations

def apply_migration(connection, migration_name, migration_path):
    """
    Применяет миграцию и записывает её в таблицу migrations.
    """
    with open(migration_path, "r", encoding="utf-8") as file:
        sql = file.read()
    cursor = connection.cursor()
    try:
        cursor.execute(sql)
        connection.commit()
        cursor.execute("INSERT INTO migrations (migration_name) VALUES (%s)", (migration_name,))
        connection.commit()
        print(f"Applied migration: {migration_name}")
    except mysql.connector.Error as e:
        connection.rollback()
        print(f"Failed to apply migration {migration_name}: {e}")
    finally:
        cursor.close()

def main():
    """
    Основная функция для выполнения миграций.
    """
    connection = mysql.connector.connect(**DB_CONFIG)
    try:
        applied_migrations = get_applied_migrations(connection)
        all_migrations = sorted(os.listdir(MIGRATIONS_DIR))

        for migration in all_migrations:
            if migration.endswith(".sql") and migration not in applied_migrations:
                migration_path = os.path.join(MIGRATIONS_DIR, migration)
                apply_migration(connection, migration, migration_path)
    finally:
        connection.close()

if __name__ == "__main__":
    main()