## EquipmentController

`EquipmentController` — это контроллер для управления оборудованием и типами оборудования. Он обрабатывает HTTP-запросы и взаимодействует с сервисным слоем через `EquipmentService`. Основные функции контроллера включают обработку CRUD-операций для оборудования и получение списка типов оборудования.

### Методы

#### `__init__(self, config)`
Инициализирует контроллер оборудования.
- **Параметры:**
  - `config`: Конфигурация базы данных.

#### `equipment(self, id: int = None, page: int = 1, limit: int = 10, **kwargs)`
Основной маршрут для управления оборудованием. Обрабатывает следующие HTTP-методы:
- **GET**: Получение списка оборудования или конкретной записи по ID.
- **POST**: Добавление нового оборудования.
- **PUT**: Обновление существующего оборудования.
- **DELETE**: Удаление оборудования.
P.S: Все маршруты обрабатываются в одной функции, что является не лучшим подходм. Он был выбран только для того, что-бы маршруты полностью соответствовали маршрутам из ТЗ.

**Параметры:**
- `id`: ID оборудования (для методов GET, PUT, DELETE).
- `page`: Номер страницы (для метода GET списка оборудования).
- `limit`: Лимит записей на странице (для метода GET списка оборудования).
- `kwargs`: Дополнительные параметры.

**Возвращает:** JSON-ответ с результатом операции.

#### `_handle_get_equipment(self, id: int, page: int, limit: int)`
Обрабатывает GET-запросы для оборудования.
- **Параметры:**
  - `id`: ID оборудования.
  - `page`: Номер страницы.
  - `limit`: Лимит записей на странице.
- **Возвращает:** Данные оборудования или список оборудования.

#### `_handle_post_equipment(self)`
Обрабатывает POST-запросы для добавления оборудования.
- **Возвращает:** JSON-ответ с результатом операции.

#### `_handle_put_equipment(self, id: int)`
Обрабатывает PUT-запросы для обновления оборудования.
- **Параметры:**
  - `id`: ID оборудования.
- **Возвращает:** JSON-ответ с результатом операции.

#### `_handle_delete_equipment(self, id: int)`
Обрабатывает DELETE-запросы для удаления оборудования.
- **Параметры:**
  - `id`: ID оборудования.
- **Возвращает:** JSON-ответ с результатом операции.

#### `equipment_type(self, page: int = 1, limit: int = 10, **kwargs)`
Обрабатывает GET-запросы для получения списка типов оборудования.
- **Параметры:**
  - `page`: Номер страницы.
  - `limit`: Лимит записей на странице.
  - `kwargs`: Дополнительные параметры.
- **Возвращает:** Список типов оборудования в формате JSON.

### Декораторы
- `@cherrypy.expose`: Делает метод доступным как HTTP-ресурс.
- `@cherrypy.tools.json_in()`: Обрабатывает входящие данные в формате JSON.
- `@cherrypy.tools.json_out()`: Возвращает данные в формате JSON.
- `@cherrypy.tools.auth()`: Проверяет авторизацию пользователя.
- `@log_and_handle_errors`: Логирует и обрабатывает ошибки для каждого метода.

## DatabaseBase

`DatabaseBase` — это базовый класс для работы с базой данных. Он предоставляет функциональность для управления пулом соединений, выполнения SQL-запросов и работы с транзакциями.

### Методы

#### `__init__(self, db_config: dict[str, Union[str, int]], pool_config: Optional[dict[str, Union[str, int]]] = None)`
Инициализирует пул соединений с базой данных.
- **Параметры:**
  - `db_config`: Словарь с параметрами подключения к базе данных (обязательные ключи: `user`, `password`, `host`, `database`).
  - `pool_config`: Словарь с параметрами пула соединений (например, `pool_size`, `pool_name`, `connection_timeout`).

#### `connection_context(self)`
Контекстный менеджер для работы с подключением к базе данных. Гарантирует закрытие соединения после использования.
- **Возвращает:** Контекстное соединение с базой данных.

