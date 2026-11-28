import json

with open('cricket_dataset_starter/data/processed/sportstats_sync_payload.json', 'r', encoding='utf-8') as f:
    payload = json.load(f)

india_raw = payload['team_histories']['India']
print(f"Total India matches in payload: {len(india_raw)}")
for i, m in enumerate(india_raw[:30]):
    print(f"{i+1:2d}. {m['date']} | {m['fmt']:4s} vs {m['opp']:15s} | {m['res']:4s} | {m['score']}")
