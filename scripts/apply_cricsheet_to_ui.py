import json, re

# Load payload
with open('cricket_dataset_starter/data/processed/sportstats_sync_payload.json', 'r', encoding='utf-8') as f:
    payload = json.load(f)

recent_matches = payload['recent_cricsheet_matches']
team_histories = payload['team_histories']

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update CRICSHEET_ALL_MATCHES (first 50 matches)
cricsheet_json_str = json.dumps(recent_matches[:50], ensure_ascii=False)
html = re.sub(
    r'const CRICSHEET_ALL_MATCHES = \[.*?\];',
    f'const CRICSHEET_ALL_MATCHES = {cricsheet_json_str};',
    html,
    flags=re.DOTALL
)

# 2. Update CRICKET_TEAMS["india"].matches
india_matches_json = json.dumps(team_histories['India'], ensure_ascii=False, indent=8)
# Find CRICKET_TEAMS = { ... india: { ... matches: [...] ... }
# Let's replace india matches array
pattern_ind = r'("india":\s*\{[^}]*?"matches":\s*)\[.*?\](\s*,\s*"stats")'
match_ind = re.search(pattern_ind, html, re.DOTALL)
if match_ind:
    html = html[:match_ind.start(1)] + match_ind.group(1) + india_matches_json + match_ind.group(2) + html[match_ind.end(2):]
    print("Updated CRICKET_TEAMS['india'].matches")
else:
    print("Pattern for india matches not found, checking alternate")

# 3. Update CRICKET_TEAMS["new-zealand"].matches
nz_matches_json = json.dumps(team_histories['New Zealand'], ensure_ascii=False, indent=8)
pattern_nz = r'("new-zealand":\s*\{[^}]*?"matches":\s*)\[.*?\](\s*,\s*"stats")'
match_nz = re.search(pattern_nz, html, re.DOTALL)
if match_nz:
    html = html[:match_nz.start(1)] + match_nz.group(1) + nz_matches_json + match_nz.group(2) + html[match_nz.end(2):]
    print("Updated CRICKET_TEAMS['new-zealand'].matches")
else:
    print("Pattern for nz matches not found, checking alternate")

# 4. Update cricket-match-picker options
picker_options = [
    '<option value="cricsheet-1539442">India tour of New Zealand 2026 • 1st Test (19–23 Nov 2026) — COMPLETED</option>',
    '<option value="cricsheet-1539441">India tour of New Zealand 2026 • 5th ODI (15 Nov 2026) — COMPLETED</option>',
    '<option value="cricsheet-1539440">India tour of New Zealand 2026 • 4th ODI (13 Nov 2026) — COMPLETED</option>',
    '<option value="cricsheet-1539438">India tour of New Zealand 2026 • 2nd ODI (07 Nov 2026) — COMPLETED</option>',
    '<option value="cricsheet-1539437">India tour of New Zealand 2026 • 1st ODI (04 Nov 2026) — COMPLETED</option>',
    '<option value="cricsheet-1539436">India tour of New Zealand 2026 • 5th T20I (01 Nov 2026) — COMPLETED</option>',
    '<option value="cricsheet-1539435">India tour of New Zealand 2026 • 4th T20I (30 Oct 2026) — COMPLETED</option>',
    '<option value="cricsheet-1539434">India tour of New Zealand 2026 • 3rd T20I (27 Oct 2026) — COMPLETED</option>',
    '<option value="cricsheet-1539433">India tour of New Zealand 2026 • 2nd T20I (24 Oct 2026) — COMPLETED</option>',
    '<option value="cricsheet-1539432">India tour of New Zealand 2026 • 1st T20I (22 Oct 2026) — COMPLETED</option>'
]
opts_html = "".join(picker_options)
html = re.sub(
    r'<select id="cricket-match-picker"[^>]*>.*?</select>',
    f'<select id="cricket-match-picker" onchange="switchMatchScorecard(\'cricket\', this.value)" class="px-3.5 py-2 rounded-xl border border-[#DCE7F3] bg-[#F7FAFD] text-xs font-semibold text-[#1B2432] focus:outline-none focus:border-[#1B2432] cursor-pointer">{opts_html}</select>',
    html,
    flags=re.DOTALL
)
print("Updated #cricket-match-picker options")

# Save updated index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html successfully!")
