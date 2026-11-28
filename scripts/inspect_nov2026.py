import glob, json
files = glob.glob('cricket_dataset_starter/data/processed/raw_match_json/*.json')

nov_2026 = []
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            d = json.load(fp)
        info = d.get('info', {})
        dates = info.get('dates', [])
        if dates and any(d_str.startswith('2026-11') for d_str in dates):
            nov_2026.append({
                'file': f,
                'dates': dates,
                'teams': info.get('teams'),
                'event': (info.get('event') or {}).get('name'),
                'type': info.get('match_type')
            })
    except Exception:
        pass

nov_2026.sort(key=lambda x: x['dates'][0], reverse=True)
print(f"Total Nov 2026 matches in dataset: {len(nov_2026)}")
for m in nov_2026[:20]:
    print(f"{m['dates']} | {m['type']} | {m['teams']} | {m['event']}")
