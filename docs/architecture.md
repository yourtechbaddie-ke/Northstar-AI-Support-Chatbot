# Northstar AI architecture

## Render-first stack

### 1. Experience
React + Vite renders the conversational customer experience. Render serves the built frontend from the same public web service as the API.

### 2. API
FastAPI exposes `/api/health` and `/api/chat`. Requests are validated with Pydantic. Production uses same-origin API calls, so the browser does not depend on localhost or a separate frontend host.

### 3. Intelligence
Northstar uses direct OpenAI API calls when `OPENAI_API_KEY` is configured. There is no CrewAI agent framework. The assistant is deliberately constrained to supplied catalog and policy facts.

### 4. Data
The Render deployment uses the versioned Northstar catalog at `data/product_catalog.json` as its current source of truth. Firebase has been removed from the application and dependency graph.

## Request flow

```text
Customer message
      |
      v
FastAPI /api/chat
      |
      v
Intent + catalog matching
      |
      +------ availability ------> Verified catalog records
      |
      +------ returns -----------> Approved return policy
      |
      +------ general -----------> Direct AI support (when configured)
      |
      v
Grounded response
      |
      v
React frontend served by Render
```

## Data rule

The catalog is authoritative for product identity, price and stock. The assistant must never invent unsupported product, stock, pricing, delivery, discount or policy information.
