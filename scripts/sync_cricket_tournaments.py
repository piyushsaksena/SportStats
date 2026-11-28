import json

with open('data/datasets/cricket.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

d['major_tournaments'] = [
    {
        "name": "ICC Men's T20 World Cup",
        "format": "Group Stage & Super 8/Knockout (T20I)",
        "frequency": "Biennial / Every 2 Years",
        "first_edition": 2007,
        "current_holder": "India (2024)",
        "description": "The marquee global tournament for the shortest international format, showcasing explosive power-hitting and global competitiveness."
    },
    {
        "name": "ICC Men's Cricket World Cup",
        "format": "Round-Robin and Knockout (ODI)",
        "frequency": "Every 4 Years",
        "first_edition": 1975,
        "current_holder": "Australia (2023)",
        "description": "The premier quadrennial championship of One Day International cricket, representing the ultimate prize in the 50-over format."
    },
    {
        "name": "ICC World Test Championship",
        "format": "Two-Year League Cycle & One-Off Final",
        "frequency": "Every 2 Years",
        "first_edition": 2019,
        "current_holder": "Australia (2023)",
        "description": "The premier championship for multi-day Test cricket, crowning the undisputed world Test champion at Lord's."
    },
    {
        "name": "ICC Women's T20 World Cup",
        "format": "Group Stage & Knockout (T20I)",
        "frequency": "Biennial / Every 2 Years",
        "first_edition": 2009,
        "current_holder": "New Zealand (2024)",
        "description": "The premier global twenty-over world tournament for women's international cricket."
    },
    {
        "name": "Asia Cup (Men's)",
        "format": "ODI / T20I Format",
        "frequency": "Every 2 Years",
        "first_edition": 1984,
        "current_holder": "India (2023)",
        "description": "The continental championship of Asia featuring the region's elite Full and Associate members."
    },
    {
        "name": "ICC Champions Trophy",
        "format": "8-Team Elite ODI Tournament",
        "frequency": "Every 4 Years",
        "first_edition": 1998,
        "current_holder": "Pakistan",
        "description": "The prestigious tournament featuring the top eight ranked ODI teams in the world."
    }
]

with open('data/datasets/cricket.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Updated data/datasets/cricket.json major_tournaments successfully!")
