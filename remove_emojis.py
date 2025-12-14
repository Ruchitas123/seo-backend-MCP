import re
import os

emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U00002700-\U000027BF\U0001F1E0-\U0001F1FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002B50\U00002B55]')

files = [
    'README.md', 'CHATGPT_CUSTOM_GPT_SETUP.md', 'MCP_SETUP.md', 
    'USAGE_EXAMPLES.md', 'ARCHITECTURE.md', 'MCP_INTEGRATION_SUMMARY.md',
    'QUICK_START.md', 'CURSOR_INTEGRATION.md', 'test_mcp_server.py', 'mcp_server.py'
]

for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        cleaned = emoji_pattern.sub('', content)
        if content != cleaned:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(cleaned)
            print(f'Cleaned: {f}')

print('Done!')

