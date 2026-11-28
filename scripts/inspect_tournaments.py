with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
matches = re.findall(r'<div class="[^"]*rounded-2xl[^"]*border[^"]*p-4[^"]*">\s*<div[^>]*>.*?Current Holder.*?</div>', html, re.DOTALL | re.IGNORECASE)
print(f"Found {len(matches)} tournament cards with 'Current Holder'")
for m in matches[:5]:
    print("--- CARD ---")
    print(m[:300])

# Also check for "current_holder" or tournament in general
terms = ['ICC Men\'s Cricket World Cup', 'World Test Championship', 'T20 World Cup', 'Champions Trophy']
for t in terms:
    idx = html.find(t)
    if idx != -1:
        print(f"\nFound '{t}' around char {idx}:")
        print(html[idx:idx+400])