#### `execute(self, query: str, params: Optional[tuple[Any, ...]] = None, fetchone: bool = False, fetchall: bool = False, commit: bool = False)`
Выполняет SQL-запрос.
- **Параметры:**
  - `query`: SQL-запрос.
  - `params`: Параметры для подстановки в запрос.
  - `fetchone`: Если `True`, возвращает одну запись.
  - `fetchall`: Если `True`, возвращает все записи.
  - `commit`: Если `True`, фиксирует изменения в базе данных.
- **Возвращает:** Результат запроса (если указаны `fetchone` или `fetchall`).

#### `begin_transaction(self)`
Контекстный менеджер для работы с транзакцией.
- **Возвращает:** Контекстное соединение для выполнения транзакции.

### Исключения
- `ValueError`: Выбрасывается, если отсутствуют обязательные ключи в `db_config` или если SQL-запрос пустой.
- `mysql.connector.Error`: Логируется и выбрасывается при ошибках выполнения запросов или транзакций.

### Логирование
- Логирует информацию о создании пула соединений.
- Логирует ошибки выполнения запросов и транзакций.

### Пример использования
```python
from Database.database_base import DatabaseBase

db_config = {
    "user": "root",
    "password": "password",
    "host": "localhost",
    "database": "example_db"
}

db = DatabaseBase(db_config)

# Выполнение запроса
result = db.execute("SELECT * FROM users WHERE id = %s", params=(1,), fetchone=True)
print(result)

# Работа с транзакцией
with db.begin_transaction() as conn:
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = %s WHERE id = %s", ("John", 1))
    conn.commit()
```

## EquipmentManager

`EquipmentManager` — это класс для управления оборудованием и типами оборудования в базе данных. Он предоставляет методы для выполнения CRUD-операций и работы с данными оборудования.

### Методы

#### `__init__(self, config)`
Инициализирует менеджер оборудования.
- **Параметры:**
  - `config`: Конфигурация базы данных.

#### `_paginate_query(self, query: str, page: int, limit: int, params: Optional[Tuple] = ())`
Выполняет запрос с пагинацией.
- **Параметры:**
  - `query`: SQL-запрос.
  - `page`: Номер страницы (начиная с 1).
  - `limit`: Лимит записей на странице.
  - `params`: Дополнительные параметры для SQL-запроса.
- **Возвращает:** Список записей.

#### `get_all_equipment_types(self, page: int, limit: int)`
Получение списка всех типов оборудования с пагинацией.
- **Параметры:**
  - `page`: Номер страницы (начиная с 1).
  - `limit`: Лимит записей на странице.
- **Возвращает:** Список типов оборудования.

#### `_validate_and_get_type_id(self, serial_number: str)`
Валидация серийного номера и получение `type_id`.
- **Параметры:**
  - `serial_number`: Серийный номер для проверки.
- **Возвращает:** Кортеж `(True, type_id)` при успешной валидации, иначе `(False, сообщение об ошибке)`.

#### `add_equipment(self, equipment_list: List[Dict[str, str]])`
Добавление нового оборудования в базу данных.
- **Параметры:**
  - `equipment_list`: Список словарей с данными оборудования.
- **Возвращает:** Кортеж `(True, сообщение)` при успешном добавлении, иначе `(False, сообщение об ошибке)`.

#### `get_all_equipment(self, page: int, limit: int)`
Получение списка оборудования с пагинацией.
- **Параметры:**
  - `page`: Номер страницы (начиная с 1).
  - `limit`: Лимит записей на странице.
- **Возвращает:** Список оборудования.

#### `get_equipment_by_id(self, equipment_id: int)`
Получение оборудования по ID.
- **Параметры:**
  - `equipment_id`: ID оборудования.
- **Возвращает:** Словарь с данными оборудования или `None`, если запись не найдена.

