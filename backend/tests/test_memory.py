import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.extensions import Base
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.memory.short_term import ShortTermMemory
from app.services.memory.long_term import LongTermMemory
from app.services.memory.summarizer import ConversationSummarizer

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_short_term_memory_sliding_window(db_session):
    conv = Conversation(session_id="session-1", title="Test")
    db_session.add(conv)
    db_session.commit()

    for i in range(10):
        role = "user" if i % 2 == 0 else "assistant"
        db_session.add(Message(conversation_id=conv.id, role=role, content=f"Message {i}"))
    db_session.commit()

    stm = ShortTermMemory(db_session, window_size=4)
    recent = stm.get_recent_messages(conv.id)
    assert len(recent) == 4
    assert recent[-1]["content"] == "Message 9"

def test_long_term_memory_isolation_and_privacy(db_session):
    ltm = LongTermMemory(db_session)

    # Session A memory
    ltm.add_or_update_memory("session-a", "interested_field", "Computer Science")
    
    # Session B memory
    ltm.add_or_update_memory("session-b", "interested_field", "Medical Sciences")

    mem_a = ltm.get_memories("session-a")
    mem_b = ltm.get_memories("session-b")

    assert len(mem_a) == 1
    assert mem_a[0]["value"] == "Computer Science"

    assert len(mem_b) == 1
    assert mem_b[0]["value"] == "Medical Sciences"

    # Test rejection of sensitive data
    rejected = ltm.add_or_update_memory("session-a", "api_key", "secret-password-123")
    assert rejected is None

    # Test toggle
    ltm.toggle_memory("session-a", False)
    assert ltm.is_enabled("session-a") is False
    assert len(ltm.get_memories("session-a")) == 0
