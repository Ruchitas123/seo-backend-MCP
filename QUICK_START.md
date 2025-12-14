# Quick Start Guide - MCP Server for SEO Keywords

Get up and running with the SEO Keyword MCP server in 5 minutes!

##  Quick Setup (3 Steps)

### Step 1: Install Dependencies (30 seconds)

Open PowerShell/Terminal in this folder and run:

```bash
pip install -r requirements.txt
```

### Step 2: Start the Backend (30 seconds)

**Windows:**
```bash
start_backend.bat
```

**macOS/Linux:**
```bash
python main.py
```

Keep this terminal window open! The backend must be running for the MCP server to work.

### Step 3: Test It Works (30 seconds)

In a **NEW** terminal window:

```bash
python test_mcp_server.py
```

You should see:
-  Backend server is running!
-  Test 1: Get Products
-  Test 2: Get Competitors
-  All tests completed!

##  Using with Cursor

### Configure Cursor (2 minutes)

1. Open Cursor Settings:
   - Press `Ctrl+,` (Windows/Linux) or `Cmd+,` (Mac)
   - Or: `Ctrl+Shift+P` → "Preferences: Open Settings (JSON)"

2. Add this to your settings file:

```json
{
  "mcp.servers": {
    "seo-keyword-assistant": {
      "command": "python",
      "args": ["C:\\Users\\ruchitas\\Desktop\\Cursor Folders\\seo-backend MCP\\mcp_server.py"],
      "env": {}
    }
  }
}
```

**Important:** Update the path in `args` to match your project location!

3. Restart Cursor

### Try It Out!

In Cursor chat, ask:

```
Get me the available products from the SEO keyword assistant
```

Or:

```
Analyze this URL for SEO keywords:
https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/adaptive-forms-authoring/authoring-adaptive-forms-foundation-components/create-an-adaptive-form-on-forms-cs

Product: Forms, Time Range: month
```

##  Example Use Cases

### 1. Get Keyword Suggestions for an Article

**Prompt:**
```
I need keyword suggestions for this Adobe Forms article:
https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/...

Use product: Forms, time_range: month
```

**Result:** You'll get:
- Keywords from the article
- Keywords competitors rank for
- Top 10 suggested high-volume keywords

### 2. Check What Competitors Rank For

**Prompt:**
```
Get competitors for the Forms product
```

**Result:** List of Forms competitors (Typeform, Jotform, etc.)

### 3. Rewrite Content for SEO

**Prompt:**
```
Rewrite this content to include keywords "adaptive forms", "form builder", "digital forms":

Create beautiful forms in minutes with our intuitive interface...
```

**Result:** SEO-optimized content with your keywords naturally integrated

##  Troubleshooting

### "Backend is not running"

**Fix:** Start the backend first:
```bash
python main.py
```
OR
```bash
start_backend.bat
```

### "MCP server not found in Cursor"

**Fix:**
1. Check the path in your Cursor settings is correct
2. Restart Cursor
3. Make sure `mcp` package is installed: `pip install mcp`

### "Invalid URL"

**Fix:** URLs must match the product type:
- **Forms:** `https://experienceleague.adobe.com/.../content/forms/...`
- **Assets:** `https://experienceleague.adobe.com/.../content/assets/...`
- **Sites:** `https://experienceleague.adobe.com/.../content/sites/...`

##  Available Tools

The MCP server exposes 4 tools you can use through Cursor/ChatGPT:

| Tool | Description | Example Prompt |
|------|-------------|----------------|
| `get_products` | List available products | "Get available products" |
| `get_competitors` | Get competitors for a product | "Get competitors for Forms" |
| `analyze_url` | **Main tool** - Full SEO analysis | "Analyze this URL: [URL]" |
| `rewrite_content` | Rewrite content with keywords | "Rewrite this content with keywords..." |

##  Learn More

- Full setup guide: [MCP_SETUP.md](MCP_SETUP.md)
- Backend API docs: [README.md](README.md)
- Test the backend directly: `python test_mcp_server.py full`

##  Tips

1. **Keep Backend Running:** The backend must be running in a separate terminal
2. **Analysis Takes Time:** Full URL analysis takes 2-5 minutes (it's analyzing competitors!)
3. **Use Suggested Keywords:** The tool returns top 10 high-volume keywords - these are gold!
4. **Product Must Match URL:** Make sure your URL matches the product type you select

##  You're Ready!

Your SEO Keyword Assistant is now integrated with Cursor. Just ask for keyword suggestions and let the AI do the work!

**Example workflow:**
1. You're writing an article about Adobe Forms
2. Ask Cursor: "Give me keyword suggestions for this Forms article: [URL]"
3. Get back article keywords, competitor keywords, and top 10 suggestions
4. Use those keywords to optimize your content
5. Ask Cursor to rewrite sections with the best keywords

Happy optimizing! 


