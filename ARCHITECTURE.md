# SEO Backend MCP Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐      │
│  │    Cursor    │   │  Claude AI   │   │   ChatGPT    │      │
│  │   IDE Chat   │   │   Desktop    │   │   w/ MCP     │      │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘      │
│         │                  │                  │                │
│         └──────────────────┴──────────────────┘                │
│                           │                                     │
│                  Natural Language Requests                      │
│                  "Get keyword suggestions"                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ MCP Protocol (stdio)
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    MCP SERVER LAYER                             │
│                   (mcp_server.py)                               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  MCP Tools (4)                                          │   │
│  │  ┌────────────────┐  ┌────────────────┐               │   │
│  │  │ get_products   │  │ get_competitors│               │   │
│  │  └────────────────┘  └────────────────┘               │   │
│  │  ┌────────────────┐  ┌────────────────┐               │   │
│  │  │ analyze_url  │  │ rewrite_content│               │   │
│  │  └────────────────┘  └────────────────┘               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Converts MCP calls → HTTP REST API calls                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ HTTP/REST (localhost:8000)
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    FASTAPI BACKEND                              │
│                      (main.py)                                  │
│                                                                 │
│  REST API Endpoints:                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ GET  /api/products        → List products               │   │
│  │ POST /api/competitors     → Get competitor list         │   │
│  │ POST /api/analyze        → Full SEO analysis         │   │
│  │ POST /api/rewrite-content → Rewrite with keywords      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Routes requests to: crew.py (SEOAgentCrew)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ Agent Orchestration
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   AGENT ORCHESTRATOR                            │
│                      (crew.py)                                  │
│                   SEOAgentCrew Class                            │
│                                                                 │
│  Manages 4 Specialized Agents:                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                                                        │    │
│  │  [1] CompetitorFetchingAgent                          │    │
│  │      • Gets competitor list for product               │    │
│  │      • Source: config.py                              │    │
│  │                                                        │    │
│  │  [2] KeywordExtractionAgent                           │    │
│  │      • Scrapes URL content                            │    │
│  │      • Extracts keywords with Azure OpenAI            │    │
│  │      • Gets search volumes from SEMrush               │    │
│  │                                                        │    │
│  │  [3] CompetitiveAnalysisAgent                         │    │
│  │      • Identifies article capability                  │    │
│  │      • Finds equivalent competitor pages              │    │
│  │      • Extracts competitor keywords                   │    │
│  │      • Ranks and suggests top 10 keywords             │    │
│  │                                                        │    │
│  │  [4] ContentRewritingAgent                            │    │
│  │      • Rewrites content with target keywords          │    │
│  │      • Maintains natural readability                  │    │
│  │      • Returns HTML-formatted content                 │    │
│  │                                                        │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 │                   │
┌────────────────▼──────┐   ┌────────▼───────────┐
│   BACKEND SERVICES    │   │   EXTERNAL APIs    │
│   (backend/)          │   │                    │
│                       │   │                    │
│  • scraper.py         │   │  • Azure OpenAI    │
│  • llm_client.py      │   │  • SEMrush         │
│  • semrush.py         │   │                    │
│  • config.py          │   │                    │
└───────────────────────┘   └────────────────────┘
```

## Request Flow: "Analyze URL for Keywords"

### Step-by-Step Flow

```
1. USER INPUT (Cursor Chat)
   ┌───────────────────────────────────────────────────────┐
   │ "Analyze this URL for SEO keywords:                   │
   │  https://experienceleague.adobe.com/.../forms/...     │
   │  Product: Forms, Time Range: month"                   │
   └───────────────────────────────────────────────────────┘
                           │
                           ▼
2. CURSOR AI PROCESSING
   ┌───────────────────────────────────────────────────────┐
   │ Identifies: analyze_url tool                          │
   │ Extracts parameters:                                  │
   │   - url: "https://..."                                │
   │   - product: "Forms"                                  │
   │   - time_range: "month"                               │
   └───────────────────────────────────────────────────────┘
                           │
                           ▼
3. MCP PROTOCOL CALL
   ┌───────────────────────────────────────────────────────┐
   │ MCP stdio communication                               │
   │ Tool: analyze_url                                     │
   │ Parameters: { url, product, time_range }              │
   └───────────────────────────────────────────────────────┘
                           │
                           ▼
4. MCP SERVER (mcp_server.py)
   ┌───────────────────────────────────────────────────────┐
   │ Receives MCP call                                     │
   │ Converts to HTTP request:                             │
   │ POST http://localhost:8000/api/analyze                │
   │ Body: { url, product, time_range }                    │
   └───────────────────────────────────────────────────────┘
                           │
                           ▼
5. FASTAPI BACKEND (main.py)
   ┌───────────────────────────────────────────────────────┐
   │ Validates URL format                                  │
   │ Validates product type                                │
   │ Calls: seo_crew.full_seo_analysis()                   │
   └───────────────────────────────────────────────────────┘
                           │
                           ▼
