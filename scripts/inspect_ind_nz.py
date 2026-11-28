import glob, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_cricsheet import parse_cricsheet_file

files = glob.glob('cricket_dataset_starter/data/processed/raw_match_json/*.json')

ind_nz_matches = []
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            d = json.load(fp)
        info = d.get('info', {})
        teams = info.get('teams', [])
        if 'India' in teams and 'New Zealand' in teams:
            parsed = parse_cricsheet_file(f)
            ind_nz_matches.append(parsed)
    except Exception as e:
        pass

ind_nz_matches.sort(key=lambda x: x['date'], reverse=True)
print(f"Total IND vs NZ matches in dataset: {len(ind_nz_matches)}")
print("\nRecent 10 IND vs NZ matches:")
for m in ind_nz_matches[:10]:
    print(f"ID: {m['id']} | Date: {m['date']} | Format: {m['match_type']} | Title: {m['title']}")
    print(f"  Team1: {m['team1']['name']} ({m['team1']['score']})")
    print(f"  Team2: {m['team2']['name']} ({m['team2']['score']})")
    print(f"  Result: {m['result_note']} | POTM: {m['player_of_match']}")
