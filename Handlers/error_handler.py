import json
import cherrypy
import logging

logger = logging.getLogger(__name__)

def custom_error_handler(status, message, traceback_info, version):
    """
    Централизованный обработчик ошибок для CherryPy.
    Возвращает JSON-ответ вместо HTML.
    """
    print("custom_error_handler called")
    logger.error(f"Error occurred: {status} - {message}")
    cherrypy.response.headers['Content-Type'] = 'application/json'
    return json.dumps({
        "status": status,
        "message": message
    })