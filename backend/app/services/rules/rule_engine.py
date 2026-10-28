import re
import json
import random
from pathlib import Path
from typing import Optional, Dict, Any

class RuleEngine:
    def __init__(self, rules_path: Optional[str] = None):
        if rules_path is None:
            rules_path = Path(__file__).parent / "faq_rules.json"
        self.rules_path = Path(rules_path)
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"greetings": [], "commands": [], "faqs": []}

    def match(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Matches a user message against greeting, command, and verified FAQ patterns.
        Returns matched response dict if matched, otherwise None.
        """
        if not text:
            return None

        clean_text = text.strip()
        lower_text = clean_text.lower()

        # 1. Match Greetings
        for item in self.rules.get("greetings", []):
            for pat in item.get("patterns", []):
                if re.search(pat, lower_text, re.IGNORECASE):
                    responses = item.get("responses", [])
                    res = random.choice(responses) if responses else "Hello! How can I assist you today?"
                    return {
                        "matched": True,
                        "type": "rule",
                        "response": res,
                        "citations": []
                    }

        # 2. Match Commands
        for item in self.rules.get("commands", []):
            for pat in item.get("patterns", []):
                if re.search(pat, lower_text, re.IGNORECASE):
                    return {
                        "matched": True,
                        "type": "rule",
                        "response": item.get("response", ""),
                        "citations": []
                    }

        # 3. Match Verified FAQs
        for item in self.rules.get("faqs", []):
            for pat in item.get("patterns", []):
                if pat in lower_text or re.search(r"\b" + re.escape(pat) + r"\b", lower_text, re.IGNORECASE):
                    citations = []
                    if "url" in item:
                        citations.append({
                            "title": "KBN University Official Portal",
                            "url": item["url"],
                            "snippet": "Verified institutional information."
                        })
                    return {
                        "matched": True,
                        "type": "rule",
                        "response": item.get("response", ""),
                        "citations": citations
                    }

        return None
