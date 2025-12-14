"""
SEO Backend MCP Server

Exposes the SEO analysis backend as an MCP (Model Context Protocol) server
so it can be integrated with Cursor, ChatGPT, and other AI assistants.
"""

import asyncio
import httpx
import json
from typing import Any, Dict, List
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server

# Backend configuration
BACKEND_URL = "http://127.0.0.1:8000"
API_TIMEOUT = 300.0  # 5 minutes for long-running analyses

# Initialize MCP server
app = Server("seo-keyword-assistant")


def create_http_client() -> httpx.AsyncClient:
    """Create an async HTTP client for backend communication"""
    return httpx.AsyncClient(timeout=API_TIMEOUT)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available SEO analysis tools.
    """
    return [
        Tool(
            name="get_products",
            description="Get list of available product types (Assets, Forms, Sites)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_competitors",
            description="Get competitor list for a specific product type",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "Product type: Assets, Forms, or Sites",
                        "enum": ["Assets", "Forms", "Sites"]
                    }
                },
                "required": ["product"]
            }
        ),
        Tool(
            name="analyze_url",
            description=(
                "Perform comprehensive SEO analysis on a URL. "
                "Returns article keywords, competitor keywords, and suggested keywords with search volumes. "
                "This is the main tool for getting keyword suggestions. "
                "URL must be from Adobe Experience League docs for the specified product."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to analyze (must be from experienceleague.adobe.com)"
                    },
                    "product": {
                        "type": "string",
                        "description": "Product type: Assets, Forms, or Sites",
                        "enum": ["Assets", "Forms", "Sites"]
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range for search volume data",
                        "enum": ["week", "month", "year"],
                        "default": "month"
                    }
                },
                "required": ["url", "product", "time_range"]
            }
        ),
        Tool(
            name="rewrite_content",
            description=(
                "Rewrite content for SEO optimization using target keywords. "
                "Returns SEO-optimized content with HTML formatting. "
                "Accepts up to 3 keywords."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Original content to rewrite"
                    },
                    "target_keywords": {
                        "type": "array",
                        "description": "Target keywords for SEO optimization (max 3)",
                        "items": {"type": "string"},
                        "maxItems": 3,
                        "minItems": 1
                    },
                    "tone": {
                        "type": "string",
                        "description": "Writing tone",
                        "enum": ["professional", "casual", "technical"],
                        "default": "professional"
                    }
                },
                "required": ["content", "target_keywords"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent | EmbeddedResource]:
    """
    Handle tool calls and route them to the appropriate backend endpoint.
    """
    
    async with create_http_client() as client:
        try:
            if name == "get_products":
                # GET /api/products
                response = await client.get(f"{BACKEND_URL}/api/products")
                response.raise_for_status()
                data = response.json()
                
                products = data.get("products", [])
                result_text = "Available Products:\n"
                for product in products:
                    result_text += f"- {product}\n"
                
                return [TextContent(type="text", text=result_text)]
            
            elif name == "get_competitors":
                # POST /api/competitors
                product = arguments.get("product")
                
                response = await client.post(
                    f"{BACKEND_URL}/api/competitors",
                    json={"product": product}
                )
                response.raise_for_status()
                data = response.json()
                
                competitors = data.get("data", {}).get("competitors", [])
                result_text = f"Competitors for {product}:\n\n"
                for comp in competitors:
                    result_text += f"• {comp['name']}\n"
                    result_text += f"  URL: {comp['url']}\n\n"
                
                return [TextContent(type="text", text=result_text)]
            
            elif name == "analyze_url":
                # POST /api/analyze - Main SEO analysis
                url = arguments.get("url")
                product = arguments.get("product")
                time_range = arguments.get("time_range", "month")
                
                # This is a long-running operation
                response = await client.post(
                    f"{BACKEND_URL}/api/analyze",
                    json={
                        "url": url,
                        "product": product,
                        "time_range": time_range
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract analysis results
                analysis = data.get("data", {})
                article_keywords = analysis.get("article_keywords", [])
                competitor_keywords = analysis.get("competitor_keywords", [])
                suggested_keywords = analysis.get("suggested_keywords", [])
                capability = analysis.get("capability", {})
                
                # Format the results
                result_text = f"# SEO Analysis Results\n\n"
                result_text += f"**URL:** {analysis.get('url', url)}\n"
                result_text += f"**Title:** {analysis.get('title', 'N/A')}\n"
                result_text += f"**Product:** {product}\n"
                result_text += f"**Time Range:** {time_range}\n\n"
                
                if capability:
                    result_text += f"**Identified Capability:** {capability.get('name', 'N/A')}\n"
                    result_text += f"**Description:** {capability.get('description', 'N/A')}\n\n"
                
                # Article Keywords
                result_text += f"## Article Keywords ({len(article_keywords)})\n"
                result_text += "Keywords extracted from the analyzed URL:\n\n"
                for kw in article_keywords[:20]:  # Show top 20
                    result_text += f"- **{kw.get('keyword')}**\n"
                    result_text += f"  - Volume: {kw.get('search_volume', 'N/A')}\n"
                    result_text += f"  - Source: {kw.get('source', 'N/A')}\n"
                    if kw.get('semrush_url'):
                        result_text += f"  - [View in SEMrush]({kw.get('semrush_url')})\n"
                    result_text += "\n"
                
                # Competitor Keywords
                result_text += f"\n## Competitor Keywords ({len(competitor_keywords)})\n"
                result_text += "Keywords that competitors rank for:\n\n"
                for kw in competitor_keywords[:20]:  # Show top 20
                    result_text += f"- **{kw.get('keyword')}**\n"
                    result_text += f"  - Volume: {kw.get('search_volume', 'N/A')}\n"
                    result_text += f"  - Competitor: {kw.get('competitor', 'N/A')}\n"
                    if kw.get('semrush_url'):
                        result_text += f"  - [View in SEMrush]({kw.get('semrush_url')})\n"
                    result_text += "\n"
                
                # Suggested Keywords (TOP 10 HIGH-VOLUME)
                result_text += f"\n##  SUGGESTED KEYWORDS ({len(suggested_keywords)})\n"
                result_text += "**Top 10 high-volume keywords combining article and competitor analysis:**\n\n"
                for i, kw in enumerate(suggested_keywords, 1):
                    result_text += f"{i}. **{kw.get('keyword')}**\n"
                    result_text += f"   - Volume: {kw.get('search_volume', 'N/A')}\n"
                    result_text += f"   - Source: {kw.get('source', 'N/A')}\n"
                    if kw.get('competitor'):
                        result_text += f"   - Found on: {kw.get('competitor')}\n"
                    if kw.get('semrush_url'):
                        result_text += f"   - [View in SEMrush]({kw.get('semrush_url')})\n"
                    result_text += "\n"
                
                # Add keyword mappings summary
                keyword_mappings = analysis.get("keyword_mappings", [])
                if keyword_mappings:
                    result_text += "\n## Keyword Relationships\n"
                    result_text += "How article keywords map to competitor keywords:\n\n"
                    for mapping in keyword_mappings[:10]:
                        article_kw_data = mapping.get('article_keyword', {})
                        article_kw = article_kw_data.get('keyword', 'N/A')
                        comp_kws = mapping.get('competitor_keywords', [])
                        if comp_kws:
                            comp_kw_names = [k.get('keyword', '') for k in comp_kws[:3]]
                            result_text += f"**{article_kw}** → {', '.join(comp_kw_names)}\n"
                
                return [TextContent(type="text", text=result_text)]
            
            elif name == "rewrite_content":
                # POST /api/rewrite-content
                content = arguments.get("content")
                target_keywords = arguments.get("target_keywords", [])
                tone = arguments.get("tone", "professional")
                
                response = await client.post(
                    f"{BACKEND_URL}/api/rewrite-content",
                    json={
                        "content": content,
                        "target_keywords": target_keywords,
                        "tone": tone
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                rewrite_result = data.get("data", {})
                rewritten_content = rewrite_result.get("rewritten_content", "")
                chunks_processed = rewrite_result.get("chunks_processed", 0)
                total_chunks = rewrite_result.get("total_chunks", 0)
                
                result_text = f"# SEO-Optimized Content\n\n"
                result_text += f"**Keywords Used:** {', '.join(target_keywords)}\n"
                result_text += f"**Tone:** {tone}\n"
                result_text += f"**Chunks Processed:** {chunks_processed}/{total_chunks}\n\n"
                result_text += "---\n\n"
                result_text += rewritten_content
                
                return [TextContent(type="text", text=result_text)]
            
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
        
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except:
                error_detail = str(e)
            
            return [TextContent(
                type="text",
                text=f"Error calling backend API: {error_detail}"
            )]
        
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]


async def main():
    """
    Run the MCP server using stdio transport.
    """
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

