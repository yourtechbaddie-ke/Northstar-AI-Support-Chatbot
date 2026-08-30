# Northstar AI architecture

## Layers

### 1. Experience
React + Vite renders the conversational customer experience. The visual system is Arctic Couture: Ink, Graphite, Deep Cobalt, Electric Cobalt, Arctic Blue, Porcelain, Snow, Champagne and Cloud.

### 2. API
FastAPI exposes `/api/health` and `/api/chat`. Requests are validated with Pydantic and the frontend communicates with the backend through `VITE_API_BASE_URL`.

### 3. Intelligence
CrewAI provides specialist agents for inventory, returns and escalation. Routing is intentionally narrow: the assistant should not fabricate unsupported facts.

### 4. Grounding
The canonical catalog is `data/product_catalog.json`, derived from the Northstar Group Project inventory. Optional Firebase integration can be added as the live inventory source without changing the frontend contract.

## Agent model

```text
Customer message
      |
      v
Intent / contact detection
      |
      +------ stock ------> Inventory Specialist
      |
      +------ return -----> Returns Specialist
      |
      +------ other ------> Escalation Specialist
      |
      v
Grounded response
```

## Data rule

The catalog is the authoritative source for product identity, price and stock in the standalone demo. Firebase should become authoritative for live stock once configured and verified. Unknown information must remain unknown.
