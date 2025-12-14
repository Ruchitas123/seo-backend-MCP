# MCP Server Setup Guide

This guide explains how to expose your SEO backend as an MCP (Model Context Protocol) server for integration with Cursor, ChatGPT, and other AI assistants.

## What is MCP?

MCP (Model Context Protocol) is a protocol that allows AI assistants to interact with external tools and services. By exposing your SEO backend as an MCP server, AI assistants can:

- Get keyword suggestions from your SEO analysis
- Analyze URLs for SEO keywords
- Get competitor keywords
- Rewrite content with SEO optimization

## Setup Instructions

### 1. Install Dependencies

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

This will install the `mcp` package along with other dependencies.

### 2. Start the Backend Server

The MCP server communicates with your FastAPI backend, so you need to start it first:

```bash
python main.py
```

This will start the backend server on `http://127.0.0.1:8000`.

**Important:** Keep this running in a separate terminal window.

### 3. Configure Cursor to Use the MCP Server

#### For Cursor:

1. Open Cursor Settings (Ctrl+Shift+P → "Preferences: Open Settings (JSON)")

2. Add the MCP server configuration to your Cursor settings. You need to add this to your user settings or workspace settings:

**On Windows:**
```json
{
  "mcp.servers": {
    "seo-keyword-assistant": {
      "command": "python",
      "args": ["C:\\Users\\ruchitas\\Desktop\\Cursor Folders\\seo-backend MCP\\mcp_server.py"],
      "env": {
        "AZURE_OPENAI_ENDPOINT": "https://forms-azure-openai-stg.openai.azure.com",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o",
        "AZURE_OPENAI_API_VERSION": "2024-02-01",
        "AZURE_OPENAI_API_KEY": "edd28de40ec043cea781abe3b4ce9936"
      }
    }
  }
}
```

**On macOS/Linux:**
```json
{
  "mcp.servers": {
    "seo-keyword-assistant": {
      "command": "python",
      "args": ["/path/to/your/project/mcp_server.py"],
      "env": {
        "AZURE_OPENAI_ENDPOINT": "https://forms-azure-openai-stg.openai.azure.com",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o",
        "AZURE_OPENAI_API_VERSION": "2024-02-01",
        "AZURE_OPENAI_API_KEY": "edd28de40ec043cea781abe3b4ce9936"
      }
    }
  }
}
```

3. Restart Cursor

#### For Claude Desktop (ChatGPT-style interface):

1. Create or edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

2. Add the MCP server configuration:

```json
{
  "mcpServers": {
    "seo-keyword-assistant": {
      "command": "python",
      "args": ["C:\\Users\\ruchitas\\Desktop\\Cursor Folders\\seo-backend MCP\\mcp_server.py"],
      "env": {
        "AZURE_OPENAI_ENDPOINT": "https://forms-azure-openai-stg.openai.azure.com",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o",
        "AZURE_OPENAI_API_VERSION": "2024-02-01",
        "AZURE_OPENAI_API_KEY": "edd28de40ec043cea781abe3b4ce9936"
      }
    }
  }
}
```

3. Restart Claude Desktop

### 4. Test the MCP Server

Once configured, you can test the MCP server by asking the AI assistant:

```
Can you get me the available products from the SEO keyword assistant?
```

Or:

```
Analyze this URL for SEO keywords: https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/adaptive-forms-authoring/authoring-adaptive-forms-foundation-components/create-an-adaptive-form-on-forms-cs

Use product: Forms, time_range: month
```

## Available MCP Tools

The MCP server exposes 4 tools:

### 1. `get_products`
Get list of available product types (Assets, Forms, Sites).

**Example:**
```
Get me the available products
```

### 2. `get_competitors`
Get competitor list for a specific product type.

**Parameters:**
- `product` (string): Assets, Forms, or Sites

**Example:**
```
Get competitors for the Forms product
```

### 3. `analyze_url` (Main Tool)
Perform comprehensive SEO analysis on a URL. Returns:
- Article keywords (from the URL)
- Competitor keywords (from competitor sites)
- Suggested keywords (top 10 high-volume)

**Parameters:**
- `url` (string): URL to analyze (must be from experienceleague.adobe.com)
- `product` (string): Assets, Forms, or Sites
- `time_range` (string): week, month, or year (default: month)

**Example:**
```
Analyze this URL for SEO keywords:
https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/adaptive-forms-authoring/authoring-adaptive-forms-foundation-components/create-an-adaptive-form-on-forms-cs

Product: Forms
Time Range: month
```

### 4. `rewrite_content`
Rewrite content for SEO optimization using target keywords.

**Parameters:**
- `content` (string): Original content to rewrite
- `target_keywords` (array): Target keywords (max 3)
- `tone` (string): professional, casual, or technical (default: professional)

**Example:**
```
Rewrite this content for SEO with keywords "adaptive forms", "form builder", "digital forms":

[Your content here]
```

## Example Conversations

### Getting Keyword Suggestions

**User:**
```
I need keyword suggestions for this article:
https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/adaptive-forms-authoring/authoring-adaptive-forms-foundation-components/create-an-adaptive-form-on-forms-cs

Product: Forms
```

**AI Assistant:**
The assistant will use the `analyze_url` tool and return:
- Article keywords extracted from your URL
- Competitor keywords from Forms competitors (Typeform, Jotform, etc.)
- Top 10 suggested high-volume keywords

### Rewriting Content

**User:**
```
Rewrite this content to include keywords "form builder", "drag and drop", "custom forms":

Create beautiful forms in minutes with our intuitive interface...
```

**AI Assistant:**
The assistant will use the `rewrite_content` tool to return SEO-optimized content.

## Troubleshooting

### Backend Not Running
**Error:** `Error calling backend API: Connection refused`

**Solution:** Make sure the FastAPI backend is running:
```bash
python main.py
```

### Invalid URL
**Error:** `Invalid URL`

**Solution:** Make sure the URL matches the selected product:
- Forms: `https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/...`
- Assets: `https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/assets/...`
- Sites: `https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/sites/...`

### MCP Server Not Recognized
**Error:** Tool not found

**Solution:**
1. Verify the MCP server configuration in your settings
2. Restart Cursor/Claude Desktop
3. Check that the `mcp` package is installed: `pip list | grep mcp`

### Long Response Times
The `analyze_url` tool performs comprehensive analysis which can take 2-5 minutes depending on:
- Number of keywords to analyze
- Number of competitors
- SEMrush API response times

This is normal behavior for thorough SEO analysis.

## Architecture

```
┌─────────────────┐
│  AI Assistant   │  (Cursor/ChatGPT)
│  (Claude/GPT)   │
└────────┬────────┘
         │ MCP Protocol
         │
┌────────▼────────┐
│   MCP Server    │  (mcp_server.py)
│   (This file)   │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│ FastAPI Backend │  (main.py)
│   SEO Agents    │
└─────────────────┘
         │
         ├─> Agent 1: Competitor Fetching
         ├─> Agent 2: Keyword Extraction
         ├─> Agent 3: Competitive Analysis
         └─> Agent 4: Content Rewriting
```

## Security Note

The `mcp_config.json` file contains your Azure OpenAI API key. Make sure to:
1. Add `mcp_config.json` to `.gitignore`
2. Never commit API keys to version control
3. Use environment variables for production deployments

## Next Steps

1.  Install dependencies
2.  Start the backend server
3.  Configure Cursor/Claude Desktop
4.  Test with a simple query
5.  Start using keyword suggestions in your workflow!

## Support

For issues or questions, refer to:
- MCP Documentation: https://github.com/modelcontextprotocol
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Project README: [README.md](./README.md)


