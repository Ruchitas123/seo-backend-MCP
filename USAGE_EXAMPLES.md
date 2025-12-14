# Usage Examples - SEO Keyword MCP Server

Complete examples showing how to use the SEO keyword assistant in Cursor, Claude, and ChatGPT.

---

##  Prerequisites

1.  Backend is running: `python main.py`
2.  MCP server is configured in Cursor/Claude (see [QUICK_START.md](QUICK_START.md))
3.  Tests passed: `python test_mcp_server.py`

---

## Example 1: Get Keyword Suggestions for an Article

###  Goal
You're writing an article about Adobe Forms and need keyword suggestions to improve SEO.

###  What You Ask (in Cursor/ChatGPT)

```
I need keyword suggestions for this article about creating adaptive forms:

https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/adaptive-forms-authoring/authoring-adaptive-forms-foundation-components/create-an-adaptive-form-on-forms-cs

Product: Forms
Time Range: month
```

###  What the AI Does

1. Recognizes you need the `analyze_url` tool
2. Extracts parameters:
   - URL: `https://experienceleague.adobe.com/.../forms/...`
   - Product: `Forms`
   - Time Range: `month`
3. Calls the MCP server
4. MCP server calls your backend `/api/analyze`
5. Your 4 agents analyze the URL + competitors

###  What You Get Back

```markdown
# SEO Analysis Results

**URL:** https://experienceleague.adobe.com/.../create-an-adaptive-form-on-forms-cs
**Title:** Create an Adaptive Form | AEM Forms as a Cloud Service
**Product:** Forms
**Time Range:** month

**Identified Capability:** Form Creation & Authoring
**Description:** Creating and building forms with drag-and-drop interface

## Article Keywords (15)
Keywords extracted from the analyzed URL:

- **adaptive forms**
  - Volume: 2,400/month
  - Source: Article
  - [View in SEMrush](https://www.semrush.com/...)

- **form builder**
  - Volume: 1,800/month
  - Source: Article
  - [View in SEMrush](https://www.semrush.com/...)

[... more keywords ...]

## Competitor Keywords (25)
Keywords that competitors rank for:

- **online form creator**
  - Volume: 3,200/month
  - Competitor: Typeform
  - [View in SEMrush](https://www.semrush.com/...)

- **drag and drop form**
  - Volume: 2,900/month
  - Competitor: Jotform
  - [View in SEMrush](https://www.semrush.com/...)

[... more keywords ...]

##  SUGGESTED KEYWORDS (10)
**Top 10 high-volume keywords combining article and competitor analysis:**

1. **online form creator**
   - Volume: 3,200/month
   - Source: Competitor Analysis
   - Found on: Typeform
   - [View in SEMrush](https://www.semrush.com/...)

2. **drag and drop form**
   - Volume: 2,900/month
   - Source: Competitor Analysis
   - Found on: Jotform
   - [View in SEMrush](https://www.semrush.com/...)

3. **adaptive forms**
   - Volume: 2,400/month
   - Source: Article
   - [View in SEMrush](https://www.semrush.com/...)

[... 7 more keywords ...]
```

###  How to Use These Results

1. **Focus on Top 10 Suggested Keywords** - These are the highest-volume, most relevant keywords
2. **Check SEMrush Links** - Click through to see search trends and difficulty
3. **Use in Content** - Incorporate these keywords naturally in your article
4. **Target High-Volume First** - Prioritize keywords with 2,000+ monthly searches

---

## Example 2: Check Competitors for a Product

###  Goal
You want to know which competitors to analyze for the Forms product.

###  What You Ask

```
What are the main competitors for the Forms product?
```

OR

```
Get competitors for Forms
```

###  What the AI Does

1. Recognizes you need the `get_competitors` tool
2. Calls MCP server with `product: Forms`
3. Returns competitor list from config

###  What You Get Back

