# Billing Agent

A billing investigation assistant. Given a customer ID and a question such as
"Why did my bill increase?", an LLM agent looks up billing, usage, customer and
rate-plan data through tools and explains the answer using only what those
tools return. If the data cannot explain a discrepancy, the agent says so
instead of guessing.

## Architecture (current)

```
Client
  |  POST /investigate {customer_id, query}
  v
FastAPI app (app/main.py)
  |-- /health                    app/api/routes/health.py
  |-- /investigate               app/api/routes/chat.py
        |  validates request     app/api/schemas.py (Pydantic)
        |  on agent failure -> HTTP 503 (generic message, details logged)
        v
LangGraph agent (app/agent.py)
  agent node (ChatOpenAI + system prompt) <--> tools node
        v
Tools (app/tools/)  ->  JSON files in data/
  get_customer, get_billing_info, get_usage_info, get_rate_plan
```

| Component | Location | Purpose |
|---|---|---|
| API | `app/main.py`, `app/api/` | FastAPI app, request/response schemas, routes |
| Agent | `app/agent.py` | LangGraph loop: model decides which tools to call until it can answer |
| Prompt | `app/prompts.py` | Instructs the agent to answer only from tool data and never invent billing info |
| Tools | `app/tools/` | Read-only lookups over `data/*.json` (a stand-in for a real billing system) |
| Tests | `tests/` | Pytest tests for the API (agent mocked), tools and agent |
| Evals | `evals/` | End-to-end cases checking tool selection, expected facts and LLM-judged groundedness |

### Design notes

- **Grounding:** the system prompt restricts answers to tool output. An
  LLM-as-judge (`evals/judge.py`) checks that answers are supported by the
  tool responses.
- **Error handling:** if the agent call fails, the API returns `503` with a
  generic message. The real exception is logged server-side and never sent to
  the client.
- **Tests do not call OpenAI:** API tests patch `app.api.routes.chat.agent`.

## Getting started

### Prerequisites

- Python 3.10+
- An OpenAI API key

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux: `source .venv/bin/activate`

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your API key

```bash
copy .env.example .env      # macOS/Linux: cp .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY`. The `.env` file is gitignored, so do not
commit it or paste the key anywhere else.

### 4. Start the application

Run from the project root (the tools read `data/` using relative paths):

```bash
uvicorn app.main:app --reload
```

The API runs at http://127.0.0.1:8000, with interactive docs at
http://127.0.0.1:8000/docs.

### 5. Try it

Include the billing months in the question; without them the agent will ask
which months to compare.

**Windows (PowerShell):**

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health

Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/investigate `
  -ContentType "application/json" `
  -Body '{"customer_id": "C001", "query": "Why did my bill increase from June 2026 to July 2026?"}'
```

**macOS/Linux (bash):**

```bash
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/investigate \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C001", "query": "Why did my bill increase from June 2026 to July 2026?"}'
```

The `bash` example uses `\` line continuations and single quotes, so it does
not work as written in PowerShell or cmd.

### Run the tests

```bash
python -m pytest -v
```

### Run the evaluations

Calls the real OpenAI API and incurs cost:

```bash
python -m evals.run_evals
```

Reports tool-selection, expected-facts and groundedness results per case, plus
pass rate, average latency and average tool calls.

## Security and secrets

- Keys are read from the `OPENAI_API_KEY` environment variable (loaded from
  `.env` locally). No keys are in source code.
- `.env` is excluded from git (`.gitignore`) and from Docker images
  (`.dockerignore`). Only `.env.example`, which has no real value, is committed.
- If a key is ever committed or shared, revoke it in the OpenAI dashboard and
  create a new one. Removing it from git history is not enough.
- In deployed environments, inject the key through your platform's secrets
  manager rather than baking it into an image or repository.

## Roadmap

### Phase 1: Portfolio-ready (about 3-5 additional hours)

- Automated FastAPI tests (in progress) and error handling (in progress)
- Structured logging
- Docker
- README with architecture and evaluation results

### Phase 2: Production-oriented (about 1-2 additional days)

- Authentication and customer authorization
- Request timeouts, rate limiting and retries
- Expanded evaluation cases
- Basic observability

### Phase 3: Enterprise production readiness (depends on requirements)

- Deploy to AWS
- Secrets management integration
- CI/CD
- Cost and performance monitoring
- Load and security testing
- Operational procedures

Actual production readiness requires validation against your deployment
environment and security requirements.

## Evaluation results

_To be added: run `python -m evals.run_evals` and record the pass rate,
average latency and average tool calls here._
