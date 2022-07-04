import json
from posixpath import split
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-r5yivtq1.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'Coffee'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

def get_token_auth_header():

    if "Authorization" not in request.headers:
        raise AuthError({"code":"No authorization headers", "description":"Authorization headers were not sent in the request"},401)

    auth_header = request.headers["Authorization"]

    split_header = auth_header.split(" ")

    if len(split_header)!= 2 or split_header[0].lower() != "bearer" :
        raise AuthError({"code":"Invalid header", "description":"malformed authorization header"},403)

    token = split_header[1]
    
    return token


def check_permissions(permission, payload):
    if "permissions" not in payload:
        raise AuthError({"code":"permissions not found", "description":"permissions not found in payload"},400)

    if permission not in payload["permissions"]:
        print(payload["permissions"])
        raise AuthError({"code":"", "description":"permissions not found in payload"},403)
    return True

def verify_decode_jwt(token):
    token = get_token_auth_header()
    jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://"+AUTH0_DOMAIN+"/"
            )
        except jwt.ExpiredSignatureError:
            raise AuthError({"code": "token_expired",
                            "description": "token is expired"}, 401)
        except jwt.JWTClaimsError:
            raise AuthError({"code": "invalid_claims",
                            "description":
                                "incorrect claims,"
                                "please check the audience and issuer"}, 401)
        except Exception:
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Unable to parse authentication"
                                " token."}, 401)

        _request_ctx_stack.top.current_user = payload

        return payload

    raise AuthError({"code": "invalid_header",
                    "description": "Unable to find appropriate key"}, 401)

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator