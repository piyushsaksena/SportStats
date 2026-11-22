import json
import glob
import os
import math

TEAM_FLAGS = {
    "India": "🇮🇳",
    "New Zealand": "🇳🇿",
    "Australia": "🇦🇺",
    "South Africa": "🇿🇦",
    "Pakistan": "🇵🇰",
    "Sri Lanka": "🇱🇰",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "West Indies": "🌴",
    "Bangladesh": "🇧🇩",
    "Zimbabwe": "🇿🇼",
    "Namibia": "🇳🇦",
    "Ireland": "🇮🇪",
    "Netherlands": "🇳🇱",
    "Oman": "🇴🇲",
    "United Arab Emirates": "🇦🇪",
    "Kuwait": "🇰🇼",
    "Qatar": "🇶🇦",
    "Jersey": "🇯🇪",
    "Denmark": "🇩🇰",
    "Kenya": "🇰🇪",
    "Papua New Guinea": "🇵🇬",
    "Argentina": "🇦🇷",
    "Mexico": "🇲🇽",
    "Sydney Sixers": "🟣",
    "Sydney Thunder": "🟢",
    "Brisbane Heat": "🔵",
    "Melbourne Stars": "🟢",
    "Melbourne Renegades": "🔴",
    "Perth Scorchers": "🟠",
    "Adelaide Strikers": "🔵",
    "Hobart Hurricanes": "🟣",
    "Western Australia": "🟡",
    "South Australia": "🔴",
    "Tasmania": "🟢",
    "New South Wales": "🔵",
    "Victoria": "🔵",
    "Queensland": "🟤",
    "Biratnagar Kings": "👑",
    "Janakpur Bolts": "⚡",
    "Karnali Yaks": "🦬",
    "Sudur Paschim Royals": "🦅",
    "Chitwan Rhinos": "🦏",
    "Lumbini Lions": "🦁",
    "Pokhara Avengers": "🛡️",
    "Kathmandu Gorkhas": "🗡️"
}

def get_flag(team_name):
    for k, flag in TEAM_FLAGS.items():
        if k.lower() in team_name.lower() or team_name.lower() in k.lower():
            return flag
    return "🏏"

