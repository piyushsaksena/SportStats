import os, subprocess

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
os.makedirs('reports/figures', exist_ok=True)

with open('index.html', 'r', encoding='utf-8') as f:
    base = f.read()

shots = [
    ('fig1_landing_view.png', '', 1440, 900),
    ('fig2_live_match_centre.png', "enterDashboard(); navigateTo('matches');", 1440, 950),
    ('fig3_cricket_team_fixtures.png', "enterDashboard(); selectSportSidebar('cricket'); switchDeptTab('cricket', 'c-teams'); renderCricketTeam('india');", 1440, 1100),
    ('fig4_icc_rankings_hub.png', "enterDashboard(); selectSportSidebar('cricket'); switchDeptTab('cricket', 'c-rankings'); switchIccRanking('men', 'odi');", 1440, 1050),
    ('fig5_comparison_studio.png', "enterDashboard(); navigateTo('compare'); if (typeof updateCompareStudio === 'function') updateCompareStudio();", 1440, 1000),
    ('fig6_my_teams_studio.png', "enterDashboard(); navigateTo('my-teams'); if (typeof toggleTeamFavourite === 'function') { toggleTeamFavourite('india', 'cricket', 'India'); toggleTeamFavourite('real-madrid', 'football', 'Real Madrid'); } if (typeof renderMyTeamsRoster === 'function') renderMyTeamsRoster();", 1440, 1000),
    ('fig7_top_50_athletes.png', "enterDashboard(); selectSportSidebar('cricket'); switchDeptTab('cricket', 'c-players');", 1440, 1000),
    ('fig8_ai_analyst.png', "enterDashboard(); navigateTo('ai');", 1440, 950)
]

for filename, nav_code, width, height in shots:
    out_png = os.path.abspath(os.path.join('reports/figures', filename))
    if nav_code:
        # Synchronous execution at end of body
        injection = f"<script>{nav_code}</script></body>"
        mod_html = base.replace('</body>', injection)
    else:
        mod_html = base

    temp_html = os.path.abspath(f'temp_{filename}.html')
    with open(temp_html, 'w', encoding='utf-8') as tf:
        tf.write(mod_html)

    cmd = [
        chrome_path,
        '--headless=new',
        '--disable-gpu',
        '--no-sandbox',
        f'--window-size={width},{height}',
        f'--screenshot={out_png}',
        f'file:///{temp_html}'
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if os.path.exists(temp_html):
        os.remove(temp_html)
    if os.path.exists(out_png):
        print(f"Captured {filename}: {os.path.getsize(out_png)} bytes")
    else:
        print(f"FAILED {filename}")

print("All screenshots updated!")
