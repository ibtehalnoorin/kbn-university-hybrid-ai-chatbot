import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.rules.rule_engine import RuleEngine
from app.services.rag.retriever import Retriever
from app.services.rag.citations import CitationBuilder
from app.services.memory.memory_retriever import MemoryRetriever
from app.services.llm.base_provider import BaseLLMProvider
from app.services.llm.prompt_templates import SYSTEM_PROMPT, RAG_CONTEXT_TEMPLATE, GENERAL_QUERY_TEMPLATE

class HybridRouter:
    def __init__(
        self,
        session: Session,
        rule_engine: RuleEngine,
        retriever: Retriever,
        llm_provider: BaseLLMProvider,
        similarity_threshold: float = 0.45,
        top_k: int = 5
    ):
        self.session = session
        self.rule_engine = rule_engine
        self.retriever = retriever
        self.llm_provider = llm_provider
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        self.memory_retriever = MemoryRetriever(session, llm_provider)

    def route_and_prepare(
        self,
        message: str,
        session_id: str,
        conversation_id: int
    ) -> Dict[str, Any]:
        """
        Determines the routing path:
        1. Rule-based match
        2. RAG pipeline with grounded context
        3. Low-confidence honest response
        4. General LLM inquiry
        """
        # Step 1: Check Rule Engine
        rule_res = self.rule_engine.match(message)
        if rule_res:
            return {
                "route": "rule",
                "direct_response": rule_res["response"],
                "citations": rule_res.get("citations", []),
                "messages_for_llm": None,
                "chunks": []
            }

        # Step 2: Assemble Memory Context
        memory_ctx = self.memory_retriever.assemble_memory_context(session_id, conversation_id)
        user_mem_str = memory_ctx["user_memory_context"]
        summary_str = memory_ctx["conversation_summary_context"]
        recent_msgs = memory_ctx["recent_messages"]

        # Step 3: RAG Retrieval
        chunks, context_str = self.retriever.retrieve(
            query=message,
            top_k=self.top_k,
            threshold=self.similarity_threshold
        )

        # Build System Prompt with injected memory
        formatted_system_prompt = SYSTEM_PROMPT.format(
            user_memory_context=user_mem_str,
            conversation_summary_context=summary_str
        )

        is_university_query = bool(re.search(
            r"\b(kbn|university|admission|fee|faculty|syllabus|exam|scholarship|hostel|campus|course|eligibility|chancellor|department|b\.?tech|m\.?tech|mbbs)\b",
            message,
            re.IGNORECASE
        ))

        if chunks:
            # RAG Route: Grounded in retrieved passages
            citations = CitationBuilder.build_citations(chunks)
            user_prompt = RAG_CONTEXT_TEMPLATE.format(
                context_passages=context_str,
                user_query=message
            )

            llm_messages = [{"role": "system", "content": formatted_system_prompt}]
            # Include recent short term messages for reference resolution
            for m in recent_msgs[-4:]:
                llm_messages.append(m)
            llm_messages.append({"role": "user", "content": user_prompt})

            return {
                "route": "rag",
                "direct_response": None,
                "citations": citations,
                "messages_for_llm": llm_messages,
                "chunks": chunks
            }

        elif is_university_query:
            # Honest low-confidence answer when no chunks match university query
            honest_reply = (
                "I could not verify information regarding this topic from the indexed KBN University sources. "
                "For verified details, please visit the official university portal at "
                "[https://www.kbn.university/](https://www.kbn.university/) or contact the university administration directly."
            )
            return {
                "route": "low_confidence",
                "direct_response": honest_reply,
                "citations": [{
                    "title": "KBN University Official Portal",
                    "url": "https://www.kbn.university/",
                    "snippet": "Official university portal."
                }],
                "messages_for_llm": None,
                "chunks": []
            }

        else:
            # General conversation route
            user_prompt = GENERAL_QUERY_TEMPLATE.format(user_query=message)
            llm_messages = [{"role": "system", "content": formatted_system_prompt}]
            for m in recent_msgs[-4:]:
                llm_messages.append(m)
            llm_messages.append({"role": "user", "content": user_prompt})

            return {
                "route": "llm",
                "direct_response": None,
                "citations": [],
                "messages_for_llm": llm_messages,
                "chunks": []
            }