#### `_check_equipment_exists(self, equipment_id: int, check_deleted: bool = False)`
Проверяет, существует ли запись оборудования в базе данных.
- **Параметры:**
  - `equipment_id`: ID оборудования.
  - `check_deleted`: Если `True`, проверяет, что запись помечена как удалённая.
- **Возвращает:** `True`, если запись существует (и соответствует параметру `check_deleted`), иначе `False`.

#### `update_equipment(self, equipment_id: int, data: Dict[str, Union[int, str]])`
Обновление данных оборудования по ID.
- **Параметры:**
  - `equipment_id`: ID оборудования.
  - `data`: Словарь с данными для обновления.
- **Возвращает:** Кортеж `(True, сообщение)` при успешном обновлении.

#### `soft_delete_equipment(self, equipment_id: int)`
Мягкое удаление оборудования (установка `is_deleted = True`).
- **Параметры:**
  - `equipment_id`: ID оборудования.
- **Возвращает:** Кортеж `(True, сообщение)` при успешном удалении.

### Исключения
- `ValueError`: Выбрасывается при некорректных параметрах (например, номер страницы меньше 1).
- `mysql.connector.Error`: Логируется и выбрасывается при ошибках выполнения запросов или транзакций.

### Логирование
- Логирует ошибки выполнения запросов, транзакций и валидации данных.
- Логирует успешные операции добавления, обновления и удаления оборудования.

### Пример использования
```python
from Database.equipment_manager import EquipmentManager

db_config = {
    "user": "root",
    "password": "password",
    "host": "localhost",
    "database": "example_db"
}

manager = EquipmentManager(db_config)

# Получение всех типов оборудования
types = manager.get_all_equipment_types(page=1, limit=10)
print(types)

# Добавление нового оборудования
equipment_list = [
    {"serial_number": "12345", "note": "Test equipment"}
]
success, message = manager.add_equipment(equipment_list)
print(success, message)

# Обновление оборудования
update_data = {"note": "Updated note"}
success, message = manager.update_equipment(equipment_id=1, data=update_data)
print(success, message)

# Мягкое удаление оборудования
success, message = manager.soft_delete_equipment(equipment_id=1)
print(success, message)
```

## EquipmentService

`EquipmentService` — это сервисный слой для управления оборудованием. Он предоставляет методы для выполнения операций с оборудованием, таких как добавление, обновление, удаление и получение данных.

### Методы

#### `__init__(self, config)`
Инициализирует сервис оборудования.
- **Параметры:**
  - `config`: Конфигурация базы данных.

#### `add_equipment(self, equipment_list: List[Dict[str, str]])`
Добавляет несколько записей в таблицу `equipment`.
- **Параметры:**
  - `equipment_list`: Список словарей с серийными номерами и примечаниями.
- **Возвращает:** Кортеж `(True, сообщение)` при успешном добавлении, иначе `(False, сообщение об ошибке)`.

#### `get_all_equipment(self, page: int, limit: int)`
Получает список оборудования с пагинацией.
- **Параметры:**
  - `page`: Номер страницы (начиная с 1).
  - `limit`: Лимит записей на странице.
- **Возвращает:** Список словарей с данными оборудования.

#### `get_equipment_by_id(self, equipment_id: int)`
Получает запись оборудования по ID.
- **Параметры:**
  - `equipment_id`: ID оборудования.
- **Возвращает:** Словарь с данными оборудования.

#### `update_equipment(self, equipment_id: int, data: Dict[str, Union[int, str]])`
Обновляет запись оборудования по ID.
- **Параметры:**
  - `equipment_id`: ID оборудования.
  - `data`: Данные для обновления (ключи — названия столбцов).
- **Возвращает:** Кортеж `(True, сообщение)` при успешном обновлении, иначе `(False, сообщение об ошибке)`.

#### `soft_delete_equipment(self, equipment_id: int)`
Мягко удаляет запись оборудования, устанавливая `is_deleted = True`.
- **Параметры:**
  - `equipment_id`: ID оборудования.
