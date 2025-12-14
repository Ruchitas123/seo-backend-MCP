"""
SEO Agent Backend Server

FastAPI server with endpoints for SEO analysis.
Returns: Article Keywords, Competitor Keywords, Suggested Keywords
Excludes product names from keywords.
No fallbacks - raises exceptions on failure.
"""

import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

from backend.config import SERVER_HOST, SERVER_PORT, PRODUCT_COMPETITORS
from crew import seo_crew  # Import the agent orchestrator - ALL operations go through this

# Custom tag for API documentation
API_TAG = "Competitive Vocabulary Intelligence Agent APIs"

# URL Validation Patterns for each product type
URL_PATTERNS = {
    "Forms": {
        "pattern": r"^https://experienceleague\.adobe\.com/en/docs/experience-manager-cloud-service/content/forms(/.*)?$",
        "example": "https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/...",
        "description": "Forms URLs must start with: https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/"
    },
    "Assets": {
        "pattern": r"^https://experienceleague\.adobe\.com/en/docs/experience-manager-cloud-service/content/assets(/.*)?$",
        "example": "https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/assets/...",
        "description": "Assets URLs must start with: https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/assets/"
    },
    "Sites": {
        "pattern": r"^https://experienceleague\.adobe\.com/en/docs/experience-manager-cloud-service/content/sites(/.*)?$",
        "example": "https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/sites/...",
        "description": "Sites URLs must start with: https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/sites/"
    }
}


