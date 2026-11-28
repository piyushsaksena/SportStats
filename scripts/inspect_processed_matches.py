import glob, json
from collections import Counter

files = glob.glob('cricket_dataset_starter/data/processed/raw_match_json/*.json')
years = Counter()
formats = Counter()
india_matches = []

for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            d = json.load(fp)
        info = d.get('info', {})
        dates = info.get('dates', [])
        if dates:
            yr = str(dates[0])[:4]
            years[yr] += 1
        m_type = info.get('match_type')
        formats[m_type] += 1
        teams = info.get('teams', [])
        if 'India' in teams:
            india_matches.append({
                'date': dates[0] if dates else '',
                'event': (info.get('event') or {}).get('name'),
                'type': m_type,
                'teams': teams,
                'outcome': info.get('outcome')
            })
    except Exception as e:
        pass

print("Total parsed matches:", len(files))
print("By Year:", dict(years))
print("By Format:", dict(formats))
print(f"Total India matches: {len(india_matches)}")
india_matches.sort(key=lambda x: x['date'], reverse=True)
print("\nLatest 10 India matches in Cricsheet dataset:")
for m in india_matches[:10]:
    print(f" - {m['date']} | {m['type']} | {m['teams']} | {m['event']} | Winner: {m['outcome'].get('winner') if m['outcome'] else None}")
