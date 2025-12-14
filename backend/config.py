"""
Configuration settings for the SEO Agent
"""

import os

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://forms-azure-openai-stg.openai.azure.com")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "Your-Key")

# LLM Provider
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "azure")

# Product-specific competitor configurations
# Only basic info - all URLs are discovered dynamically
PRODUCT_COMPETITORS = {
    "Assets": [
        {"name": "Bynder", "url": "https://www.bynder.com/"},
        {"name": "Brandfolder", "url": "https://brandfolder.com/"},
        {"name": "Canto", "url": "https://www.canto.com/"},
        {"name": "Widen", "url": "https://www.widen.com/"}
    ],
    "Forms": [
        {"name": "Typeform", "url": "https://www.typeform.com/"},
        {"name": "Jotform", "url": "https://www.jotform.com/"},
        {"name": "Formstack", "url": "https://www.formstack.com/"},
        {"name": "Wufoo", "url": "https://www.wufoo.com/"}
    ],
    "Sites": [
        {"name": "Wix", "url": "https://www.wix.com/"},
        {"name": "Squarespace", "url": "https://www.squarespace.com/"},
        {"name": "Webflow", "url": "https://webflow.com/"},
        {"name": "WordPress", "url": "https://wordpress.com/"}
    ]
}


# Default competitors (for backward compatibility)
COMPETITORS = PRODUCT_COMPETITORS["Forms"]

# SEMrush base URL format
SEMRUSH_URL_TEMPLATE = "https://www.semrush.com/analytics/keywordmagic/?q={keyword}&db=us"

# Server settings
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

