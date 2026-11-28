import json, re

with open('cricket_dataset_starter/data/processed/sportstats_sync_payload.json', 'r', encoding='utf-8') as f:
    payload = json.load(f)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Helper to format match for CRICKET_TEAMS table
def fmt_team_matches(team_name, raw_matches):
    formatted = []
    for m in raw_matches:
        d = m['date']
        # e.g. "2026-11-19" -> "19 Nov 2026"
        parts = d.split('-')
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        date_display = f"{parts[2]} {months[int(parts[1])-1]} {parts[0]}" if len(parts)==3 else d
        
        opp_str = f"vs {m['opp']}"
        if m.get('event') and 'Match' in m.get('event'):
            opp_str += f" ({m['event']})"
        elif m.get('fmt'):
            opp_str += f" ({m['fmt']})"
            
        formatted.append({
            "date": date_display,
            "opp": opp_str,
            "format": m.get('fmt', 'T20I'),
            "venue": "International Venue",
            "res": m.get('res', 'WON'),
            "score": m.get('score', ''),
            "link": "cricket-scorecard"
        })
    return formatted

ind_matches = fmt_team_matches('India', payload['team_histories']['India'])
nz_matches = fmt_team_matches('New Zealand', payload['team_histories']['New Zealand'])

# Replace India matches array
ind_json = json.dumps(ind_matches, indent=18)
html = re.sub(
    r'("india":\s*\{.*?"matches":\s*)\[.*?\](\s*,\s*"venues")',
    f'\\1{ind_json}\\2',
    html,
    flags=re.DOTALL
)

# Replace New Zealand matches array
nz_json = json.dumps(nz_matches, indent=18)
html = re.sub(
    r'("new-zealand":\s*\{.*?"matches":\s*)\[.*?\](\s*,\s*"venues")',
    f'\\1{nz_json}\\2',
    html,
    flags=re.DOTALL
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated CRICKET_TEAMS matches for India and New Zealand successfully!")