- **Возвращает:** Кортеж `(True, сообщение)` при успешном удалении, иначе `(False, сообщение об ошибке)`.

#### `get_all_equipment_types(self, page: int, limit: int)`
Получает список всех типов оборудования с пагинацией.
- **Параметры:**
  - `page`: Номер страницы (начиная с 1).
  - `limit`: Лимит записей на странице.
- **Возвращает:** Список словарей с данными типов оборудования.

### Исключения
- `ValueError`: Выбрасывается при некорректных параметрах (например, номер страницы меньше 1).
- `ValidationError`: Выбрасывается при ошибках валидации входных данных.

### Логирование
- Логирует ошибки выполнения операций и валидации данных.
- Логирует успешные операции добавления, обновления и удаления оборудования.

### Пример использования
```python
from Services.equipment_service import EquipmentService

db_config = {
    "user": "root",
    "password": "password",
    "host": "localhost",
    "database": "example_db"
}

service = EquipmentService(db_config)

# Добавление нового оборудования
equipment_list = [
    {"serial_number": "12345", "note": "Test equipment"}
]
success, message = service.add_equipment(equipment_list)
print(success, message)

# Получение всех типов оборудования
types = service.get_all_equipment_types(page=1, limit=10)
print(types)

# Обновление оборудования
update_data = {"note": "Updated note"}
success, message = service.update_equipment(equipment_id=1, data=update_data)
print(success, message)

# Мягкое удаление оборудования
success, message = service.soft_delete_equipment(equipment_id=1)
print(success, message)
```

## ErrorHandler

`ErrorHandler` — это централизованный обработчик ошибок для CherryPy. Он позволяет возвращать JSON-ответы вместо HTML при возникновении ошибок.

### Методы

#### `custom_error_handler(status, message, traceback_info, version)`
Обрабатывает ошибки, возникающие в приложении.
- **Параметры:**
  - `status`: HTTP-статус ошибки (например, "404 Not Found").
  - `message`: Сообщение об ошибке.
  - `traceback_info`: Информация о трассировке (если доступно).
  - `version`: Версия CherryPy.
- **Возвращает:** JSON-ответ с полями:
  - `status`: HTTP-статус ошибки.
  - `message`: Сообщение об ошибке.

### Логирование
- Логирует информацию об ошибке, включая статус и сообщение.

### Пример использования
Для использования `custom_error_handler` в приложении CherryPy, его нужно зарегистрировать как обработчик ошибок:

```python
import cherrypy
from Handlers.error_handler import custom_error_handler

cherrypy.config.update({
    'error_page.default': custom_error_handler
})

if __name__ == '__main__':
    cherrypy.quickstart()
```

## Migrate

`migrate.py` — это скрипт для управления миграциями базы данных. Он автоматически применяет новые миграции из папки `migrations` и записывает информацию о применённых миграциях в таблицу `migrations`.

### Основные функции

#### `get_applied_migrations(connection)`
Получает список уже применённых миграций из таблицы `migrations`.
- **Параметры:**
  - `connection`: Объект соединения с базой данных.
- **Возвращает:** Множество названий применённых миграций.
- **Примечание:** Если таблица `migrations` не существует, она будет создана автоматически.

#### `apply_migration(connection, migration_name, migration_path)`
Применяет миграцию и записывает её в таблицу `migrations`.
- **Параметры:**
  - `connection`: Объект соединения с базой данных.
  - `migration_name`: Название файла миграции.
  - `migration_path`: Путь к файлу миграции.
- **Действия:**
  - Читает SQL-запросы из файла миграции.
  - Выполняет SQL-запросы.
  - Записывает информацию о применённой миграции в таблицу `migrations`.
  - В случае ошибки откатывает изменения.

#### `main()`
Основная функция для выполнения миграций.
- **Действия:**
  - Устанавливает соединение с базой данных.
  - Получает список всех миграций в папке `migrations`.
  - Применяет миграции, которые ещё не были применены.

