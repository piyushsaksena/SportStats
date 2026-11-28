import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update the live strip cricket card (lines ~1240-1270)
old_live_card = r'<!-- 1\. Cricket 2026 Live -->.*?</div>\s*</div>\s*</div>'
new_live_card = '''<!-- 1. Cricket Recent Result -->
          <div onclick="navigateTo('cricket-matches')" class="group bg-white p-5 rounded-2xl border-2 border-[#1B2432] hover:bg-[#EAF4FF]/40 shadow-xs hover:shadow-md transition-all space-y-3 cursor-pointer">
            <div class="flex justify-between items-center text-xs">
              <span class="font-bold text-[#1B2432] flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                🏏 Cricket • 1st Test
              </span>
              <span class="font-mono text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-bold border border-emerald-200">RECENT RESULT</span>
            </div>
            <div class="space-y-1.5 py-1">
              <div class="flex justify-between items-center text-sm font-semibold">
                <span class="flex items-center gap-2"><span>🇮🇳</span> India</span>
                <span class="font-mono text-xs font-bold text-[#1B2432]">720/9 <span class="text-[10px] text-[#5A6B82]">(166 ov)</span></span>
              </div>
              <div class="flex justify-between items-center text-sm font-black text-[#1B2432]">
                <span class="flex items-center gap-2"><span>🇳🇿</span> New Zealand</span>
                <span class="font-mono text-xs font-bold text-[#1B2432]">368 &amp; 239/5</span>
              </div>
            </div>
            <div class="text-[11px] font-mono text-[#5A6B82] border-t border-[#DCE7F3] pt-2 flex justify-between">
              <span>Basin Reserve, Wellington</span>
              <span class="text-emerald-700 font-bold">Match Drawn (19–23 Nov)</span>
            </div>
          </div>'''

html = re.sub(r'<!-- 1\. Cricket 2026 Live -->.*?</div>\s*</div>\s*</div>', new_live_card, html, flags=re.DOTALL)
print("Updated Live strip cricket card")

# 2. Update default scorecard in #cricket-scorecard-display
default_card_replacement = '''<div id="cricket-scorecard-display" class="bg-white p-6 rounded-2xl border border-[#DCE7F3] space-y-5 shadow-sm">
        <div class="flex justify-between items-center pb-3 border-b border-[#DCE7F3]">
          <div>
            <span class="text-xs font-mono font-bold text-slate-700 bg-slate-100 px-2.5 py-1 rounded-full border border-slate-300 inline-flex items-center gap-1.5">
              COMPLETED
            </span>
            <h4 class="text-sm sm:text-base font-extrabold text-[#1B2432] mt-1.5">India tour of New Zealand 2026 • 1st Test</h4>
            <p class="text-xs text-[#5A6B82]">Basin Reserve, Wellington • 19–23 Nov 2026</p>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 py-2">
          <div class="p-4 rounded-xl bg-[#EAF4FF] border border-[#DCE7F3] flex justify-between items-center">
            <div class="flex items-center gap-2.5">
              <span class="text-2xl">🇳🇿</span>
              <div>
                <strong class="text-sm font-black text-[#1B2432]">New Zealand</strong>
                <span class="text-[10px] text-[#5A6B82] block">121.0 &amp; 120.0 ov</span>
              </div>
            </div>
            <span class="font-mono text-xl font-black text-[#1B2432]">368 &amp; 239/5</span>
          </div>

          <div class="p-4 rounded-xl bg-[#F3F8FE] border border-[#DCE7F3] flex justify-between items-center">
            <div class="flex items-center gap-2.5">
              <span class="text-2xl">🇮🇳</span>
              <div>
                <strong class="text-sm font-black text-[#1B2432]">India</strong>
                <span class="text-[10px] text-[#5A6B82] block">166.0 ov</span>
              </div>
            </div>
            <span class="font-mono text-xl font-black text-[#1B2432]">720/9 d</span>
          </div>
        </div>

        <div class="p-3.5 rounded-xl bg-[#F7FAFD] border border-[#DCE7F3] text-xs font-mono text-[#1B2432]">
          <span class="font-bold">Match Situation:</span> Match Drawn. High-scoring marathon Test at Basin Reserve.
          <div class="text-[11px] text-[#5A6B82] mt-1 font-sans"><strong>Key Performers:</strong> Player of the Match: Henry Nicholls • Mammoth innings by India posting 720/9 declared.</div>
        </div>
      </div>'''

html = re.sub(r'<div id="cricket-scorecard-display".*?</div>\s*</div>\s*</div>\s*</div>', default_card_replacement, html, count=1, flags=re.DOTALL)
print("Updated default scorecard display")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved index.html successfully!")
