# How to Integrate MCP with Cursor - Step by Step

This guide shows you exactly how to connect your SEO backend to Cursor so you can ask for keyword suggestions directly in the chat.

---

##  Prerequisites

Before starting, make sure you have:
1.  Python installed
2.  This project downloaded/cloned

---

##  Step 1: Install Dependencies (30 seconds)

Open PowerShell or Terminal in this project folder and run:

```bash
pip install -r requirements.txt
```

This installs all required packages including the MCP library.

---

##  Step 2: Start Your Backend (30 seconds)

The MCP server needs your backend running to work.

**Option A - Windows (Easy):**
```bash
start_backend.bat
```

**Option B - Any OS:**
```bash
python main.py
```

**You should see:**
```
[SEOAgentCrew] Initializing 4 agents...
[SEOAgentCrew] All agents initialized
INFO:     Uvicorn running on http://127.0.0.1:8000
```

 **Keep this terminal window open!** Don't close it while using the MCP tools.

---

##  Step 3: Test Backend is Working (30 seconds)

Open a **NEW** terminal window (keep the backend running) and run:

```bash
python test_mcp_server.py
```

**You should see:**
```
 Checking if backend is running...
 Backend server is running!
 Test 1: Get Products - passed
 Test 2: Get Competitors - passed
 All tests completed!
```

If you see errors, make sure the backend (Step 2) is still running.

---

## ️ Step 4: Configure Cursor (2 minutes)

Now we'll tell Cursor about your MCP server.

### Method 1: Using the Template (Easiest)

1. **Open the template file:**
   - Open `cursor_settings_template.json` in this project

2. **Copy the path:**
   - You'll see a line like: `"C:\\Users\\ruchitas\\Desktop\\Cursor Folders\\seo-backend MCP\\mcp_server.py"`
   - **Update this path** to match where YOU saved this project
   - Keep the double backslashes `\\` on Windows
   - On Mac/Linux, use forward slashes: `/Users/yourname/projects/seo-backend MCP/mcp_server.py`

3. **Open Cursor Settings:**
   - In Cursor, press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
   - Type: "Preferences: Open User Settings (JSON)"
   - Press Enter

4. **Add MCP Configuration:**
   - If your settings file is empty or has just `{}`, replace everything with the content from `cursor_settings_template.json`
   - If you already have settings, add the `"mcp.servers"` section inside the existing `{}`

**Example - Empty Settings:**
```json
{
  "mcp.servers": {
    "seo-keyword-assistant": {
      "command": "python",
      "args": ["C:\\Users\\YOUR_USERNAME\\path\\to\\seo-backend MCP\\mcp_server.py"],
      "env": {}
    }
  }
}
```

**Example - Existing Settings:**
```json
{
  "editor.fontSize": 14,
  "editor.tabSize": 2,
  "mcp.servers": {
    "seo-keyword-assistant": {
      "command": "python",
      "args": ["C:\\Users\\YOUR_USERNAME\\path\\to\\seo-backend MCP\\mcp_server.py"],
      "env": {}
    }
  }
}
```

5. **Save the file** (Ctrl+S or Cmd+S)

6. **Restart Cursor** completely (close and reopen)

### Method 2: Manual Configuration

If you prefer to type it yourself:

**Windows:**
```json
{
  "mcpservers": {
    "seo-keyword-assistant": {
      "command": "python",
      "args": ["C:\\Users\\YOUR_USERNAME\\Desktop\\Cursor Folders\\seo-backend MCP\\mcp_server.py"],
      "env": {}
    }
  }
}
```

**Mac:**
```json
{
  "mcpservers": {
    "seo-keyword-assistant": {
      "command": "python3",
      "args": ["/Users/YOUR_USERNAME/projects/seo-backend MCP/mcp_server.py"],
      "env": {}
    }
  }
}
```

**Linux:**
```json
{
  "mcp.servers": {
    "seo-keyword-assistant": {
      "command": "python3",
      "args": ["/home/YOUR_USERNAME/projects/seo-backend MCP/mcp_server.py"],
      "env": {}
    }
  }
}
```

**Important Notes:**
- Replace `YOUR_USERNAME` and the path with your actual project location
- On Windows, use double backslashes `\\`
- On Mac/Linux, you might need `python3` instead of `python`
- Make sure the path is correct - copy it from File Explorer/Finder

---

##  Step 5: Test in Cursor (30 seconds)

1. **Open Cursor Chat:**
   - Press `Ctrl+L` (Windows/Linux) or `Cmd+L` (Mac)
   - Or click the chat icon in the sidebar

2. **Try this test command:**
   ```
   Get me the available products from the SEO keyword assistant
   ```

3. **You should see:**
   ```
   Available Products:
   - Assets
   - Forms
   - Sites
   ```

 **It works!** Your MCP server is connected to Cursor!

---

##  Step 6: Try a Real Analysis

Now try getting actual keyword suggestions:

**In Cursor Chat, type:**
```
Analyze this URL for SEO keywords:

https://experienceleague.adobe.com/en/docs/experience-manager-cloud-service/content/forms/adaptive-forms-authoring/authoring-adaptive-forms-foundation-components/create-an-adaptive-form-on-forms-cs

Product: Forms
Time Range: month
```

