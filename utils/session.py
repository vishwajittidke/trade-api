import time
import uuid
from collections import defaultdict
from config import SESSION_TTL


class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.user_sessions = defaultdict(list)  # user_id -> [session_ids]

    def create_session(self, user_id):
        # clean up old ones first
        self._cleanup()

        sid = str(uuid.uuid4())
        self.sessions[sid] = {
            "session_id": sid,
            "user_id": user_id,
            "created_at": time.time(),
            "last_active": time.time(),
            "request_count": 0,
            "requests": [],
        }
        self.user_sessions[user_id].append(sid)
        return sid

    def get_session(self, session_id):
        s = self.sessions.get(session_id)
        if s and (time.time() - s["created_at"]) < SESSION_TTL:
            return s
        return None

    def get_or_create_session(self, user_id):
        """grab existing session or make a new one"""
        for sid in reversed(self.user_sessions.get(user_id, [])):
            if self.get_session(sid):
                return sid
        return self.create_session(user_id)

    def track_request(self, session_id, endpoint):
        s = self.sessions.get(session_id)
        if not s:
            return
        s["request_count"] += 1
        s["last_active"] = time.time()
        s["requests"].append({"endpoint": endpoint, "timestamp": time.time()})

    def _cleanup(self):
        """remove expired sessions"""
        now = time.time()
        expired = [sid for sid, s in self.sessions.items()
                   if now - s["created_at"] > SESSION_TTL]
        for sid in expired:
            uid = self.sessions[sid]["user_id"]
            del self.sessions[sid]
            self.user_sessions[uid] = [x for x in self.user_sessions[uid] if x != sid]
