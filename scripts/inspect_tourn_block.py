with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

# Check current tournaments block
block_match = re.search(r'(<div class="flex items-center justify-between mb-4">.*?Official Competitions.*?</div>\s*<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3\.5">.*?</div>\s*</div>)', html, re.DOTALL)
if block_match:
    print("Found tournaments block! Length:", len(block_match.group(1)))
    print(block_match.group(1)[:500])
else:
    print("Tournaments block not found by regex")
