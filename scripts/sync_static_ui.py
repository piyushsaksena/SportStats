with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

header = '"""Embedded Static UI for SportStats Web Dashboard."""\n\nHTML_DASHBOARD = r\'\'\''
footer = '\'\'\'\n'

with open('backend/src/sportstats/api/static_ui.py', 'w', encoding='utf-8') as f:
    f.write(header + html_content + footer)

print("Synchronized backend/src/sportstats/api/static_ui.py with HTML_DASHBOARD successfully!")
