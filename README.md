# Northstar AI Support Chatbot

> **Your intelligent retail concierge.**

Northstar AI Support is a portfolio-grade, product-aware customer support application for Northstar Retail Co. It combines a refined React experience, a FastAPI service, CrewAI specialist agents, and a grounded Northstar product catalog.

## What it demonstrates

- **AI engineering:** CrewAI specialist agents with grounded prompts and controlled routing.
- **Backend engineering:** FastAPI, validation, CORS, structured API responses, and error handling.
- **Frontend engineering:** React + Vite, responsive conversational UX, product cards, loading states, and accessible controls.
- **Data grounding:** responses are tied to the canonical Northstar catalog rather than invented products or stock.
- **Production thinking:** deterministic fallback behavior keeps the demo usable when an LLM key is not configured.

## Arctic Couture design system

The chatbot has its own visual identity rather than duplicating the Northstar storefront.

| Token | Hex | Purpose |
|---|---|---|
| Ink | `#101114` | Primary dark surfaces |
| Graphite | `#252A32` | Elevated dark surfaces |
| Deep Cobalt | `#172F68` | Secondary brand depth |
| Electric Cobalt | `#3159C8` | AI/action accent |
| Arctic Blue | `#C9DDE5` | AI surfaces and highlights |
| Porcelain | `#F5F3EE` | Main canvas |
| Snow | `#FAFAF7` | Clean surfaces |
| Champagne | `#D3BE96` | Restrained luxury accent |
| Cloud | `#E8E9E7` | Borders and muted UI |

## Architecture

```text
                         CUSTOMER
                            |
                            v
                    React + Vite UI
                            |
                     POST /api/chat
                            |
                            v
                       FastAPI API
                            |
                            v
                    Support Service
                            |
             +--------------+--------------+
             |              |              |
        Intent route    Product match   Contact signal
             |              |              |
             v              v              v
          CrewAI       Northstar      Contact capture
         specialist      catalog
             |
       +-----+------+----------------+
       |            |                |
   Inventory     Returns        Escalation
   Specialist   Specialist       Specialist
       |            |                |
       +------------+----------------+
                    |
                    v
             Grounded response
                    |
                    v
                  UI card
```

When `OPENAI_API_KEY` is configured, the selected CrewAI specialist produces the customer-facing response. Without a key, the same routing layer uses deterministic catalog/policy responses so local development and automated tests remain useful.

## Supported customer journeys

### Product availability

The service matches the customer's request against the canonical Northstar catalog and returns up to three relevant product records. Stock status is never fabricated.

### Returns and exchanges

The returns specialist explains the documented policy without inventing exceptions or eligibility decisions.

### Escalation

Unsupported requests receive a transparent handoff instead of a hallucinated answer.

### Contact capture

Requests that clearly ask for email follow-up can be routed into a contact-capture journey.

## Grounding and safety

Northstar AI does **not** fabricate:

- product names
- SKUs
- prices
- stock levels
- order numbers
- tracking details
- return eligibility decisions

Unknown information is treated as unknown and can be escalated to human support.

## Repository structure

```text
Northstar-AI-Support-Chatbot/
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── api/
│   │   └── main.py
│   ├── agents/
│   │   └── service.py
│   ├── crew/
│   │   ├── agents.py
│   │   ├── crew.py
│   │   └── tasks.py
│   ├── tests/
│   │   └── test_service.py
│   └── requirements.txt
├── data/
│   └── product_catalog.json
├── docs/
│   └── architecture.md
├── public/
│   └── images/              # product assets will be added here
├── .env.example
├── .gitignore
└── README.md
```

## Local development

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

Create `backend/.env` from the root `.env.example` or your preferred environment configuration. Add `OPENAI_API_KEY` to enable CrewAI LLM responses.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL=http://localhost:8000` in `frontend/.env` for local API calls.

## API

### `GET /api/health`

Returns service status and whether the LLM integration is configured.

### `POST /api/chat`

Request:

```json
{
  "message": "Is the Sovereign Shearling Trench in stock?",
  "session_id": "demo-session"
}
```

Response:

```json
{
  "message": "Yes — the Sovereign Shearling Trench is currently in stock.",
  "intent": "stock_availability",
  "products": [
    {
      "id": "NSJ001",
      "name": "Sovereign Shearling Trench",
      "category": "Jacket",
      "price": 2850,
      "stock": 40,
      "status": "IN_STOCK"
    }
  ]
}
```

## Testing

From `backend/`:

```bash
pytest
```

The tests cover catalog matching, out-of-stock handling, returns, and escalation behavior without requiring an external LLM call.

## Portfolio context

This project originated from **The Northstar Group Project** and is being independently expanded as a standalone portfolio application. The goal of the standalone build is to make the AI system, UX, backend, grounding strategy, and deployment independently demonstrable.
