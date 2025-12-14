# Connect Your SEO Backend to ChatGPT via Custom GPT

While ChatGPT doesn't support MCP natively, you can create a **Custom GPT** that calls your backend API directly.

---

##  Option 1: Custom GPT with Actions (For ChatGPT Plus Users)

### Prerequisites
- ChatGPT Plus or Enterprise account
- Your backend running and accessible via a public URL (or ngrok tunnel)

### Step 1: Make Backend Publicly Accessible

Since ChatGPT needs to access your API, you need to expose it. Use **ngrok**:

```bash
# Install ngrok: https://ngrok.com/download

# Start your backend
python main.py

# In another terminal, expose it
ngrok http 8000
```

Ngrok will give you a public URL like: `https://abc123.ngrok-free.app`

### Step 2: Create OpenAPI Schema

Create a file `openapi_schema.json`:

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "SEO Keyword Assistant API",
    "version": "1.0.0",
    "description": "Analyze URLs for SEO keywords and get suggestions"
  },
  "servers": [
    {
      "url": "https://YOUR-NGROK-URL.ngrok-free.app"
    }
  ],
  "paths": {
    "/api/products": {
      "get": {
        "operationId": "getProducts",
        "summary": "Get available product types",
        "responses": {
          "200": {
            "description": "List of products",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object"
                }
              }
            }
          }
        }
      }
    },
    "/api/competitors": {
      "post": {
        "operationId": "getCompetitors",
        "summary": "Get competitors for a product",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "product": {
                    "type": "string",
                    "enum": ["Assets", "Forms", "Sites"]
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Competitor list"
          }
        }
      }
    },
    "/api/analyze": {
      "post": {
        "operationId": "analyzeUrl",
        "summary": "Analyze URL for SEO keywords - returns article keywords, competitor keywords, and top 10 suggested keywords",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["url", "product", "time_range"],
                "properties": {
                  "url": {
                    "type": "string",
                    "description": "URL to analyze (must be from experienceleague.adobe.com)"
                  },
                  "product": {
                    "type": "string",
                    "enum": ["Assets", "Forms", "Sites"],
                    "description": "Product type"
                  },
                  "time_range": {
                    "type": "string",
                    "enum": ["week", "month", "year"],
                    "description": "Time range for search volume"
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "SEO analysis results with keywords"
          }
        }
      }
    },
    "/api/rewrite-content": {
      "post": {
        "operationId": "rewriteContent",
        "summary": "Rewrite content with SEO keywords",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["content", "target_keywords"],
                "properties": {
                  "content": {
                    "type": "string",
                    "description": "Original content to rewrite"
                  },
                  "target_keywords": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    },
                    "maxItems": 3,
                    "description": "Up to 3 target keywords"
                  },
                  "tone": {
                    "type": "string",
                    "enum": ["professional", "casual", "technical"],
                    "default": "professional"
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Rewritten content"
          }
        }
      }
    }
  }
}
```

### Step 3: Create Custom GPT

1. Go to https://chat.openai.com/gpts/editor
2. Click **Create**
3. Fill in:
   - **Name:** SEO Keyword Assistant
   - **Description:** Analyzes URLs for SEO keywords and provides suggestions
   - **Instructions:**
   
   ```
   You are an SEO Keyword Assistant that helps users analyze web pages and get keyword suggestions.
   
   Your capabilities:
   1. Get available products (Assets, Forms, Sites)
   2. Get competitors for each product
   3. Analyze URLs for SEO keywords - extracts article keywords, competitor keywords, and suggests top 10 high-volume keywords
   4. Rewrite content with target keywords
   
   When users ask to analyze a URL:
   - Always ask for the product type if not provided
   - Use "month" as default time_range
   - Present results clearly with keyword volumes
   - Highlight the top 10 suggested keywords
   
   Analysis takes 2-5 minutes as it analyzes competitor websites.
   ```

4. Click **Actions** → **Create new action**
5. Paste the OpenAPI schema (update the ngrok URL!)
6. **Save** and **Publish**

### Step 4: Use Your Custom GPT

Now you can chat with your Custom GPT:

```
Analyze this URL:
https://experienceleague.adobe.com/.../forms/...

Product: Forms
```

---

##  Security Note

**Ngrok URLs are temporary and public!** For production:

1. Deploy backend to a cloud server (AWS, Azure, GCP)
2. Add API key authentication
3. Use proper HTTPS certificates
4. Whitelist ChatGPT IPs if possible

---

## ️ Limitations

-  Requires ChatGPT Plus ($20/month)
-  Need public URL (ngrok or cloud deployment)
-  More complex setup than MCP
-  Additional latency through ngrok

---

##  Advantages

-  Works with ChatGPT
-  Can share with team
-  Web-based (no desktop app needed)
-  Mobile access via ChatGPT app