```markdown
Competitors for Forms:

• Typeform
  URL: https://www.typeform.com/

• Jotform
  URL: https://www.jotform.com/

• Formstack
  URL: https://www.formstack.com/

• Wufoo
  URL: https://www.wufoo.com/
```

###  How to Use These Results

- Understand your competitive landscape
- Visit competitor sites to see their messaging
- Use for competitor keyword analysis (automatic in `analyze_url`)

---

## Example 3: Get All Available Products

###  Goal
You want to see what products are available for analysis.

###  What You Ask

```
What products are available in the SEO keyword assistant?
```

OR

```
Get available products
```

###  What the AI Does

1. Recognizes you need the `get_products` tool
2. Calls MCP server
3. Returns product list

###  What You Get Back

```markdown
Available Products:
- Assets
- Forms
- Sites
```

###  How to Use These Results

- Choose the right product for your URL analysis
- Each product has different competitors
- URLs must match the product type

---

## Example 4: Rewrite Content with SEO Keywords

###  Goal
You have article content that needs SEO optimization with specific keywords.

###  What You Ask

```
Rewrite this content to naturally include these keywords:
- "adaptive forms"
- "form builder"
- "digital forms"

Content:
"Our tool allows you to create forms quickly and easily. You can add fields,
customize layouts, and publish your forms in minutes. The interface is 
intuitive and requires no coding knowledge."
```

###  What the AI Does

1. Recognizes you need the `rewrite_content` tool
2. Extracts:
   - Content: Original text
   - Keywords: ["adaptive forms", "form builder", "digital forms"]
   - Tone: "professional" (default)
3. Calls MCP server
4. Backend Agent 4 rewrites the content

###  What You Get Back

```markdown
# SEO-Optimized Content

**Keywords Used:** adaptive forms, form builder, digital forms
**Tone:** professional
**Chunks Processed:** 1/1

---

Our adaptive forms builder allows you to create digital forms quickly and 
easily using our intuitive form builder interface. You can add fields, 
customize layouts, and publish your adaptive forms in minutes. The digital 
forms interface is user-friendly and requires no coding knowledge, making it 
perfect for building professional forms that engage your audience.
```

###  How to Use These Results

- Copy the rewritten content
- Keywords are naturally integrated
- Maintains readability and flow
- Can be used for up to 3 keywords at once

---

## Example 5: Compare Multiple URLs

###  Goal
You want to analyze multiple articles to find the best keywords across them.

###  What You Ask

```
Analyze these two Forms URLs and tell me the best keywords to target:

URL 1: https://experienceleague.adobe.com/.../forms/create-an-adaptive-form-on-forms-cs
URL 2: https://experienceleague.adobe.com/.../forms/adaptive-forms-authoring

Product: Forms
Time Range: month
```

###  What the AI Does

1. Calls `analyze_url` for first URL
2. Calls `analyze_url` for second URL
3. Compares results
4. Identifies common high-volume keywords
5. Provides recommendations

###  What You Get Back

```markdown
# Multi-URL Keyword Analysis

## URL 1 Analysis
[Full analysis results...]
Top Keywords: adaptive forms, form builder, digital forms

## URL 2 Analysis
[Full analysis results...]
Top Keywords: form authoring, create forms, form templates

## Combined Recommendations

**Keywords appearing in both articles (highest priority):**
1. adaptive forms (3,200/month)
2. form builder (2,900/month)

**Unique high-volume keywords:**
- From URL 1: digital forms (2,400/month)
- From URL 2: form templates (2,100/month)

**Recommendation:**
Focus on "adaptive forms" and "form builder" as these appear
across multiple articles and have high search volume.
```

---

## Example 6: Product-Specific Analysis

###  Goal
You want to analyze an Assets article (different product).

###  What You Ask

```
Analyze this Assets article for SEO keywords:

https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/assets/admin/asset-microservices-configure-and-use

Product: Assets
Time Range: month
```

