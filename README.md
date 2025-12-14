# SEO Agent Backend with MCP Integration

Multi-agent SEO analysis system using CrewAI framework with Azure OpenAI.

**🆕 NEW: Now accessible via MCP (Model Context Protocol)** - Use directly in Cursor, Claude, or ChatGPT!

---

##  Quick Start with MCP (5 minutes)

Get keyword suggestions directly in Cursor:

1. **Install & Start Backend:**
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

2. **Test It Works:**
   ```bash
   python test_mcp_server.py
   ```

3. **Configure Cursor:** Copy `cursor_settings_template.json` to your Cursor settings

4. **Use It:** Ask Cursor - *"Get me keyword suggestions for [URL]"*

 **Full MCP Setup:** See [QUICK_START.md](QUICK_START.md) for detailed instructions

---

## Architecture

The system consists of four specialized agents:

### 1. Product Selection & Competitor Fetching Agent
- Fetches competitor list based on product selection (Assets / Forms / Sites)
- Retrieves competitors silently from `backend/config.py`
- No direct output to user

### 2. Keyword Extraction Agent
- Takes a URL as input
- Performs web scraping to extract content
- Uses Azure OpenAI and SEMrush URL to generate keywords
- Returns keywords with search volume (week/month/year)

### 3. Competitive Keyword Analysis Agent
- Scrapes competitor websites (from config.py)
- Extracts competitor keywords using ChatGPT and SEMrush URL
- Produces keyword lists for each competitor
- Includes search volume based on user-selected time range

### 4. Content Rewriting Agent
- Rewrites content using up to 3 user-selected keywords
- Ensures SEO-optimized content aligned with keywords
- Maintains natural readability

## Project Structure

```
seo-backend/
├── backend/
│   ├── __init__.py
│   ├── config.py         # Configuration settings
│   ├── llm_client.py     # Azure OpenAI client
│   ├── scraper.py        # Web scraper
│   └── semrush.py        # SEMrush URL generator
├── agents/
│   ├── __init__.py
│   ├── competitor_agent.py
│   ├── keyword_extraction_agent.py
│   ├── competitive_analysis_agent.py
│   └── content_rewriting_agent.py
├── crew.py               # CrewAI orchestration
├── main.py               # FastAPI server
├── config.py             # Root config (imports from backend)
└── requirements.txt
```

##  Using via MCP (Recommended)

The easiest way to use this system is through MCP integration:

### In Cursor/ChatGPT, ask:

```
"Analyze this URL for SEO keywords:
https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/...

Product: Forms, Time Range: month"
```

**You'll get back:**
-  Article keywords (from the URL)
-  Competitor keywords (from Typeform, Jotform, etc.)
-  **Top 10 suggested high-volume keywords** 

### Available MCP Tools:
- `get_products` - List available products
- `get_competitors` - Get competitors for a product
- `analyze_url` - **Main tool** - Full SEO analysis with keyword suggestions
- `rewrite_content` - Rewrite content with SEO keywords

 **Setup Guide:** [QUICK_START.md](QUICK_START.md)

---

##  API Endpoints (Direct Access)

You can also use the REST API directly:

### Main Analysis Endpoint
```
POST /api/analyze
{
    "url": "https://experienceleague.adobe.com/.../forms/...",
    "product": "Forms",  // Assets, Forms, or Sites
    "time_range": "month"  // week, month, or year
}
```

Returns:
- Article keywords
- Competitor keywords  
- Suggested keywords (top 10 high-volume)

### Other Endpoints
```
GET  /health                  # Health check
GET  /api/products            # List products
POST /api/competitors         # Get competitors for product
POST /api/rewrite-content     # Rewrite content with keywords
```

 **Full API Documentation:** `http://localhost:8000/docs` (when server is running)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (optional - defaults are provided):
```bash
export AZURE_OPENAI_ENDPOINT="your-endpoint"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"
export AZURE_OPENAI_API_VERSION="2024-02-01"
export AZURE_OPENAI_API_KEY="your-api-key"
```

3. Run the server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## Configuration

Edit `backend/config.py` to customize:
- Azure OpenAI settings
- Product competitors
- SEMrush URL template
- Server settings

### Product Competitors

```python
PRODUCT_COMPETITORS = {
    "Assets": [...],
    "Forms": [...],
    "Sites": [...]
}
```

## Time Range Options

Search volume can be fetched for:
- `week` - Weekly search volume
- `month` - Monthly search volume (default)
- `year` - Yearly search volume

---

##  Documentation

- ** Quick Start (MCP):** [QUICK_START.md](QUICK_START.md) - Get up and running in 5 minutes
- ** Full MCP Setup:** [MCP_SETUP.md](MCP_SETUP.md) - Detailed setup instructions
- ** Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and data flow
- ** Summary:** [MCP_INTEGRATION_SUMMARY.md](MCP_INTEGRATION_SUMMARY.md) - What was created

---

##  Use Cases

### 1. Get Keyword Suggestions for an Article
**Via Cursor:**
```
"I need keyword suggestions for this Forms article:
https://experienceleague.adobe.com/.../forms/create-an-adaptive-form-..."
```

**Result:** Top 10 high-volume keywords based on article + competitor analysis

### 2. Competitive Analysis
**Via Cursor:**
```
"What are the competitors for Forms and what keywords do they rank for?"
```

**Result:** Competitor list + their top-ranking keywords

### 3. Content Optimization
**Via Cursor:**
```
"Rewrite this content to include 'adaptive forms', 'form builder', 'digital forms':
[Your content here]"
```

**Result:** SEO-optimized content with natural keyword integration

---

## ️ System Architecture

```
Cursor/ChatGPT
    ↓ (MCP Protocol)
MCP Server (mcp_server.py)
    ↓ (HTTP REST)
FastAPI Backend (main.py)
    ↓ (Orchestration)
4 Specialized Agents (crew.py)
    ├─ Agent 1: Competitor Fetching
    ├─ Agent 2: Keyword Extraction
    ├─ Agent 3: Competitive Analysis
    └─ Agent 4: Content Rewriting
```

 **Full Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)

---

##  Testing

### Quick Test (30 seconds)
```bash
python test_mcp_server.py
```

### Full Test with Analysis (2-5 minutes)
```bash
python test_mcp_server.py full
```

---

##  Troubleshooting

### "Backend is not running"
```bash
python main.py
```

### "MCP server not found"
1. Check Cursor settings path is correct
2. Restart Cursor
3. Verify: `python -c "import mcp.server; print('OK')"`

### "Invalid URL"
URL must match product type:
- Forms: `.../content/forms/...`
- Assets: `.../content/assets/...`
- Sites: `.../content/sites/...`

 **More Help:** [MCP_SETUP.md](MCP_SETUP.md#troubleshooting)

---

##  Security

-  Runs locally only (no external exposure)
-  API keys protected by `.gitignore`
-  URL validation (Adobe Experience League only)
-  Input validation on all endpoints

---

##  What's New?

**MCP Integration (Latest):**
-  Use directly in Cursor/ChatGPT/Claude
-  Natural language keyword requests
-  No need to call APIs directly
-  Formatted, readable results

**System Features:**
-  4 specialized AI agents
-  SEMrush integration for search volumes
-  Competitive keyword analysis
- ️ SEO content rewriting
-  Top 10 suggested keywords per analysis

