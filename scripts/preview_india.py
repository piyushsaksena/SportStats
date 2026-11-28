import json

with open('cricket_dataset_starter/data/processed/sportstats_sync_payload.json', 'r', encoding='utf-8') as fp:
    d = json.load(fp)

print("India's latest 10 matches:")
for m in d['team_histories']['India'][:10]:
    print(f" - {m['date']} | {m['fmt']} vs {m['opp']} | {m['res']} | {m['score']} | {m['event']}")
