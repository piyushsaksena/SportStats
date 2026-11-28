import json

# Load existing cricket.json
with open('data/datasets/cricket.json', 'r', encoding='utf-8') as f:
    cricket_data = json.load(f)

# Load our sync payload
with open('cricket_dataset_starter/data/processed/sportstats_sync_payload.json', 'r', encoding='utf-8') as f:
    payload = json.load(f)

# Update cricsheet_matches (first 60 with complete scorecards)
cricket_data['cricsheet_matches'] = payload['recent_cricsheet_matches'][:60]

# Update matches_2026
cricket_data['matches_2026'] = payload['matches_2026'][:25]

# Update team_fixtures
cricket_data['team_fixtures'] = payload['team_histories']
cricket_data['last_updated'] = "2026-11-28"

with open('data/datasets/cricket.json', 'w', encoding='utf-8') as f:
    json.dump(cricket_data, f, indent=2, ensure_ascii=False)

print("Updated data/datasets/cricket.json successfully!")
print(f" - cricsheet_matches: {len(cricket_data['cricsheet_matches'])}")
print(f" - matches_2026: {len(cricket_data['matches_2026'])}")
print(f" - team_fixtures teams: {list(cricket_data['team_fixtures'].keys())}")
