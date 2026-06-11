# AgentOps — AI-Powered Market Research Automation Platform

> Multi-agent LLM system that automates end-to-end market research using LangGraph, RAG, and real-time financial data.

**Live Demo:** [agentops.ddns.net](http://agentops.ddns.net)

---

## What it does

You give it a company name and a research question. It spins up a 5-agent pipeline that:
- Plans the research approach
- Retrieves relevant context from uploaded annual reports (RAG)
- Fetches real-time stock prices and financials
- Generates revenue and stock charts
- Writes a structured research report
- Validates the output for hallucinations and prompt injections

No manual data gathering. No copy-pasting from PDFs. Just a research report, end to end.

---

## Architecture

```
User Query
    │
    ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Planner   │────▶│  Researcher  │────▶│   Analyst    │────▶│    Writer    │────▶│    Safety    │
│    Agent    │     │    Agent     │     │    Agent     │     │    Agent     │     │    Agent     │
│             │     │  (RAG +      │     │  (yfinance + │     │  (report     │     │  (halluc.    │
│ breaks down │     │  ChromaDB)   │     │  matplotlib) │     │  synthesis)  │     │  detection)  │
│ the query   │     │              │     │              │     │              │     │              │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                                          │
                                                                                          ▼
                                                                                   Final Report
```

Built on **LangGraph** — a stateful directed graph where each agent reads from and writes to shared state. Supports conditional edges (e.g. Safety Agent can loop back to Writer on hallucination detection).

---

## RAG Pipeline

```
PDF Upload → Text Extraction → Chunking (500 tokens, 50 overlap)
    → sentence-transformer embeddings → ChromaDB vector storage
    → Query time: cosine similarity retrieval (top-k chunks)
    → Injected as context into Researcher Agent prompt
```

Agents can cite exact figures from uploaded annual reports rather than hallucinating numbers.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | LangGraph, LangChain |
| LLM | Groq API (Llama 3) |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers |
| Financial Data | yfinance |
| Charts | matplotlib |
| Backend | FastAPI |
| Deployment | AWS EC2, Nginx, systemd, Let's Encrypt SSL |

---

## Project Structure

```
AgentOps/
├── agents/          # Individual agent definitions (planner, researcher, analyst, writer, safety)
├── rag/             # RAG pipeline: chunking, embedding, retrieval
├── tools/           # yfinance wrapper, chart generation
├── static/          # Frontend assets
├── pipeline.py      # LangGraph state machine definition
├── main.py          # FastAPI app entry point
├── config.py        # Configuration and environment variables
└── requirements.txt
```

---

## Setup & Run

```bash
git clone https://github.com/RamcharanReddy22/AgentOps
cd AgentOps
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key
```

Run locally:
```bash
uvicorn main:app --reload
```

---

## Deployment

Deployed on AWS EC2 (Ubuntu 24.04) with:
- **Nginx** as reverse proxy
- **systemd** service for 24/7 uptime and auto-restart
- **Let's Encrypt SSL** via Certbot
- **Elastic IP** with DDNS hostname

---

## Key Design Decisions

**Why LangGraph over a simple chain?**
LangGraph supports stateful execution with conditional edges — agents can loop back, branch, or share state. A linear chain can't handle the Planner → conditional routing → Safety loop pattern.

**Why ChromaDB over Pinecone?**
Self-hosted, zero cost, persistent storage — ideal for a single-server AWS deployment without external dependencies.

**Why Groq over OpenAI?**
5-10x lower latency on equivalent models. For a 5-agent sequential pipeline, latency compounds — Groq keeps total response time reasonable.

---

## Future Work

- [ ] Streaming intermediate agent outputs to frontend
- [ ] Parallel execution of independent agents (Researcher + Analyst)
- [ ] Authentication and user sessions
- [ ] Redis caching for repeated company lookups
- [ ] Support for multiple document uploads per session