**What happens:**
- ⏳ Analysis takes 2-5 minutes (normal - it's analyzing 4 competitors!)
- ⏳ Cursor will show "Thinking..." or loading indicator
-  You'll get back:
  - Article keywords from the URL
  - Competitor keywords
  - **Top 10 suggested high-volume keywords** 

---

##  What You Can Do Now

### 1. Get Keyword Suggestions
```
I need keyword suggestions for this Forms article:
https://experienceleague.adobe.com/.../forms/...
```

### 2. Check Competitors
```
What are the competitors for Forms?
```

### 3. Get Available Products
```
What products are available?
```

### 4. Rewrite Content for SEO
```
Rewrite this content to include "adaptive forms", "form builder", "digital forms":

Create beautiful forms in minutes with our intuitive interface...
```

---

##  How to Find Your Project Path

### Windows:
1. Open File Explorer
2. Navigate to your project folder
3. Click on the address bar at the top
4. Copy the path (e.g., `C:\Users\YourName\Desktop\seo-backend MCP`)
5. In the JSON, replace `\` with `\\` (double backslashes)
   - Example: `C:\\Users\\YourName\\Desktop\\seo-backend MCP\\mcp_server.py`

### Mac:
1. Open Finder
2. Navigate to your project folder
3. Right-click on the folder → Get Info
4. Copy the path from "Where:"
5. Add `/mcp_server.py` to the end
   - Example: `/Users/YourName/projects/seo-backend MCP/mcp_server.py`

### Linux:
1. Open Terminal
2. Navigate to your project folder: `cd /path/to/project`
3. Run: `pwd`
4. Copy the output and add `/mcp_server.py`
   - Example: `/home/yourname/projects/seo-backend MCP/mcp_server.py`

---

##  Troubleshooting

### "Tool not found" or "MCP server not available"

**Fix:**
1. Make sure you **restarted Cursor** after adding the configuration
2. Check the path in your settings is correct
3. Try running the MCP server manually to see errors:
   ```bash
   python mcp_server.py
   ```
4. On Mac/Linux, try `python3` instead of `python`

### "Connection refused" or "Backend not running"

**Fix:**
1. Make sure the backend is running: `python main.py`
2. Check it's running on port 8000: Open browser to `http://localhost:8000/health`
3. You should see: `{"status":"healthy","service":"Competitive Vocabulary Intelligence Agent"}`

### "Cannot find python" or "command not found"

**Fix:**
1. Check Python is installed: `python --version`
2. On Mac/Linux, try `python3` instead
3. Make sure Python is in your PATH
4. Update the Cursor settings to use the full path to Python:
   ```json
   "command": "C:\\Python312\\python.exe",  // Windows
   "command": "/usr/bin/python3",           // Mac/Linux
   ```

### "Invalid URL"

**Fix:**
Make sure your URL matches the product:
- **Forms:** `https://experienceleague.adobe.com/.../content/forms/...`
- **Assets:** `https://experienceleague.adobe.com/.../content/assets/...`
- **Sites:** `https://experienceleague.adobe.com/.../content/sites/...`

### MCP server starts but tools don't work

**Fix:**
1. Check backend logs in the terminal where you ran `python main.py`
2. Look for error messages
3. Make sure all dependencies are installed: `pip install -r requirements.txt`
4. Try testing outside Cursor: `python test_mcp_server.py`

---

##  Checklist - Is Everything Working?

Go through this checklist:

- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Backend is running: `python main.py` (in separate terminal)
- [ ] Backend responds: Visit `http://localhost:8000/health` in browser
- [ ] Tests pass: `python test_mcp_server.py` shows all green checkmarks
- [ ] Cursor settings updated with correct path to `mcp_server.py`
- [ ] Path uses correct slashes (Windows: `\\`, Mac/Linux: `/`)
- [ ] Cursor was restarted after changing settings
- [ ] Test command works: "Get me the available products"

If all boxes are checked , you're ready to use it!

---

##  Tips for Daily Use

### Always Start Backend First
Before using MCP tools in Cursor:
1. Open terminal
2. Run `python main.py` (or `start_backend.bat` on Windows)
3. Keep it running
4. Now use Cursor

### Check Backend is Running
If tools stop working:
1. Check the terminal where backend is running
2. Look for error messages
3. If it stopped, restart it

### Be Patient with Analysis
Full URL analysis takes 2-5 minutes because it:
- Scrapes your article
- Analyzes 4 competitor websites
- Gets search volumes for all keywords
- Ranks and suggests top 10

This is normal!  Grab a coffee while it works.

---

##  Example Workflow

Here's a typical workflow:

1. **Morning:** Start backend
   ```bash
   python main.py
   ```

2. **In Cursor:** Ask for keyword suggestions
   ```
   Analyze this Forms article for keywords:
   [paste URL]
   ```

3. **Get Results:** 2-5 minutes later, get top 10 keywords

4. **Use Keywords:** Incorporate them into your content

5. **Optimize More:** Ask Cursor to rewrite sections with the keywords

6. **End of Day:** Stop the backend (Ctrl+C in terminal)

---

##  Next Steps

1.  Complete the setup above
2.  Try the test command
3.  Analyze a real URL
4.  Use the suggested keywords in your content
5.  Check [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for more examples

---

##  Still Having Issues?

1. **Check the backend terminal** for error messages
2. **Run the test:** `python test_mcp_server.py`
3. **Verify Python path** in Cursor settings is correct
4. **Check all file paths** - common issue!
5. **Review [MCP_SETUP.md](MCP_SETUP.md)** for more detailed troubleshooting

---

**You're all set!**  Start getting keyword suggestions directly in Cursor!

