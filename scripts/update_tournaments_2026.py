import json

# 1. Update data/datasets/cricket.json
with open('data/datasets/cricket.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

d['major_tournaments'] = [
    {
        "name": "ICC Men's T20 World Cup",
        "format": "Group Stage & Super 8/Knockout (T20I)",
        "frequency": "Biennial / Every 2 Years",
        "first_edition": 2007,
        "current_holder": "India (2026 Champions)",
        "description": "The premier global 20-over world championship, won by India in 2026 to claim their third Men's T20 World Cup crown."
    },
    {
        "name": "ICC World Test Championship",
        "format": "Two-Year League Cycle & One-Off Final",
        "frequency": "Every 2 Years",
        "first_edition": 2019,
        "current_holder": "South Africa (2025 Champions)",
        "description": "The pinnacle championship for traditional multi-day Test cricket, won by South Africa in the 2025 Lord's final."
    },
    {
        "name": "ICC Champions Trophy",
        "format": "8-Team Elite ODI Tournament",
        "frequency": "Every 4 Years",
        "first_edition": 1998,
        "current_holder": "India (2025 Champions)",
        "description": "The prestigious 8-team elite 50-over championship, won by India in the 2025 tournament."
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
        "current_holder": "India",
        "description": "The continental championship of Asia featuring the region's elite Full and Associate members."
    }
]

with open('data/datasets/cricket.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("Updated data/datasets/cricket.json successfully!")

# 2. Update index.html
with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

tourn_start = -1
tourn_end = -1
for i, l in enumerate(lines):
    if '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">' in l and i < 2000:
        tourn_start = i
        for j in range(i+1, i+100):
            if '</div>' in lines[j] and '<!-- Cricket Tab 2' in lines[j+3]:
                tourn_end = j
                break
        break

print(f"Tournaments grid located: lines {tourn_start+1} to {tourn_end+1}")

new_tournaments_html = """      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
        <div class="p-4 rounded-xl bg-[#F3F8FE] border border-[#DCE7F3] hover:border-[#1B2432] space-y-2 transition-all">
          <div class="flex justify-between items-start">
            <h4 class="font-bold text-xs sm:text-sm text-[#1B2432]">ICC Men's T20 World Cup</h4>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-white border border-[#DCE7F3] text-[#1B2432] font-bold">2026 Edition</span>
          </div>
          <p class="text-[11px] text-[#5A6B82] leading-snug">The premier global 20-over world championship, won by India in 2026 to claim their historic world title.</p>
          <div class="flex items-center justify-between text-[10px] font-mono pt-1 text-[#1B2432] border-t border-[#DCE7F3]/60">
            <span>Inaugural: 2007</span>
            <span class="font-bold text-emerald-700">Holder: India 🇮🇳 (2026 Champions)</span>
          </div>
        </div>

        <div class="p-4 rounded-xl bg-[#F3F8FE] border border-[#DCE7F3] hover:border-[#1B2432] space-y-2 transition-all">
          <div class="flex justify-between items-start">
            <h4 class="font-bold text-xs sm:text-sm text-[#1B2432]">ICC World Test Championship</h4>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-white border border-[#DCE7F3] text-[#1B2432] font-bold">2023–25 Cycle</span>
          </div>
          <p class="text-[11px] text-[#5A6B82] leading-snug">The pinnacle championship for traditional multi-day Test cricket, won by South Africa in the 2025 Lord's final.</p>
          <div class="flex items-center justify-between text-[10px] font-mono pt-1 text-[#1B2432] border-t border-[#DCE7F3]/60">
            <span>Inaugural: 2019</span>
            <span class="font-bold text-emerald-700">Holder: South Africa 🇿🇦 (2025 Champions)</span>
          </div>
        </div>

        <div class="p-4 rounded-xl bg-[#F3F8FE] border border-[#DCE7F3] hover:border-[#1B2432] space-y-2 transition-all">
          <div class="flex justify-between items-start">
            <h4 class="font-bold text-xs sm:text-sm text-[#1B2432]">ICC Champions Trophy</h4>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-white border border-[#DCE7F3] text-[#1B2432] font-bold">2025 Edition</span>
          </div>
          <p class="text-[11px] text-[#5A6B82] leading-snug">The prestigious 8-team elite 50-over championship, won by India in 2025 in an undefeated tournament campaign.</p>
          <div class="flex items-center justify-between text-[10px] font-mono pt-1 text-[#1B2432] border-t border-[#DCE7F3]/60">
            <span>Inaugural: 1998</span>
            <span class="font-bold text-emerald-700">Holder: India 🇮🇳 (2025 Champions)</span>
          </div>
        </div>

        <div class="p-4 rounded-xl bg-[#F3F8FE] border border-[#DCE7F3] hover:border-[#1B2432] space-y-2 transition-all">
          <div class="flex justify-between items-start">
            <h4 class="font-bold text-xs sm:text-sm text-[#1B2432]">ICC Men's Cricket World Cup</h4>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-white border border-[#DCE7F3] text-[#1B2432] font-bold">Every 4 Years</span>
          </div>
          <p class="text-[11px] text-[#5A6B82] leading-snug">The premier quadrennial 50-over championship, representing the ultimate prize in One Day International cricket.</p>
          <div class="flex items-center justify-between text-[10px] font-mono pt-1 text-[#1B2432] border-t border-[#DCE7F3]/60">
            <span>Inaugural: 1975</span>
            <span class="font-bold text-emerald-700">Holder: Australia 🇦🇺 (2023)</span>
          </div>
        </div>

        <div class="p-4 rounded-xl bg-[#F3F8FE] border border-[#DCE7F3] hover:border-[#1B2432] space-y-2 transition-all">
          <div class="flex justify-between items-start">
            <h4 class="font-bold text-xs sm:text-sm text-[#1B2432]">ICC Women's T20 World Cup</h4>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-white border border-[#DCE7F3] text-[#1B2432] font-bold">Biennial</span>
          </div>
          <p class="text-[11px] text-[#5A6B82] leading-snug">The premier global 20-over world tournament featuring the top ten international women's sides.</p>
          <div class="flex items-center justify-between text-[10px] font-mono pt-1 text-[#1B2432] border-t border-[#DCE7F3]/60">
            <span>Inaugural: 2009</span>
            <span class="font-bold text-emerald-700">Holder: New Zealand 🇳🇿 (2024 Champions)</span>
          </div>
        </div>

        <div class="p-4 rounded-xl bg-[#F3F8FE] border border-[#DCE7F3] hover:border-[#1B2432] space-y-2 transition-all">
          <div class="flex justify-between items-start">
            <h4 class="font-bold text-xs sm:text-sm text-[#1B2432]">Asia Cup (Men's)</h4>
            <span class="text-[9px] font-mono px-2 py-0.5 rounded bg-white border border-[#DCE7F3] text-[#1B2432] font-bold">Every 2 Years</span>
          </div>
          <p class="text-[11px] text-[#5A6B82] leading-snug">The continental championship of Asia contested between the region's top Full and Associate members.</p>
          <div class="flex items-center justify-between text-[10px] font-mono pt-1 text-[#1B2432] border-t border-[#DCE7F3]/60">
            <span>Inaugural: 1984</span>
            <span class="font-bold text-emerald-700">Holder: India 🇮🇳 (Defending Champions)</span>
          </div>
        </div>
      </div>
"""

lines[tourn_start:tourn_end+1] = [new_tournaments_html]

with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Updated index.html major tournaments successfully!")
