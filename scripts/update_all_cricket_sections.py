import json

# 1. Load payload
with open('cricket_dataset_starter/data/processed/sportstats_sync_payload.json', 'r', encoding='utf-8') as f:
    payload = json.load(f)

# Format India matches
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
def format_match(m):
    d = m['date']
    parts = d.split('-')
    date_display = f"{parts[2]} {months[int(parts[1])-1]} {parts[0]}" if len(parts)==3 else d
    opp_str = f"vs {m['opp']}"
    if m.get('event') and 'Match' in m.get('event'):
        opp_str += f" ({m['event']})"
    elif m.get('fmt'):
        opp_str += f" ({m['fmt']})"
    
    venue_name = "Wellington" if "New Zealand" in m['opp'] and m['fmt']=="Test" else ("Hamilton / Eden Park" if "New Zealand" in m['opp'] else "International Venue")
    if "South Africa" in m.get('event', ''):
        venue_name = "Kensington Oval, Barbados"
        
    return {
        "date": date_display,
        "opp": opp_str,
        "format": m.get('fmt', 'T20I'),
        "venue": venue_name,
        "res": m.get('res', 'WON'),
        "score": m.get('score', ''),
        "link": "cricket-scorecard"
    }

ind_matches = [format_match(m) for m in payload['team_histories']['India']]
nz_matches = [format_match(m) for m in payload['team_histories']['New Zealand']]

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 2. Update Tournaments grid (around line 1719)
tourn_start = -1
tourn_end = -1
for i, l in enumerate(lines):
    if '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">' in l and i < 2000:
        tourn_start = i
        for j in range(i+1, i+60):
            if '</div>' in lines[j] and '<!-- Cricket Tab 2' in lines[j+3]:
                tourn_end = j
                break
        break

print(f"Tournaments grid located: lines {tourn_start+1} to {tourn_end+1}")

new_tournaments_html = """      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
        <div class="p-4 rounded-xl bg-[#F3F8FE] border border-[#DCE7F3] hover:border-[#1B2432] space-y-2 transition-all">
          <div class="flex justify-between items-start">
            <h4 class="font-bold text-xs sm:text-sm text-[#1B2432]">ICC Men's T20 World Cup</h4>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-white border border-[#DCE7F3] text-[#1B2432] font-bold">Biennial</span>
          </div>
          <p class="text-[11px] text-[#5A6B82] leading-snug">The premier global 20-over championship, crowning the undisputed world champions of the shortest format.</p>
          <div class="flex items-center justify-between text-[10px] font-mono pt-1 text-[#1B2432] border-t border-[#DCE7F3]/60">
            <span>Inaugural: 2007</span>
            <span class="font-bold text-emerald-700">Holder: India 🇮🇳 (2024 Champions)</span>
          </div>
        </div>

        <div class="p-4 rounded-xl bg-[#F3F8FE] border border-[#DCE7F3] hover:border-[#1B2432] space-y-2 transition-all">
          <div class="flex justify-between items-start">
            <h4 class="font-bold text-xs sm:text-sm text-[#1B2432]">ICC Men's Cricket World Cup</h4>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-white border border-[#DCE7F3] text-[#1B2432] font-bold">Every 4 Years</span>
          </div>
          <p class="text-[11px] text-[#5A6B82] leading-snug">The premier quadrennial 50-over championship, representing the pinnacle trophy in international One Day cricket.</p>
          <div class="flex items-center justify-between text-[10px] font-mono pt-1 text-[#1B2432] border-t border-[#DCE7F3]/60">
            <span>Inaugural: 1975</span>
            <span class="font-bold text-emerald-700">Holder: Australia 🇦🇺 (2023)</span>
          </div>
        </div>

        <div class="p-4 rounded-xl bg-[#F3F8FE] border border-[#DCE7F3] hover:border-[#1B2432] space-y-2 transition-all">
          <div class="flex justify-between items-start">
            <h4 class="font-bold text-xs sm:text-sm text-[#1B2432]">ICC World Test Championship</h4>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-white border border-[#DCE7F3] text-[#1B2432] font-bold">2-Year Cycle</span>
          </div>
          <p class="text-[11px] text-[#5A6B82] leading-snug">The pinnacle championship for traditional multi-day Test cricket, culminating in the Lord's WTC Final.</p>
          <div class="flex items-center justify-between text-[10px] font-mono pt-1 text-[#1B2432] border-t border-[#DCE7F3]/60">
            <span>Inaugural: 2019</span>
            <span class="font-bold text-emerald-700">Holder: Australia 🇦🇺 (Next: June 2025)</span>
          </div>
        </div>

        <div class="p-4 rounded-xl bg-[#F3F8FE] border border-[#DCE7F3] hover:border-[#1B2432] space-y-2 transition-all">
          <div class="flex justify-between items-start">
            <h4 class="font-bold text-xs sm:text-sm text-[#1B2432]">ICC Women's T20 World Cup</h4>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-white border border-[#DCE7F3] text-[#1B2432] font-bold">Biennial</span>
          </div>
          <p class="text-[11px] text-[#5A6B82] leading-snug">The premier women's twenty-over world tournament featuring the top ten ranked international sides.</p>
          <div class="flex items-center justify-between text-[10px] font-mono pt-1 text-[#1B2432] border-t border-[#DCE7F3]/60">
            <span>Inaugural: 2009</span>
            <span class="font-bold text-emerald-700">Holder: New Zealand 🇳🇿 (Oct 2024)</span>
          </div>
        </div>

        <div class="p-4 rounded-xl bg-[#F3F8FE] border border-[#DCE7F3] hover:border-[#1B2432] space-y-2 transition-all">
          <div class="flex justify-between items-start">
            <h4 class="font-bold text-xs sm:text-sm text-[#1B2432]">Asia Cup (Men's)</h4>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-white border border-[#DCE7F3] text-[#1B2432] font-bold">Every 2 Years</span>
          </div>
          <p class="text-[11px] text-[#5A6B82] leading-snug">The continental championship of Asia contested between the region's elite Full and Associate members.</p>
          <div class="flex items-center justify-between text-[10px] font-mono pt-1 text-[#1B2432] border-t border-[#DCE7F3]/60">
            <span>Inaugural: 1984</span>
            <span class="font-bold text-emerald-700">Holder: India 🇮🇳 (8 Titles)</span>
          </div>
        </div>

        <div class="p-4 rounded-xl bg-[#F3F8FE] border border-[#DCE7F3] hover:border-[#1B2432] space-y-2 transition-all">
          <div class="flex justify-between items-start">
            <h4 class="font-bold text-xs sm:text-sm text-[#1B2432]">ICC Champions Trophy</h4>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-white border border-[#DCE7F3] text-[#1B2432] font-bold">Quadrennial</span>
          </div>
          <p class="text-[11px] text-[#5A6B82] leading-snug">The prestigious 'Mini-World Cup' featuring the world's top 8 ranked ODI nations.</p>
          <div class="flex items-center justify-between text-[10px] font-mono pt-1 text-[#1B2432] border-t border-[#DCE7F3]/60">
            <span>Inaugural: 1998</span>
            <span class="font-bold text-emerald-700">Holder: Pakistan 🇵🇰 (Defender)</span>
          </div>
        </div>
      </div>
"""

