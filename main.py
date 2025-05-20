import cherrypy
from Utils.authentication import validate_bearer_token  # Импорт функции авторизации
from Handlers.error_handler import custom_error_handler
from dotenv import load_dotenv
import os
from logging import basicConfig, INFO
import logging

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=os.path.join(os.getcwd(), 'app.log'),
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Регистрация инструмента auth
cherrypy.tools.auth = cherrypy.Tool('before_handler', validate_bearer_token)

# Импорт контроллера после регистрации инструмента
from Controllers.equipment_controller import EquipmentController

# Загрузка переменных окружения
load_dotenv()

if __name__ == '__main__':
  
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }

    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8080,
        'tools.json_in.on': True,
        'tools.json_out.on': True,
        'tools.auth.on': True,  
        'log.screen': True,
        'engine.autoreload.on': False,
        'request.error_response': custom_error_handler,  
        'request.show_tracebacks': False  
    })

    dispatcher_conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.auth.on': True,
            'tools.json_in.on': True,
            'tools.json_out.on': True,
        }
    }

    cherrypy.quickstart(EquipmentController(db_config), '/api', config=dispatcher_conf)