def parse_cricsheet_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    info = data.get('info', {})
    event = info.get('event', {})
    event_name = event.get('name') if isinstance(event, dict) else (str(event) if event else "International Series")
    match_num = event.get('match_number') if isinstance(event, dict) else None
    
    dates = info.get('dates', [])
    date_str = dates[0] if dates else "2026"
    match_type = info.get('match_type', 'T20')
    teams = info.get('teams', ['Team A', 'Team B'])
    venue = info.get('venue', 'Cricket Ground')
    city = info.get('city', '')
    venue_full = f"{venue}, {city}".strip(', ') if city else venue
    
    outcome = info.get('outcome', {})
    winner = outcome.get('winner')
    by_dict = outcome.get('by', {})
    
    margin_str = ""
    if 'runs' in by_dict:
        margin_str = f"by {by_dict['runs']} runs"
    elif 'wickets' in by_dict:
        margin_str = f"by {by_dict['wickets']} wickets"
    elif 'innings' in by_dict:
        margin_str = f"by an innings and {by_dict.get('runs', 0)} runs"
    
    result_text = f"{winner} won {margin_str}".strip() if winner else outcome.get('result', 'Draw / No Result')
    potm_list = info.get('player_of_match', [])
    potm = potm_list[0] if potm_list else "Not awarded"
    
    innings_data = []
    innings_scores = {}
    
    for idx, inn in enumerate(data.get('innings', [])):
        inn_team = inn.get('team', f"Team {idx+1}")
        total_runs = 0
        wickets = 0
        legit_balls = 0
        
        batter_stats = {}
        bowler_stats = {}
        
        overs_list = inn.get('overs', [])
        for ov_obj in overs_list:
            ov_num = ov_obj.get('over', 0)
            for d in ov_obj.get('deliveries', []):
                batter = d.get('batter')
                bowler = d.get('bowler')
                runs = d.get('runs', {})
                b_runs = runs.get('batter', 0)
                extras = runs.get('extras', 0)
                d_total = runs.get('total', 0)
                
                total_runs += d_total
                
                # Check for extras that don't count as legal balls (wide, noball)
                d_extras = d.get('extras', {})
                is_wide = 'wides' in d_extras
                is_noball = 'noballs' in d_extras
                if not is_wide and not is_noball:
                    legit_balls += 1
                
                if batter not in batter_stats:
                    batter_stats[batter] = {'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'out': False, 'dismissal': 'not out'}
                batter_stats[batter]['runs'] += b_runs
                if not is_wide:
                    batter_stats[batter]['balls'] += 1
                if b_runs == 4:
                    batter_stats[batter]['fours'] += 1
                elif b_runs == 6:
                    batter_stats[batter]['sixes'] += 1
                
                if bowler not in bowler_stats:
                    bowler_stats[bowler] = {'runs': 0, 'balls': 0, 'wickets': 0}
                # Bowler conceded runs include batter runs and wides/noballs, but not leg-byes or byes
                conceded = b_runs + d_extras.get('wides', 0) + d_extras.get('noballs', 0)
                bowler_stats[bowler]['runs'] += conceded
                if not is_wide and not is_noball:
                    bowler_stats[bowler]['balls'] += 1
                
                if 'wickets' in d:
                    for w in d['wickets']:
                        wickets += 1
                        w_player = w.get('player_out')
                        w_kind = w.get('kind', 'out')
                        if w_player in batter_stats:
                            batter_stats[w_player]['out'] = True
                            batter_stats[w_player]['dismissal'] = w_kind
                        if w_kind != 'run out':
                            bowler_stats[bowler]['wickets'] += 1
        
        # Calculate overs string
        full_overs = legit_balls // 6
        rem_balls = legit_balls % 6
        overs_str = f"{full_overs}.{rem_balls}" if rem_balls > 0 else f"{full_overs}"
        
        # Top 3 batters
        sorted_batters = sorted(batter_stats.items(), key=lambda x: -x[1]['runs'])[:3]
        top_bat_list = []
        for b_name, b_info in sorted_batters:
            sr = round((b_info['runs'] / b_info['balls'] * 100), 1) if b_info['balls'] > 0 else 0
            star = "" if b_info['out'] else "*"
            top_bat_list.append(f"{b_name} {b_info['runs']}{star} ({b_info['balls']}b, {b_info['fours']}x4, {b_info['sixes']}x6, SR {sr})")
        
        # Top 3 bowlers
        sorted_bowlers = sorted(bowler_stats.items(), key=lambda x: (-x[1]['wickets'], x[1]['runs']))[:3]
        top_bowl_list = []
        for bo_name, bo_info in sorted_bowlers:
            bo_overs = f"{bo_info['balls'] // 6}.{bo_info['balls'] % 6}" if bo_info['balls'] % 6 else f"{bo_info['balls'] // 6}"
            econ = round(bo_info['runs'] / (bo_info['balls'] / 6), 2) if bo_info['balls'] > 0 else 0
            top_bowl_list.append(f"{bo_name} {bo_info['wickets']}/{bo_info['runs']} ({bo_overs} ov, Econ {econ})")
        
        inn_score_str = f"{total_runs}/{wickets} ({overs_str} ov)"
        if inn_team not in innings_scores:
            innings_scores[inn_team] = []
        innings_scores[inn_team].append(inn_score_str)
        
        innings_data.append({
            'team': inn_team,
            'runs': total_runs,
            'wickets': wickets,
            'overs': overs_str,
            'score_str': inn_score_str,
            'top_batters': top_bat_list,
            'top_bowlers': top_bowl_list
        })
    
    # Combined score string per team
    team_scores_summary = {}
    for t in teams:
        scores = innings_scores.get(t, [])
        team_scores_summary[t] = " & ".join(scores) if scores else "Did not bat"
        
    return {
        'id': f"cricsheet-{os.path.splitext(os.path.basename(filepath))[0]}",
        'file': os.path.basename(filepath),
        'title': f"{event_name}" + (f" (Match {match_num})" if match_num else ""),
        'event': event_name,
        'date': date_str,
        'dates': dates,
        'venue': venue_full,
        'match_type': match_type,
        'teams': teams,
        'team1': {
            'name': teams[0],
            'flag': get_flag(teams[0]),
            'score': team_scores_summary.get(teams[0], '')
        },
        'team2': {
            'name': teams[1],
            'flag': get_flag(teams[1]),
            'score': team_scores_summary.get(teams[1], '')
        },
        'winner': winner,
        'result_note': result_text,
        'player_of_match': potm,
        'innings': innings_data
    }

if __name__ == '__main__':
    files = sorted(glob.glob('data/uploaded_cricket_zip/*.json'))
    print(f"Parsing {len(files)} Cricsheet files...")
    all_parsed = [parse_cricsheet_file(f) for f in files]
    print(f"Successfully parsed {len(all_parsed)} matches.")
    
    # Preview marquee matches
    for m in all_parsed[:5]:
        print(f"\n--- {m['title']} | {m['date']} ---")
        print(f"  {m['team1']['flag']} {m['team1']['name']}: {m['team1']['score']}")
        print(f"  {m['team2']['flag']} {m['team2']['name']}: {m['team2']['score']}")
        print(f"  Result: {m['result_note']}")
        print(f"  POTM: {m['player_of_match']}")
