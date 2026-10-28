import pytest
from app.services.rules.rule_engine import RuleEngine

@pytest.fixture
def rule_engine():
    return RuleEngine()

def test_greeting_matching(rule_engine):
    for phrase in ["Hello", "hi there", "Good morning!", "hey assistant", "Namaste"]:
        match = rule_engine.match(phrase)
        assert match is not None, f"Failed to match greeting: {phrase}"
        assert match["matched"] is True
        assert match["type"] == "rule"
        assert len(match["response"]) > 0

def test_command_matching(rule_engine):
    match = rule_engine.match("/help")
    assert match is not None
    assert "Academic Programs" in match["response"]

    match_about = rule_engine.match("/about")
    assert match_about is not None
    assert "Khaja Bandanawaz University" in match_about["response"]

def test_verified_faqs(rule_engine):
    match_loc = rule_engine.match("Where is KBN University located?")
    assert match_loc is not None
    assert "Kalaburagi" in match_loc["response"]
    assert len(match_loc["citations"]) > 0
    assert "kbn.university" in match_loc["citations"][0]["url"]

    match_fac = rule_engine.match("What faculties are available at KBN University?")
    assert match_fac is not None
    assert "Faculty of Engineering" in match_fac["response"]
    assert "Faculty of Medical Sciences" in match_fac["response"]

def test_unmatched_query(rule_engine):
    match = rule_engine.match("What is quantum entanglement in physics?")
    assert match is None
