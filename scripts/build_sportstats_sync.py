import glob, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scripts.parse_cricsheet import parse_cricsheet_file, get_flag

PROCESSED_JSON_DIR = 'cricket_dataset_starter/data/processed/raw_match_json'
files = glob.glob(f'{PROCESSED_JSON_DIR}/*.json')
print(f"Found {len(files)} match files in processed folder.")

all_matches = []
for f in files:
    try:
        m = parse_cricsheet_file(f)
        all_matches.append(m)
    except Exception as e:
        pass

# Sort by date descending
all_matches.sort(key=lambda x: (x.get('date', ''), x.get('id', '')), reverse=True)
print(f"Parsed and sorted {len(all_matches)} matches.")

# Top recent marquee matches for 2026
matches_2026 = []
for m in all_matches:
    d = m.get('date', '')
    if d.startswith('2026'):
        status = 'COMPLETED'
        matches_2026.append({
            'id': m['id'],
            'title': f"{m['teams'][0]} vs {m['teams'][1]} • {m.get('title')}",
            'date': d,
            'status': status,
            'summary': m['result_note'],
            'team1': m['team1'],
            'team2': m['team2'],
            'venue': m['venue'],
            'player_of_match': m['player_of_match']
        })

print(f"Found {len(matches_2026)} matches in 2026.")

# Build Last 30 matches for key teams
key_teams = ['India', 'New Zealand', 'Australia', 'England', 'South Africa', 'Pakistan']
team_histories = {}

for team in key_teams:
    team_m = []
    for m in all_matches:
        if team in m['teams']:
            opp = [t for t in m['teams'] if t != team]
            opp_name = opp[0] if opp else 'Opposition'
            winner = m.get('winner')
            if winner == team:
                res = 'WON'
            elif winner is None or winner == 'None':
                res = 'DRAW'
            else:
                res = 'LOST'
            
            # Form scores
            team_score = m['team1']['score'] if m['team1']['name'] == team else m['team2']['score']
            opp_score = m['team2']['score'] if m['team1']['name'] == team else m['team1']['score']
            
            team_m.append({
                'opp': opp_name,
                'opp_flag': get_flag(opp_name),
                'res': res,
                'fmt': m['match_type'],
                'date': m['date'],
                'event': m.get('event', m.get('title', '')),
                'score': f"{team_score} vs {opp_score}".strip(),
                'note': m['result_note'],
                'id': m['id']
            })
    team_histories[team] = team_m[:30]
    print(f"Team {team}: {len(team_histories[team])} matches extracted.")

# Save to helper file for review
output_payload = {
    'recent_cricsheet_matches': all_matches[:100],  # 100 most recent with full innings
    'matches_2026': matches_2026[:30],
    'team_histories': team_histories
}

with open('cricket_dataset_starter/data/processed/sportstats_sync_payload.json', 'w', encoding='utf-8') as fp:
    json.dump(output_payload, fp, indent=2, ensure_ascii=False)

print("Saved sync payload successfully!")
