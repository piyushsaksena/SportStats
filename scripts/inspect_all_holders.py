with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
matches = re.findall(r'[^\n]*holder[^\n]*', html, re.IGNORECASE)
print(f"Total lines mentioning 'holder': {len(matches)}")
for m in matches[:15]:
    print(" - ", m.strip())
