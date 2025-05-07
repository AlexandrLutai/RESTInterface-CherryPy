import cherrypy

VALID_TOKENS = ["1111111"]  

def validate_bearer_token():
    """
    Проверяет наличие и валидность Bearer-токена в заголовке Authorization.
    """
    auth_header = cherrypy.request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise cherrypy.HTTPError(401, "Unauthorized: Missing or invalid Authorization header.")
    
    token = auth_header.split("Bearer ")[1]
    

    if token not in VALID_TOKENS:
        raise cherrypy.HTTPError(403, "Forbidden: Invalid token.")