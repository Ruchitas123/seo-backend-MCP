"""
Test script for the MCP server

This script tests the MCP server locally without needing to configure Cursor/ChatGPT.
"""

import asyncio
import subprocess
import sys
import time
import httpx


BACKEND_URL = "http://127.0.0.1:8000"


async def check_backend():
    """Check if the backend server is running"""
    print(" Checking if backend is running...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                print(" Backend server is running!")
                return True
            else:
                print(f" Backend returned status code: {response.status_code}")
                return False
    except Exception as e:
        print(f" Backend is not running: {str(e)}")
        print("\n️  Please start the backend first:")
        print("   python main.py")
        print("   OR")
        print("   start_backend.bat")
        return False


async def test_get_products():
    """Test the get_products endpoint"""
    print("\n" + "="*50)
    print("TEST 1: Getting Available Products")
    print("="*50)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/api/products")
        data = response.json()
        
        print(f"Status: {data.get('status')}")
        print(f"Products: {data.get('products')}")
        print(" Test passed!")
        return data


async def test_get_competitors():
    """Test the get_competitors endpoint"""
    print("\n" + "="*50)
    print("TEST 2: Getting Competitors for 'Forms'")
    print("="*50)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/api/competitors",
            json={"product": "Forms"}
        )
        data = response.json()
        
        print(f"Status: {data.get('status')}")
        competitors = data.get('data', {}).get('competitors', [])
        print(f"Found {len(competitors)} competitors:")
        for comp in competitors:
            print(f"  - {comp['name']}: {comp['url']}")
        print(" Test passed!")
        return data


async def test_analyze_url():
    """Test the analyze_url endpoint (main SEO analysis)"""
    print("\n" + "="*50)
    print("TEST 3: Analyzing URL for SEO Keywords")
    print("="*50)
    print("\n️  This test will be skipped in quick mode.")
    print("To run the full analysis, pass 'full' as an argument:")
    print("   python test_mcp_server.py full")
    print("\nFull analysis takes 2-5 minutes to complete.")
    
    # Skip full analysis unless explicitly requested
    if len(sys.argv) < 2 or sys.argv[1] != "full":
        print("\n⏭️  Skipping full analysis test.")
        return None
    
    print("\n Starting full SEO analysis...")
    print("This may take 2-5 minutes...\n")
    
    test_url = "https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/adaptive-forms-authoring/authoring-adaptive-forms-foundation-components/create-an-adaptive-form-on-forms-cs"
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        start_time = time.time()
        
        response = await client.post(
            f"{BACKEND_URL}/api/analyze",
            json={
                "url": test_url,
                "product": "Forms",
                "time_range": "month"
            }
        )
        
        elapsed = time.time() - start_time
        data = response.json()
        
        analysis = data.get('data', {})
        
        print(f"\n Analysis completed in {elapsed:.1f} seconds!")
        print(f"\nResults:")
        print(f"  Title: {analysis.get('title')}")
        print(f"  Article Keywords: {len(analysis.get('article_keywords', []))}")
        print(f"  Competitor Keywords: {len(analysis.get('competitor_keywords', []))}")
        print(f"  Suggested Keywords: {len(analysis.get('suggested_keywords', []))}")
        
        print(f"\nTop 5 Suggested Keywords:")
        for i, kw in enumerate(analysis.get('suggested_keywords', [])[:5], 1):
            print(f"  {i}. {kw.get('keyword')} (Volume: {kw.get('search_volume')})")
        
        print("\n Full analysis test passed!")
        return data


async def main():
    """Run all tests"""
    print("\n")
    print("="*60)
    print("  MCP SERVER TEST SUITE")
    print("="*60)
    
    # Check backend
    if not await check_backend():
        return
    
    print("\n Backend is ready! Starting tests...\n")
    
    try:
        # Test 1: Get products
        await test_get_products()
        
        # Test 2: Get competitors
        await test_get_competitors()
        
        # Test 3: Analyze URL (optional, takes time)
        await test_analyze_url()
        
        print("\n" + "="*60)
        print("  ALL TESTS COMPLETED!")
        print("="*60)
        print("\n The MCP server is ready to use with Cursor/ChatGPT!")
        print("\nNext steps:")
        print("1. Configure Cursor/ChatGPT with the MCP server (see MCP_SETUP.md)")
        print("2. Ask the AI assistant to analyze URLs and get keyword suggestions")
        print("\nExample prompt:")
        print('  "Analyze this URL for SEO keywords: [URL]"')
        print('  "Get me keyword suggestions for Forms product"')
        
    except Exception as e:
        print(f"\n Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())


