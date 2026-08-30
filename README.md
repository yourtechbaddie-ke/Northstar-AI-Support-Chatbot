# Northstar AI Support Chatbot

A portfolio-grade, product-aware customer support application for Northstar Retail Co.

**Your intelligent retail concierge.**

Northstar AI combines a polished conversational frontend with a FastAPI backend and a CrewAI orchestration layer. It is designed to answer product availability questions, explain returns, capture customer contact details, and safely escalate requests outside its supported capabilities.

## Visual identity — Arctic Couture

- Ink `#101114`
- Graphite `#252A32`
- Deep Cobalt `#172F68`
- Electric Cobalt `#3159C8`
- Arctic Blue `#C9DDE5`
- Porcelain `#F5F3EE`
- Snow `#FAFAF7`
- Champagne `#D3BE96`
- Cloud `#E8E9E7`

## Architecture

```text
Customer
   |
   v
React + Vite frontend
   |
   | POST /api/chat
   v
FastAPI backend
   |
   v
CrewAI orchestration
   |
   +--> Intent / contact extraction
   +--> Query routing
   +--> Inventory specialist
   +--> Returns specialist
   +--> Escalation specialist
   |
   +--> Product catalog / optional Firebase inventory
   |
   v
Grounded response
```

## Supported journeys

- **Stock availability** — identify products and report only known inventory facts.
- **Returns** — provide the documented Northstar return policy.
- **Out of scope** — acknowledge the request and route it toward human support.
- **Contact capture** — request an email when email follow-up is required and none was supplied.
- **Product-aware responses** — use the canonical catalog instead of inventing products, prices, SKUs, or stock levels.

## Safety principle

Northstar AI does not fabricate product facts, order details, tracking numbers, prices, stock levels, or return eligibility. Unknown information is treated as unknown.

## Project structure

```text
Northstar-AI-Support-Chatbot/
├── frontend/                 # React + Vite customer experience
├── backend/
│   ├── api/                  # FastAPI application
│   ├── agents/               # CrewAI specialist agents
│   ├── crew/                 # orchestration
│   └── tools/                # catalog + optional Firebase tools
├── data/                     # canonical product catalog
├── public/images/             # Northstar product imagery
├── docs/                     # architecture notes
├── .env.example
├── .gitignore
└── README.md
```

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Create `backend/.env` from `.env.example` and add your CrewAI LLM credentials. Firebase variables are optional for the catalog-first MVP.

Create `frontend/.env` from `frontend/.env.example` and point `VITE_API_BASE_URL` at the FastAPI server.

## API

### `GET /api/health`

Returns service status.

### `POST /api/chat`

```json
{
  "message": "Is the Sovereign Shearling Trench in stock?",
  "session_id": "demo-session"
}
```

Response shape:

```json
{
  "message": "...",
  "intent": "stock_availability",
  "products": []
}
```

## Portfolio context

This application originated from The Northstar Group Project and is being independently expanded as a standalone portfolio project. The standalone repository is intentionally self-contained so it can be demonstrated, deployed, and evaluated independently.
