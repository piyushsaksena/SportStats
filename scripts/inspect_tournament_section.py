with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find("ICC Men's Cricket World Cup")
start_line = html[:idx].count('\n')
lines = html.splitlines()
print(f"Tournaments start around line {start_line+1}")
for i in range(start_line-5, min(start_line+75, len(lines))):
    print(f"{i+1}: {lines[i]}")
