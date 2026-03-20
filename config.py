import os

# rate limiting
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "10"))
RATE_WINDOW = int(os.getenv("RATE_WINDOW", "60"))  # seconds

# session config
SESSION_TTL = int(os.getenv("SESSION_TTL", "3600"))

# caching
CACHE_TTL = int(os.getenv("CACHE_TTL", "1800"))  # 30 min default
CACHE_MAX_SIZE = 100

# jwt stuff
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret-change-me")
JWT_ALGO = "HS256"
JWT_EXPIRY = 3600  # 1 hour

ALLOWED_SECTORS = {
    "pharmaceuticals",
    "technology",
    "agriculture",
    "banking",
    "energy",
    "automotive",
    "textiles",
    "infrastructure",
    "telecommunications",
    "chemicals",
}