###  What the AI Does

1. Validates URL matches Assets product path
2. Gets Assets competitors (Bynder, Brandfolder, Canto, Widen)
3. Analyzes article + Assets competitors
4. Returns Assets-specific keywords

###  What You Get Back

Similar to Example 1, but with:
- Assets-specific competitors (Bynder, Brandfolder, etc.)
- DAM-related keywords (digital asset management, asset library, etc.)
- Asset-focused capabilities

---

## Example 7: Error Handling

###  Goal
Understanding what happens when something goes wrong.

###  Wrong Product for URL

**You Ask:**
```
Analyze this URL:
https://experienceleague.adobe.com/.../forms/...

Product: Assets
```

**You Get:**
```
Error: Invalid URL. This URL is for Forms content, but Assets was selected.
Please use Product: Forms
```

###  Invalid URL

**You Ask:**
```
Analyze this URL:
https://example.com/my-article

Product: Forms
```

**You Get:**
```
Error: Invalid URL. URLs must be from Adobe Experience League:
https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/...
```

###  Backend Not Running

**You Get:**
```
Error calling backend API: Connection refused

Please make sure the backend is running:
  python main.py
```

---

## Example 8: Advanced Workflow

###  Goal
Complete SEO optimization workflow for a new article.

### Step 1: Analyze Existing Article
```
Analyze this article for keywords:
[URL]
Product: Forms
```

### Step 2: Get Top Keywords
From results, identify:
- Top 3 suggested keywords
- Highest volume (e.g., "online form creator", "adaptive forms", "form builder")

### Step 3: Rewrite Introduction
```
Rewrite this introduction with "online form creator", "adaptive forms", "form builder":

[Original introduction text]
```

### Step 4: Check Competitors
```
What do Typeform and Jotform focus on for form creation?
```

Use `analyze_url` on competitor pages or check the competitor keywords from Step 1.

### Step 5: Optimize Headings
```
Suggest SEO-optimized headings using these keywords:
- online form creator
- adaptive forms
- form builder

Current headings:
- How to Create a Form
- Adding Fields
- Publishing Your Form
```

###  Complete Optimized Article
- SEO-optimized introduction
- High-volume keywords naturally integrated
- Competitive positioning
- Optimized headings

---

##  Pro Tips

### 1. **Always Match Product to URL**
Forms URLs need Product: Forms, Assets URLs need Product: Assets, etc.

### 2. **Use Monthly Time Range for Most Cases**
`month` gives the best balance of specificity and volume.

### 3. **Focus on Top 10 Suggested Keywords**
These are already ranked by volume - no need to analyze all keywords.

### 4. **Check SEMrush Links**
Click through to see:
- Search trends
- Keyword difficulty
- Related keywords
- Competitor rankings

### 5. **Rewrite in Chunks**
For long articles, rewrite section by section with the rewrite tool.

### 6. **Use Competitor Keywords**
Often competitor keywords have higher volume than your article keywords.

### 7. **Be Patient with Analysis**
Full analysis takes 2-5 minutes because it:
- Scrapes your URL
- Analyzes 4 competitor sites
- Gets search volumes for all keywords
- This is normal for thorough analysis!

### 8. **Save Results**
Copy and paste results to a document for future reference.

---

##  Quick Command Reference

| What You Want | Example Prompt |
|---------------|---------------|
| Keyword suggestions | "Analyze [URL] for keywords, Product: Forms" |
| Competitor list | "Get competitors for Forms" |
| Available products | "What products are available?" |
| Rewrite content | "Rewrite this with keywords: [keywords]" |
| Compare URLs | "Analyze these URLs and compare keywords" |
| Check specific keyword | "Is 'adaptive forms' a good keyword?" |

---

##  Next Steps

1. Try Example 1 with your own URL
2. Use the suggested keywords in your content
3. Measure improvement in search rankings
4. Iterate based on results

Happy optimizing! 


