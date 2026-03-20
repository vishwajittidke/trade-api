import time
from collections import defaultdict
from config import RATE_LIMIT, RATE_WINDOW

# simple in-memory store: user_id -> list of timestamps
_store = defaultdict(list)


def is_allowed(user_id):
    now = time.time()

    # drop old timestamps outside the window
    _store[user_id] = [t for t in _store[user_id] if now - t < RATE_WINDOW]

    if len(_store[user_id]) >= RATE_LIMIT:
        return False

    _store[user_id].append(now)
    return True
