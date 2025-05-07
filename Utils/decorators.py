import logging
from functools import wraps

logger = logging.getLogger(__name__)

def log_and_handle_errors(operation: str):
    """
    Декоратор для логирования выполнения метода и обработки ошибок.
    
    :param operation: Описание операции для логирования.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Starting operation: {operation}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Operation '{operation}' completed successfully.")
                return result
            except ValueError as e:
                logger.error(f"ValueError during '{operation}': {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error during '{operation}': {e}", exc_info=True)
                raise
        return wrapper
    return decorator