with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'const CRICKET_TEAMS =' in l:
        print(f"CRICKET_TEAMS starts at line {i+1}")
        for j in range(i, min(i+500, len(lines))):
            if lines[j].strip().startswith('"') and lines[j].strip().endswith('": {') or lines[j].strip().endswith('": {'):
                print(f"Line {j+1}: {lines[j].strip()}")
            elif '};' in lines[j] and lines[j].startswith('    };'):
                print(f"CRICKET_TEAMS ends around line {j+1}")
                break
        break
