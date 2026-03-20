import time
import jwt
from config import SECRET_KEY, JWT_ALGO, JWT_EXPIRY


def create_token(user_id: str):
    payload = {
        "user_id": user_id,
        "iat": time.time(),
        "exp": time.time() + JWT_EXPIRY
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGO)


def verify_token(token: str):
    """Returns user_id if valid, None otherwise"""
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGO])
        return data.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