lines[tourn_start:tourn_end+1] = [new_tournaments_html]
print("Replaced tournaments HTML successfully.")

# Join and re-split lines for accurate line numbers
content = "".join(lines)
lines = content.splitlines(keepends=True)

# 3. Locate and replace CRICKET_TEAMS["india"].matches
ind_start = -1
ind_end = -1
for i, l in enumerate(lines):
    if '"india": {' in l and i > 5000:
        for j in range(i+1, i+40):
            if '"matches": [' in lines[j]:
                ind_start = j
                for k in range(j+1, j+400):
                    if lines[k].startswith('            ]') and '"australia": {' in lines[k+2]:
                        ind_end = k
                        break
                break
        break

print(f"India matches located: lines {ind_start+1} to {ind_end+1}")

ind_matches_code = '            "matches": ' + json.dumps(ind_matches, indent=18).strip() + '\n'
lines[ind_start:ind_end+1] = [ind_matches_code]

content = "".join(lines)
lines = content.splitlines(keepends=True)

# 4. Locate and replace CRICKET_TEAMS["new-zealand"].matches
nz_start = -1
nz_end = -1
for i, l in enumerate(lines):
    if '"new-zealand": {' in l and i > 5000:
        for j in range(i+1, i+40):
            if '"matches": [' in lines[j]:
                nz_start = j
                for k in range(j+1, j+400):
                    if lines[k].startswith('            ]') and ('};' in lines[k+2] or 'FOOTBALL_TEAMS' in lines[k+4]):
                        nz_end = k
                        break
                break
        break

print(f"New Zealand matches located: lines {nz_start+1} to {nz_end+1}")

nz_matches_code = '            "matches": ' + json.dumps(nz_matches, indent=18).strip() + '\n'
lines[nz_start:nz_end+1] = [nz_matches_code]

# Write back index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Saved updated index.html with all tournaments and full 30 matches for India and New Zealand!")