6. AGENT PIPELINE (crew.py)
   ┌───────────────────────────────────────────────────────┐
   │                                                       │
   │  AGENT 1: CompetitorFetchingAgent                  │
   │    ├─ Input: "Forms"                                 │
   │    └─ Output: [Typeform, Jotform, Formstack, Wufoo] │
   │                                                       │
   │              ▼                                        │
   │                                                       │
   │  AGENT 2: KeywordExtractionAgent                   │
   │    ├─ Scrape URL content (title, headings, text)     │
   │    ├─ Call Azure OpenAI to extract keywords          │
   │    ├─ Get search volumes from SEMrush                │
   │    └─ Output: Article keywords with volumes          │
   │              (e.g., "adaptive forms": 2400/month)    │
   │                                                       │
   │              ▼                                        │
   │                                                       │
   │  AGENT 3: CompetitiveAnalysisAgent                 │
   │    ├─ Identify article capability (e.g., "form       │
   │    │  builder features")                             │
   │    ├─ For each competitor:                           │
   │    │  ├─ Find equivalent capability page             │
   │    │  ├─ Scrape content                              │
   │    │  ├─ Extract keywords with OpenAI                │
   │    │  └─ Get search volumes                          │
   │    ├─ Merge all keywords (article + competitor)      │
   │    ├─ Deduplicate and rank by volume                 │
   │    └─ Output: Top 10 suggested keywords              │
   │                                                       │
   └───────────────────────────────────────────────────────┘
                           │
                           ▼
7. RESPONSE ASSEMBLY
   ┌───────────────────────────────────────────────────────┐
   │ {                                                     │
   │   "status": "success",                                │
   │   "title": "Create Adaptive Forms",                   │
   │   "article_keywords": [                               │
   │     { "keyword": "adaptive forms", "volume": 2400 },  │
   │     { "keyword": "form builder", "volume": 1800 }     │
   │   ],                                                  │
   │   "competitor_keywords": [                            │
   │     { "keyword": "drag drop forms", "volume": 3200 }, │
   │     { "keyword": "online form", "volume": 2900 }      │
   │   ],                                                  │
   │   "suggested_keywords": [                             │
   │     { "keyword": "online form", "volume": 3200 },     │
   │     { "keyword": "drag drop forms", "volume": 2900 }  │
   │   ]                                                   │
   │ }                                                     │
   └───────────────────────────────────────────────────────┘
                           │
                           ▼
8. MCP SERVER FORMATTING
   ┌───────────────────────────────────────────────────────┐
   │ Formats JSON as readable text:                       │
   │ "# SEO Analysis Results                              │
   │  **URL:** https://...                                │
   │  **Title:** Create Adaptive Forms                    │
   │                                                       │
   │  ## Article Keywords (15)                            │
   │  - adaptive forms (Volume: 2400)                     │
   │  ...                                                 │
   │                                                       │
   │  ##  SUGGESTED KEYWORDS (10)                       │
   │  1. online form (Volume: 3200)                       │
   │  2. drag drop forms (Volume: 2900)                   │
   │  ..."                                                │
   └───────────────────────────────────────────────────────┘
                           │
                           ▼
9. USER OUTPUT (Cursor Chat)
   ┌───────────────────────────────────────────────────────┐
   │ Formatted, readable keyword suggestions               │
   │ with volumes, sources, and SEMrush links              │
   └───────────────────────────────────────────────────────┘
```

## Data Flow Timing

| Step | Component | Time | Details |
|------|-----------|------|---------|
| 1-4 | User → MCP Server | < 1s | Nearly instant |
| 5 | FastAPI validation | < 0.1s | URL/product checks |
| 6.1 | Agent 1: Competitors | < 0.1s | From config |
| 6.2 | Agent 2: Keyword Extraction | 10-30s | Scraping + OpenAI + SEMrush |
| 6.3 | Agent 3: Competitive Analysis | 60-240s | 4 competitors × scraping/analysis |
| 7-9 | Response formatting | < 1s | JSON → Text |
| **TOTAL** | **Full Analysis** | **2-5 min** | Depends on competitor count |

## Component Communication

### MCP Protocol (stdio)
- **Transport:** stdin/stdout
- **Format:** JSON-RPC
- **Direction:** Bidirectional
- **Connection:** Persistent (one per session)

### HTTP REST API
- **Transport:** HTTP/1.1
- **Format:** JSON
- **Direction:** Request/Response
- **Connection:** Per-request

### Agent Communication
- **Type:** Function calls (synchronous/async)
- **Format:** Python objects/dicts
- **Direction:** Sequential pipeline
- **State:** Shared through function arguments

## Security Layers

```
┌─────────────────────────────────────────────┐
│  Layer 1: Local Only                        │
│  • MCP server runs on local machine         │
│  • No external network exposure             │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│  Layer 2: Localhost Backend                 │
│  • FastAPI on 127.0.0.1:8000                │
│  • Only accepts local connections           │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│  Layer 3: API Key Management                │
│  • Azure OpenAI key in config.py            │
│  • Protected by .gitignore                  │
│  • Environment variables supported          │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│  Layer 4: URL Validation                    │
│  • Only Adobe Experience League URLs        │
│  • Product-specific path validation         │
│  • Regex pattern matching                   │
└─────────────────────────────────────────────┘
```

## Technology Stack

### MCP Layer
- **Language:** Python 3.8+
- **MCP SDK:** `mcp[cli]` package
- **Protocol:** Model Context Protocol (stdio)
- **Format:** JSON-RPC

### Backend Layer
- **Framework:** FastAPI
- **Server:** Uvicorn (ASGI)
- **Async:** asyncio
- **Validation:** Pydantic

### Agent Layer
- **AI:** Azure OpenAI (GPT-4)
- **Scraping:** BeautifulSoup4 + httpx
- **SEO Data:** SEMrush API
- **Orchestration:** Custom Python classes

### Infrastructure
- **OS:** Windows/macOS/Linux
- **Python:** 3.8+
- **Network:** Localhost only
- **Storage:** None (stateless)

## Extensibility

### Adding New Tools

1. **Add Backend Endpoint** (main.py)
```python
@app.post("/api/new-feature")
async def new_feature(request: NewRequest):
    result = await seo_crew.new_method(...)
    return JSONResponse(content=result)
```

2. **Add Agent Method** (crew.py)
```python
async def new_method(self, ...):
    return await self.new_agent.execute(...)
```

3. **Add MCP Tool** (mcp_server.py)
```python
Tool(
    name="new_feature",
    description="Does something new",
    inputSchema={...}
)
```

4. **Handle Tool Call** (mcp_server.py)
```python
elif name == "new_feature":
    response = await client.post(
        f"{BACKEND_URL}/api/new-feature",
        json=arguments
    )
    ...
```

### Adding New Agents

1. Create agent file: `agents/new_agent.py`
2. Initialize in `crew.py`: `self.new_agent = NewAgent()`
3. Add method in `SEOAgentCrew` class
4. Use in existing or new endpoints

### Adding New Products

1. Update `PRODUCT_COMPETITORS` in `backend/config.py`
2. Add URL pattern in `URL_PATTERNS` in `main.py`
3. Restart backend
4. Product automatically available in all endpoints

## Performance Characteristics

### Fast Operations (< 1s)
- `get_products`
- `get_competitors`
- URL validation
- Response formatting

### Medium Operations (10-30s)
- Article scraping
- Keyword extraction (single page)
- Content rewriting (per chunk)

### Slow Operations (2-5 min)
- Full competitive analysis (4 competitors)
- Multiple competitor page discoveries
- Batch SEMrush API calls

### Optimization Opportunities
1. **Caching:** Cache competitor keywords (currently not implemented)
2. **Parallel Processing:** Analyze competitors in parallel
3. **Incremental Results:** Stream results as they complete
4. **Rate Limiting:** Batch SEMrush calls more efficiently

## Error Handling

```
User Error
    ↓
┌─────────────────────────┐
│ Input Validation        │ → 400 Bad Request
│ (FastAPI)               │   "Invalid URL"
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Agent Execution         │ → 500 Internal Error
│ (crew.py)               │   "Scraping failed"
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ MCP Server Handling     │ → TextContent with error
│ (mcp_server.py)         │   "Error calling backend"
└─────────────────────────┘
    ↓
User sees formatted error message
```

## Monitoring & Debugging

### Backend Logs
```bash
python main.py
# Shows:
# - Incoming requests
# - Agent execution
# - Keyword counts
# - Errors
```

### MCP Server Logs
```bash
python mcp_server.py
# (When run directly, but normally invisible via MCP)
```

### Test Suite
```bash
python test_mcp_server.py
# - Backend health check
# - API endpoint tests
# - Optional full analysis test
```

## Future Enhancements

1. **Streaming Results:** Stream keywords as they're discovered
2. **Caching Layer:** Redis for competitor keyword caching
3. **Database:** Store analysis history
4. **Authentication:** Multi-user support with API keys
5. **Rate Limiting:** Protect external APIs
6. **Batch Processing:** Analyze multiple URLs at once
7. **Async Competitors:** Parallel competitor analysis
8. **Smart Caching:** Time-based cache invalidation
9. **Monitoring:** Prometheus metrics
10. **Web UI:** Optional dashboard for direct access

---

This architecture provides a scalable, maintainable foundation for SEO keyword analysis accessible through AI assistants.