def validate_url_for_product(url: str, product: str) -> tuple[bool, str]:
    """
    Validate if the URL matches the expected pattern for the selected product.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if product not in URL_PATTERNS:
        return False, "Invalid URL"
    
    pattern_info = URL_PATTERNS[product]
    pattern = pattern_info["pattern"]
    
    if re.match(pattern, url):
        return True, ""
    else:
        return False, "Invalid URL"


app = FastAPI(
    title="Competitive Vocabulary Intelligence Agent",
    version="1.0.0",
    description="SEO Analysis - Article Keywords, Competitor Keywords, Suggested Keywords",
    openapi_tags=[
        {
            "name": API_TAG,
            "description": "APIs for keyword extraction, competitor analysis, and SEO optimization"
        }
    ],
    # Hide the Schemas section in Swagger UI
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Models
class AnalyzeRequest(BaseModel):
    url: str
    product: str  # Assets, Forms, Sites - REQUIRED
    time_range: str  # week, month, year - REQUIRED


class ProductRequest(BaseModel):
    product: str


class ContentRewriteRequest(BaseModel):
    content: str
    target_keywords: List[str]
    tone: str = "professional"


# Health Check
@app.get("/health", tags=[API_TAG])
async def health_check():
    """Check if the service is running"""
    return {"status": "healthy", "service": "Competitive Vocabulary Intelligence Agent"}


# Root endpoint
@app.get("/", tags=[API_TAG])
async def root():
    """Get API information and available endpoints"""
    return {
        "message": "Competitive Vocabulary Intelligence Agent API",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "GET /api/products": "Get product list (Forms, Assets, Sites)",
            "POST /api/competitors": "Get competitors for a product",
            "POST /api/analyze": "Analyze URL - returns Article, Competitor, Suggested keywords",
            "POST /api/rewrite-content": "Rewrite content for SEO"
        }
    }


# Get Products
@app.get("/api/products", tags=[API_TAG])
async def get_products():
    """Get list of available product types"""
    return {
        "status": "success",
        "products": list(PRODUCT_COMPETITORS.keys())
    }


# Get Competitors
@app.post("/api/competitors", tags=[API_TAG])
async def get_competitors(request: ProductRequest):
    """Get competitors for a specific product type"""
    if request.product not in PRODUCT_COMPETITORS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid product. Options: {list(PRODUCT_COMPETITORS.keys())}"
        )
    
    competitors = PRODUCT_COMPETITORS[request.product]
    return JSONResponse(content={
        "status": "success",
        "data": {
            "product": request.product,
            "competitors": competitors
        }
    })


# Main Analysis Endpoint - Uses ALL 4 AGENTS through seo_crew
@app.post("/api/analyze", tags=[API_TAG])
async def analyze_url(request: AnalyzeRequest):
    """
    Main SEO Analysis Endpoint - Uses All 4 Agents
    
    Agent Pipeline:
    1. CompetitorFetchingAgent - Gets competitor list for the product
    2. KeywordExtractionAgent - Scrapes URL and extracts article keywords
    3. CompetitiveAnalysisAgent - Gets competitor keywords for each article keyword
    
    Returns:
    - Article Keywords (from the URL)
    - Competitor Keywords (what competitors rank for)
    - Suggested Keywords (top 10 high-volume from both sources)
    
    URL Validation:
    - Forms: URL must be from experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/
    - Assets: URL must be from experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/assets/
    - Sites: URL must be from experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/sites/
    """
    print(f"\n[API] /api/analyze called")
    print(f"[API] URL: {request.url}")
    print(f"[API] Product: {request.product}")
    print(f"[API] Time Range: {request.time_range}")
    
    # Validate product
    if request.product not in PRODUCT_COMPETITORS:
        print(f"[API]  Invalid product: {request.product}")
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid product. Options: {list(PRODUCT_COMPETITORS.keys())}"
        )
    
    # Validate time_range
    if request.time_range not in ["week", "month", "year"]:
        print(f"[API]  Invalid time_range: {request.time_range}")
        raise HTTPException(status_code=400, detail="time_range must be: week, month, or year")
    
    url = request.url
    product = request.product
    time_range = request.time_range
    
    # Validate URL matches the selected product type
    is_valid, error_message = validate_url_for_product(url, product)
    if not is_valid:
        print(f"[API]  Invalid URL for product {product}: {url}")
        raise HTTPException(status_code=400, detail=error_message)
    
    print(f"[API]  Validation passed, starting analysis...")
    
    try:
        # ===== USE SEO_CREW (All 4 Agents) =====
        # This orchestrates: Agent 1 (Competitors) → Agent 2 (Keywords) → Agent 3 (Competitive Analysis)
        result = await seo_crew.full_seo_analysis(
            url=url,
            product=product,
            time_range=time_range
        )
        
        if result.get("status") == "error":
            print(f"[API]  Analysis error: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Analysis failed"))
        
        print(f"[API]  Analysis complete!")
        return JSONResponse(content={"status": "success", "data": result})
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API]  Exception: {str(e)[:200]}")
        raise HTTPException(status_code=500, detail=str(e)[:500])


# Content Rewriting - Uses ContentRewritingAgent
@app.post("/api/rewrite-content", tags=[API_TAG])
async def rewrite_content(request: ContentRewriteRequest):
    """
    Rewrite content for SEO optimization using ContentRewritingAgent
    
    Takes content and up to 3 target keywords, returns SEO-optimized content with HTML formatting.
    Uses chunked processing to handle long articles.
    """
    print(f"\n[API] /api/rewrite-content called")
    print(f"[API] Content length: {len(request.content)} chars")
    print(f"[API] Keywords: {request.target_keywords}")
    
    if len(request.target_keywords) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 keywords allowed")
    
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    
    if not request.target_keywords:
        raise HTTPException(status_code=400, detail="At least one keyword required")
    
    try:
        # Use ContentRewritingAgent through seo_crew
        result = await seo_crew.rewrite_content(
            content=request.content,
            target_keywords=request.target_keywords,
            tone=request.tone
        )
        
        if result.get("status") == "error":
            print(f"[API]  Rewrite error: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Content rewriting failed"))
        
        print(f"[API]  Rewrite complete! {result.get('chunks_processed', 0)}/{result.get('total_chunks', 0)} chunks")
        return JSONResponse(content={"status": "success", "data": result})
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API]  Rewrite exception: {str(e)[:200]}")
        raise HTTPException(status_code=500, detail=f"Content rewriting failed: {str(e)[:300]}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
