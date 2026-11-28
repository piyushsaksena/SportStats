with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'const CRICKET_TEAMS =' in l:
        for j in range(i, len(lines)):
            if lines[j].strip().startswith('"') and lines[j].strip().endswith('": {'):
                print(f"Line {j+1}: {lines[j].strip()}")
            elif 'const FOOTBALL_TEAMS =' in lines[j] or 'const TENNIS_PLAYERS =' in lines[j] or '};' in lines[j] and lines[j].strip() == '};' and j > i + 1000:
                print(f"CRICKET_TEAMS ends at line {j+1}")
                break
        break