### Переменные окружения
- `DB_HOST`: Хост базы данных.
- `DB_USER`: Имя пользователя базы данных.
- `DB_PASSWORD`: Пароль пользователя базы данных.
- `DB_NAME`: Название базы данных.

### Логика работы
1. Загружаются переменные окружения из файла `.env`.
2. Устанавливается соединение с базой данных с использованием параметров из переменных окружения.
3. Проверяется наличие таблицы `migrations`. Если её нет, она создаётся.
4. Сравниваются файлы миграций в папке `migrations` с уже применёнными миграциями.
5. Применяются новые миграции.

### Пример структуры папки `migrations`
```
migrations/
├── 000_create_migrations_table.sql
├── 001_create_equipment_type_table.sql
├── 002_create_equipment_table.sql
├── 003_add_new_column_to_equipment.sql
```

### Пример использования
1. Создайте файл `.env` с параметрами подключения к базе данных:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=password
   DB_NAME=example_db
   ```
2. Запустите скрипт:
   ```bash
   python migrate.py
   ```
3. Скрипт автоматически применит новые миграции и выведет результат в консоль.

## Models

`models.py` — это файл, содержащий Pydantic-модели для валидации и обработки данных, связанных с оборудованием. Эти модели используются для проверки входных данных и их преобразования в удобный формат.

### Классы

#### `EquipmentInput`
Модель для представления данных оборудования.
- **Поля:**
  - `serial_number` (str): Серийный номер оборудования. Обязательное поле с минимальной длиной 1 и максимальной длиной 50 символов.
  - `note` (Optional[str]): Примечание к оборудованию. Необязательное поле с максимальной длиной 255 символов.

#### `EquipmentListInput`
Корневая модель для списка объектов `EquipmentInput`.
- **Описание:**
  - Используется для валидации списков оборудования.

#### `EquipmentUpdateInput`
Модель для обновления данных оборудования.
- **Поля:**
  - `serial_number` (Optional[str]): Серийный номер оборудования. Необязательное поле с минимальной длиной 1 и максимальной длиной 50 символов.
  - `note` (Optional[str]): Примечание к оборудованию. Необязательное поле с максимальной длиной 255 символов.
- **Описание:**
  - Все поля являются необязательными, что позволяет обновлять только те данные, которые были переданы.

### Пример использования
```python
from Models.models import EquipmentInput, EquipmentListInput, EquipmentUpdateInput

# Пример валидации одного объекта
input_data = {"serial_number": "12345", "note": "Test equipment"}
equipment = EquipmentInput(**input_data)
print(equipment.dict())

# Пример валидации списка объектов
list_input_data = [
    {"serial_number": "12345", "note": "Test equipment"},
    {"serial_number": "67890"}
]
equipment_list = EquipmentListInput(root=list_input_data)
print(equipment_list.root)

# Пример обновления данных
update_data = {"note": "Updated note"}
equipment_update = EquipmentUpdateInput(**update_data)
print(equipment_update.dict(exclude_unset=True))
```

## Decorators

`decorators.py` — это файл, содержащий декораторы для логирования выполнения методов и обработки ошибок. Эти декораторы помогают централизовать обработку исключений и улучшить читаемость кода.

### Декораторы

#### `log_and_handle_errors(operation: str)`
Декоратор для логирования выполнения метода и обработки ошибок.
- **Параметры:**
  - `operation` (str): Описание операции для логирования.
- **Описание:**
  - Логирует начало и успешное завершение операции.
  - Обрабатывает исключения `ValueError` и другие неожиданные ошибки, записывая их в лог.
  - Повторно выбрасывает исключения после логирования.

### Пример использования
```python
from Utils.decorators import log_and_handle_errors

@log_and_handle_errors("Example operation")
def example_function(param):
    if not param:
        raise ValueError("Parameter cannot be empty.")
    return f"Processed {param}"

# Вызов функции
try:
    result = example_function("test")
    print(result)
except Exception as e:
    print(f"Error: {e}")
```

