# KBN University Hybrid AI Chatbot

A production-grade, full-stack Hybrid Conversational AI Assistant built from scratch for **Khaja Bandanawaz University (KBN University)**, Kalaburagi, Karnataka.

The system combines deterministic rule-based FAQ responses, an end-to-end Retrieval-Augmented Generation (RAG) pipeline grounded in the official university website ([https://www.kbn.university/](https://www.kbn.university/)), local LLM integration through Ollama (Qwen), persistent PostgreSQL + pgvector storage, three-layer conversational memory, and a university-helpdesk interface following the **Deep Amethyst** and **Electric Purple** design system.

---

## Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │   React + Vite Frontend (Tailwind CSS) │
                      │   Deep Amethyst & Electric Purple UI   │
                      └───────────────────┬────────────────────┘
                                          │ REST API & SSE Streams
                                          ▼
                      ┌────────────────────────────────────────┐
                      │          Flask Backend Service         │
                      └───────────────────┬────────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
      ┌─────────────────────────┐                     ┌─────────────────────────┐
      │   Hybrid Router Service │                     │ Ingestion & Web Crawler │
      └───────────┬─────────────┘                     └───────────┬─────────────┘
                  │                                               │
    ┌─────────────┼─────────────┐                     ┌───────────┼─────────────┐
    ▼             ▼             ▼                     ▼           ▼             ▼
┌────────┐  ┌───────────┐ ┌───────────┐         ┌───────────┐ ┌───────┐ ┌─────────────┐
│ Rules  │  │ RAG & Cit.│ │ 3-Layer   │         │ SameDomain│ │ HTML  │ │ Recursive   │
│ Engine │  │ Pipeline  │ │ Memory    │         │ Crawler   │ │ Clean │ │ Chunker     │
└────────┘  └─────┬─────┘ └─────┬─────┘         └─────┬─────┘ └───────┘ └──────┬──────┘
                  │             │                     │                        │
                  ▼             ▼                     └───────────┬────────────┘
      ┌─────────────────────────────────┐                         │
      │   Persistent Storage & pgvector │ ◄───────────────────────┘
      │   PostgreSQL / SQLite fallback  │
      └─────────────────────────────────┘
                  │
                  ▼
      ┌─────────────────────────────────┐
      │     Ollama LLM Provider         │
      │     Qwen 2.5 + nomic-embed      │
      └─────────────────────────────────┘
```

---

## Design System & Palette

The user interface follows the required **Deep Amethyst** and **Electric Purple** palette:

| Element | Color Name | Hex Code | Purpose |
| :--- | :--- | :--- | :--- |
| **Main Background** | Deep Black Amethyst | `#0F0A19` | Main page canvas |
| **Surface** | Dark Surface | `#1B1229` | Cards, modals, chat bubbles |
| **Deep Amethyst** | Deep Amethyst | `#24103F` | Active items, sidebar borders |
| **Dark Amethyst** | Dark Amethyst | `#160B2B` | Headers, sidebars, code blocks |
| **Electric Purple**| Electric Purple | `#8B5CF6` | Primary action buttons, accents, focus |
| **Bright Electric**| Bright Electric Purple | `#A855F7` | Link hovers, active tags |
| **Soft Lavender**  | Soft Lavender | `#D8B4FE` | Headings, badge highlights |
| **Primary Text**   | Primary Text | `#F5F3FF` | High contrast readable content |
| **Secondary Text** | Secondary Text | `#B8A9CC` | Muted labels, timestamps, previews |
| **Border**         | Border | `#38264D` | Subtle section dividers |

---

## Technology Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React, React Router DOM, React Markdown, Rehype Sanitize, Server-Sent Events (SSE).
- **Backend**: Python 3.11+, Flask 3, SQLAlchemy 2, Alembic, Flask-CORS, Pydantic 2, Requests, BeautifulSoup4, NumPy.
- **AI & LLM**: Ollama local API, Qwen 2.5 (`qwen2.5:7b`), Nomic Embeddings (`nomic-embed-text`), Local SentenceTransformers fallback.
- **Database**: PostgreSQL 16 + pgvector (`pgvector/pgvector:pg16`), with automatic SQLite vector fallback for standalone testing.
- **Security**: SSRF protection (private IP / link-local blocking, DNS resolution, redirect validation), HMAC session token authentication, prompt injection shields.

---

## Project Structure

```
hybrid-ai-chatbot/
├── README.md
├── .gitignore
├── docker-compose.yml
├── backend/
│   ├── .env.example
│   ├── .env
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── run.py
│   ├── kbn_chatbot.db
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── conversations.py
│   │   │   ├── knowledge.py
│   │   │   ├── memories.py
│   │   │   ├── health.py
│   │   │   └── session_helper.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── conversation.py
│   │   │   ├── message.py
│   │   │   ├── knowledge_source.py
│   │   │   ├── document.py
│   │   │   ├── document_chunk.py
│   │   │   ├── memory.py
│   │   │   ├── conversation_summary.py
│   │   │   └── ingestion_job.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── chat_schema.py
│   │   │   ├── knowledge_schema.py
│   │   │   └── memory_schema.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── chat_service.py
│   │   │   ├── conversation_service.py
│   │   │   ├── hybrid_router.py
│   │   │   ├── llm/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_provider.py
│   │   │   │   ├── ollama_provider.py
│   │   │   │   └── prompt_templates.py
│   │   │   ├── rag/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── embeddings.py
│   │   │   │   ├── chunker.py
│   │   │   │   ├── retriever.py
│   │   │   │   ├── vector_store.py
│   │   │   │   └── citations.py
│   │   │   ├── ingestion/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── url_validator.py
│   │   │   │   ├── content_cleaner.py
│   │   │   │   ├── scraper.py
│   │   │   │   ├── crawler.py
│   │   │   │   └── ingestion_service.py
│   │   │   ├── memory/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── short_term.py
│   │   │   │   ├── summarizer.py
│   │   │   │   ├── long_term.py
│   │   │   │   └── memory_retriever.py
│   │   │   └── rules/
│   │   │       ├── __init__.py
│   │   │       ├── rule_engine.py
│   │   │       └── faq_rules.json
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── errors.py
│   │       ├── logging_config.py
│   │       └── security.py
│   ├── scripts/
│   │   ├── init_db.py
│   │   ├── check_services.py
│   │   └── ingest_initial.py
│   └── tests/
│       ├── __init__.py
│       ├── test_rules.py
│       ├── test_ingestion.py
│       ├── test_rag.py
│       ├── test_memory.py
│       └── test_chat.py
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── index.css
        ├── context/
        │   └── ChatContext.jsx
        ├── hooks/
        │   └── useChat.js
        ├── services/
        │   ├── api.js
        │   ├── chatService.js
        │   ├── knowledgeService.js
        │   ├── memoryService.js
        │   └── settingsService.js
        ├── pages/
        │   ├── ChatPage.jsx
        │   ├── KnowledgePage.jsx
        │   ├── MemoryPage.jsx
        │   └── SettingsPage.jsx
        └── components/
            ├── layout/
            │   ├── AppLayout.jsx
            │   ├── Header.jsx
            │   ├── Sidebar.jsx
            │   └── MobileNavigation.jsx
            ├── common/
            │   ├── Button.jsx
            │   ├── Modal.jsx
            │   ├── LoadingSpinner.jsx
            │   └── ErrorMessage.jsx
            ├── chat/
            │   ├── ChatWindow.jsx
            │   ├── MessageList.jsx
            │   ├── MessageBubble.jsx
            │   ├── MessageInput.jsx
            │   ├── TypingIndicator.jsx
            │   ├── SourceCitations.jsx
            │   └── WelcomeScreen.jsx
            ├── knowledge/
            │   ├── WebsiteForm.jsx
            │   ├── SourceCard.jsx
            │   └── IngestionStatus.jsx
            └── memory/
                ├── MemoryList.jsx
                └── MemoryCard.jsx
```

---

## Quickstart Guide

### 1. Prerequisites
- **Python**: 3.11+
- **Node.js**: v18+ (Node v26.12.1 verified)
- **Ollama** (optional, for local LLM generation): [https://ollama.com](https://ollama.com)
- **Docker** (optional, for PostgreSQL + pgvector container)

### 2. Database Setup

#### Option A: PostgreSQL with pgvector (Docker)
Start the PostgreSQL container with pgvector:
```bash
cd hybrid-ai-chatbot
docker compose up -d
```
Update `backend/.env`:
```env
DATABASE_URL=postgresql+psycopg2://chatbot:chatbot_secret@localhost:5432/chatbot
```

#### Option B: Standalone SQLite with Vector Engine (Default)
The backend defaults to SQLite (`backend/kbn_chatbot.db`) with an embedded vector cosine similarity engine, requiring no external databases to run.

### 3. Backend Setup & Startup

1. Open a terminal in the backend directory:
```powershell
cd hybrid-ai-chatbot/backend
```

2. Run tests to verify all 16 test cases pass:
```powershell
pytest
```

3. Run system diagnostics:
```powershell
python scripts/check_services.py
```

4. Start the Flask server:
```powershell
python run.py
```
The API starts on `http://127.0.0.1:5000`.

### 4. Frontend Setup & Startup

1. Open a new terminal in the frontend directory:
```powershell
cd hybrid-ai-chatbot/frontend
```

2. Start the Vite development server:
```powershell
npm run dev
```

3. Open your browser at:
`http://localhost:5173`

---

## Ollama & Qwen Configuration

To activate local natural-language generation:
1. Download Ollama from [ollama.com](https://ollama.com) and install it.
2. Start the daemon:
   ```bash
   ollama serve
   ```
3. Pull the configured Qwen model:
   ```bash
   ollama pull qwen2.5:7b
   ```
4. Pull the embedding model:
   ```bash
   ollama pull nomic-embed-text
   ```

*Note: If Ollama is offline, the chatbot seamlessly uses deterministic rule matching and verified KBN University FAQ data, reporting the offline LLM status via `/api/llm/status` and on the Settings page.*

---

## REST API Documentation

### Chat & Conversations
- `POST /api/chat`: Send a chat message. Supports SSE streaming (`stream: true`) or standard JSON (`stream: false`).
- `GET /api/conversations`: List active conversations for the authenticated session.
- `POST /api/conversations`: Create a new conversation thread (`{title: "..."}`).
- `GET /api/conversations/<id>/messages`: Fetch message history for a conversation.
- `PATCH /api/conversations/<id>`: Rename a conversation.
- `DELETE /api/conversations/<id>`: Delete a conversation and all its messages.
- `DELETE /api/conversations/<id>/messages`: Clear message history.

### Knowledge Management
- `GET /api/knowledge/sources`: List indexed website sources with total document and chunk counts.
- `POST /api/knowledge/sources`: Register and trigger crawl for a website (`{url: "https://www.kbn.university/"}`).
- `POST /api/knowledge/sources/<id>/refresh`: Reindex an existing source.
- `DELETE /api/knowledge/sources/<id>`: Delete source, cascading documents and vector embeddings.
- `GET /api/knowledge/jobs`: Monitor crawler background jobs and metrics.

### Three-Layer Memory
- `GET /api/memories`: List saved user preferences for current session.
- `POST /api/memories`: Store user preference (`{key: "...", value: "...", category: "..."}`).
- `PATCH /api/memories/<id>`: Update an existing memory item.
- `DELETE /api/memories/<id>`: Remove an individual memory item.
- `DELETE /api/memories`: Purge all memories for current session.
- `GET /api/memories/settings`: Inspect memory settings (`long_term_memory_enabled`).
- `POST /api/memories/settings`: Toggle long-term memory on or off.

### System Diagnostics
- `GET /api/health`: Database connection check, engine type, total documents, and chunk counts.
- `GET /api/llm/status`: Real Ollama reachability, configured model status, vector dimension.
- `GET /api/models`: Installed model list in local Ollama registry.

---

## Automated Test Results

The backend contains 16 comprehensive automated unit and integration tests covering:
- **Rule Engine**: Greeting patterns, command handlers (`/help`, `/about`), verified university FAQ matches.
- **SSRF & Security**: Blocking loopbacks (`127.0.0.1`), private RFC1918 subnets, cloud metadata (`169.254.169.254`), and IPv6.
- **Ingestion & Cleaning**: HTML sanitization, script stripping, unicode normalizations (`\u200b`, `\xa0`), content hashing.
- **Recursive Chunker**: Sliding chunk boundaries, paragraph and sentence preservation.
- **RAG & Vector Retrieval**: Embedding generation, vector similarity matching, relevance filtering, source citation attribution.
- **Conversational Memory**: Short-term sliding windows, long-term memory isolation between sessions, privacy filters rejecting passwords/API keys.
- **REST APIs**: Health status, Ollama status, conversation CRUD, and guest session handling.

Run tests:
```powershell
pytest
```
*Result: 16 passed in 40.56s.*
