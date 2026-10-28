import re
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.memory import Memory, UserSetting

SENSITIVE_PATTERNS = [
    r"\bpassword\b", r"\bpasswd\b", r"\bapi[_-]?key\b", r"\bsecret\b",
    r"\bcredit[_-]?card\b", r"\bcvv\b", r"\bpin\b", r"\botp\b"
]

class LongTermMemory:
    def __init__(self, session: Session):
        self.session = session

    def is_enabled(self, session_id: str) -> bool:
        setting = self.session.query(UserSetting).filter_by(session_id=session_id).first()
        if setting is None:
            # Default to True
            return True
        return setting.long_term_memory_enabled

    def toggle_memory(self, session_id: str, enabled: bool) -> bool:
        setting = self.session.query(UserSetting).filter_by(session_id=session_id).first()
        if setting is None:
            setting = UserSetting(session_id=session_id, long_term_memory_enabled=enabled)
            self.session.add(setting)
        else:
            setting.long_term_memory_enabled = enabled
        self.session.commit()
        return setting.long_term_memory_enabled

    def get_memories(self, session_id: str) -> List[Dict[str, Any]]:
        if not self.is_enabled(session_id):
            return []
        memories = (
            self.session.query(Memory)
            .filter_by(session_id=session_id)
            .order_by(Memory.created_at.desc())
            .all()
        )
        return [m.to_dict() for m in memories]

    def add_or_update_memory(
        self,
        session_id: str,
        key: str,
        value: str,
        category: str = "preference"
    ) -> Optional[Dict[str, Any]]:
        if not self.is_enabled(session_id):
            return None

        clean_key = key.strip()
        clean_val = value.strip()

        # Reject sensitive data patterns
        combined = f"{clean_key} {clean_val}".lower()
        for pat in SENSITIVE_PATTERNS:
            if re.search(pat, combined):
                # Discard sensitive information silently
                return None

        mem = (
            self.session.query(Memory)
            .filter_by(session_id=session_id, key=clean_key)
            .first()
        )

        if mem:
            mem.value = clean_val
            mem.category = category
        else:
            mem = Memory(
                session_id=session_id,
                key=clean_key,
                value=clean_val,
                category=category
            )
            self.session.add(mem)

        self.session.commit()
        return mem.to_dict()

    def delete_memory(self, memory_id: int, session_id: str) -> bool:
        mem = (
            self.session.query(Memory)
            .filter_by(id=memory_id, session_id=session_id)
            .first()
        )
        if not mem:
            return False
        self.session.delete(mem)
        self.session.commit()
        return True

    def clear_all(self, session_id: str) -> int:
        deleted = (
            self.session.query(Memory)
            .filter_by(session_id=session_id)
            .delete()
        )
        self.session.commit()
        return deleted
