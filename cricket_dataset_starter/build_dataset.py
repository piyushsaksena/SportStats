#!/usr/bin/env python3
"""
SportStats international cricket dataset builder.
Downloads Cricsheet's public JSON archive, filters men's/women's Test/ODI/T20I
matches from 2023-01-01 through 2026-11-28, and exports raw JSON plus CSVs.

IMPORTANT:
1) Fill config/top10_teams.json with the ICC top-10 lists you want to freeze.
2) Cricsheet coverage is not complete for every match; this script reports
   exactly what it found and does not fabricate missing scorecards.
3) Cricsheet JSON is ball-by-ball data. CSVs are derived from those deliveries.
"""
from __future__ import annotations
import csv, json, os, re, sys, urllib.request, zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RAW = DATA / "raw_json"
OUT = DATA / "processed"
CONFIG = ROOT / "config" / "top10_teams.json"
ARCHIVE = DATA / "all_json.zip"
URL = "https://cricsheet.org/downloads/all_json.zip"
START = date(2023, 1, 1)
END = date(2026, 11, 28)
GENDERS = {"male", "female"}
FORMATS = {"TEST": "Test", "ODI": "ODI", "T20I": "T20"}

def norm(s):
    return re.sub(r"\s+", " ", str(s or "")).strip().casefold()

def read_config():
    if not CONFIG.exists():
        raise SystemExit(f"Missing {CONFIG}. Copy top10_teams.example.json and fill it.")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    for gender in ("men", "women"):
        for fmt in ("TEST", "ODI", "T20I"):
            teams = cfg.get(gender, {}).get(fmt, [])
            if not isinstance(teams, list):
                raise SystemExit(f"config error: {gender}.{fmt} must be a list")
    return cfg

def download_archive():
    DATA.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE.exists():
        print("Downloading Cricsheet JSON archive (this may take 1-2 minutes)...")
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req) as resp, open(ARCHIVE, "wb") as out:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
                downloaded += len(chunk)
                if total:
                    print(f"\rDownloading: {downloaded/1024/1024:.1f} / {total/1024/1024:.1f} MB ({(downloaded/total)*100:.1f}%)", end="", flush=True)
            print()
    print(f"Archive ready: {ARCHIVE} ({ARCHIVE.stat().st_size/1024/1024:.1f} MB)")

def extract_archive():
    RAW.mkdir(parents=True, exist_ok=True)
    if any(RAW.glob("*.json")):
        print("Raw JSON already extracted; skipping extraction.")
        return
    with zipfile.ZipFile(ARCHIVE) as z:
        for name in z.namelist():
            if name.lower().endswith(".json") and not name.startswith("__MACOSX/"):
                target = RAW / Path(name).name
                with z.open(name) as src, target.open("wb") as dst:
                    dst.write(src.read())
    print(f"Extracted {len(list(RAW.glob('*.json')))} JSON files.")

def gender_key(g):
    return {"male": "men", "female": "women"}.get(norm(g))

def fmt_key(t):
    t = norm(t).upper()
    if t in ("TEST", "ODI", "T20"):
        return "T20I" if t == "T20" else t
    return None

def delivery_rows(match_id, info, innings):
    """Yield one row per delivery; preserve extras and dismissal details."""
    for inn_no, inn in enumerate(innings, 1):
        batting_team = inn.get("team")
        for over in inn.get("overs", []):
            over_no = over.get("over")
            for ball_no, delivery in enumerate(over.get("deliveries", []), 1):
                batter = delivery.get("batter")
                bowler = delivery.get("bowler")
                non_striker = delivery.get("non_striker")
                runs = delivery.get("runs", {})
                extras = delivery.get("extras", {})
                wickets = delivery.get("wickets", [])
                total_extras = sum(extras.values()) if extras else 0
                total = runs.get("total", 0)
                batter_runs = runs.get("batter", 0)
                bowler_runs = total - extras.get("byes", 0) - extras.get("legbyes", 0) - extras.get("penalty", 0)
                wicket_types = "|".join(w.get("kind", "") for w in wickets)
                wicket_players = "|".join(w.get("player_out", "") for w in wickets)
                yield {
                    "match_id": match_id, "date": (info.get("dates") or [""])[0],
                    "gender": info.get("gender"), "match_type": info.get("match_type"),
                    "event": (info.get("event") or {}).get("name"),
                    "venue": info.get("venue"), "city": info.get("city"),
                    "innings": inn_no, "batting_team": batting_team,
                    "over": over_no, "ball_in_over": ball_no,
                    "batter": batter, "non_striker": non_striker, "bowler": bowler,
                    "batter_runs": batter_runs, "total_runs": total,
                    "extras_total": total_extras,
                    "wides": extras.get("wides", 0), "noballs": extras.get("noballs", 0),
                    "byes": extras.get("byes", 0), "legbyes": extras.get("legbyes", 0),
                    "penalty": extras.get("penalty", 0),
                    "is_legal_ball": not ("wides" in extras or "noballs" in extras),
                    "dismissal_types": wicket_types, "players_out": wicket_players
                }

def aggregate_scorecards(match_id, info, innings):
    batting, bowling, innings_rows = [], [], []
    for inn_no, inn in enumerate(innings, 1):
        bat = defaultdict(lambda: {"runs":0,"balls":0,"fours":0,"sixes":0,"dismissal":""})
        bowl = defaultdict(lambda: {"legal_balls":0,"maidens":0,"runs_conceded":0,"wickets":0,"wides":0,"noballs":0})
        total_runs = legal_balls = wickets = 0
        over_runs = defaultdict(int)
        for over in inn.get("overs", []):
            over_no = over.get("over")
            for d in over.get("deliveries", []):
                b, bo = d.get("batter"), d.get("bowler")
                r, ex = d.get("runs", {}), d.get("extras", {})
                bat[b]["runs"] += r.get("batter", 0)
                total_runs += r.get("total", 0)
                over_runs[over_no] += r.get("total", 0)
                legal = not ("wides" in ex or "noballs" in ex)
                if legal:
                    bat[b]["balls"] += 1
                    bowl[bo]["legal_balls"] += 1
                    legal_balls += 1
                bat[b]["fours"] += int(r.get("batter",0) == 4)
                bat[b]["sixes"] += int(r.get("batter",0) == 6)
                bowl[bo]["runs_conceded"] += r.get("total",0) - ex.get("byes",0) - ex.get("legbyes",0) - ex.get("penalty",0)
                bowl[bo]["wides"] += ex.get("wides",0)
                bowl[bo]["noballs"] += ex.get("noballs",0)
                for w in d.get("wickets", []):
                    wickets += 1
                    bat[w.get("player_out","")]["dismissal"] = w.get("kind","")
                    if w.get("kind") not in ("run out","retired hurt","retired out","obstructing the field"):
                        bowl[bo]["wickets"] += 1
        for player, s in bat.items():
            batting.append({"match_id":match_id,"innings":inn_no,"team":inn.get("team"),"player":player,**s,
                            "strike_rate": round(100*s["runs"]/s["balls"],2) if s["balls"] else None})
        for player, s in bowl.items():
            # Maidens are counted only when the whole over has zero runs.
            s["maidens"] = sum(1 for ov in inn.get("overs",[]) if over_runs[ov.get("over")] == 0 and any(d.get("bowler")==player for d in ov.get("deliveries",[])))
            overs = s["legal_balls"] // 6 + (s["legal_balls"] % 6)/10
            bowling.append({"match_id":match_id,"innings":inn_no,"team":inn.get("team"),"player":player,**s,
                            "overs":overs,"economy":round(s["runs_conceded"]/(s["legal_balls"]/6),2) if s["legal_balls"] else None})
        innings_rows.append({"match_id":match_id,"innings":inn_no,"team":inn.get("team"),
                             "runs":total_runs,"wickets":wickets,"legal_balls":legal_balls,
                             "overs":f"{legal_balls//6}.{legal_balls%6}"})
    return batting, bowling, innings_rows

def main():
    cfg = read_config()
    download_archive()
    extract_archive()
    OUT.mkdir(parents=True, exist_ok=True)
    wanted = {(g, f): {norm(x) for x in cfg[g][f]} for g in ("men","women") for f in FORMATS}
    matches, deliveries, batting, bowling, innings_out = [], [], [], [], []
    seen = 0
    for p in RAW.glob("*.json"):
        try:
            m = json.loads(p.read_text(encoding="utf-8"))
            info = m.get("info", {})
            dates = info.get("dates") or []
            if not dates: continue
            d = date.fromisoformat(str(dates[0])[:10])
            if not START <= d <= END: continue
            g = gender_key(info.get("gender"))
            f = fmt_key(info.get("match_type"))
            if not g or not f: continue
            teams = info.get("teams", [])
            if not any(norm(t) in wanted[(g,f)] for t in teams): continue
            seen += 1
            mid = p.stem
            outcome = info.get("outcome") or {}
            toss = info.get("toss") or {}
            row = {
                "match_id":mid,"date":str(d),"gender":g,"format":f,
                "teams":teams,"team1":teams[0] if teams else None,"team2":teams[1] if len(teams)>1 else None,
                "venue":info.get("venue"),"city":info.get("city"),"country":info.get("country"),
                "event":(info.get("event") or {}).get("name"),"match_type_note":info.get("event",{}).get("match_number"),
                "toss_winner":toss.get("winner"),"toss_decision":toss.get("decision"),
                "winner":outcome.get("winner"),"by":outcome.get("by"),"result":outcome.get("result"),
                "player_of_match":info.get("player_of_match"),"overs":info.get("overs"),
                "source":"Cricsheet","source_file":p.name
            }
            matches.append(row)
            innings = m.get("innings", [])
            dr = list(delivery_rows(mid, info, innings)); deliveries.extend(dr)
            ba, bo, ir = aggregate_scorecards(mid, info, innings)
            batting.extend(ba); bowling.extend(bo); innings_out.extend(ir)
        except Exception as e:
            print(f"SKIP {p.name}: {e}", file=sys.stderr)
    def write_csv(name, rows):
        if not rows:
            (OUT/name).write_text("", encoding="utf-8"); return
        cols = list(dict.fromkeys(k for r in rows for k in r.keys()))
        with (OUT/name).open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    write_csv("matches.csv", matches)
    write_csv("innings_score.csv", innings_out)
    write_csv("batting_scorecards.csv", batting)
    write_csv("bowling_scorecards.csv", bowling)
    write_csv("ball_by_ball.csv", deliveries)
    with (OUT/"matches.json").open("w",encoding="utf-8") as f:
        json.dump(matches,f,ensure_ascii=False,indent=2)
    # Copy complete source JSON for every selected match.
    selected_ids = {r["match_id"] for r in matches}
    selected_dir = OUT/"raw_match_json"; selected_dir.mkdir(exist_ok=True)
    for mid in selected_ids:
        src = RAW/(mid+".json")
        if src.exists():
            (selected_dir/src.name).write_bytes(src.read_bytes())
    report = {
        "date_range":[str(START),str(END)],"selected_match_count":len(matches),
        "delivery_count":len(deliveries),"batting_rows":len(batting),
        "bowling_rows":len(bowling),"innings_rows":len(innings_out),
        "ranking_config":str(CONFIG.relative_to(ROOT)),
        "coverage_note":"Cricsheet archive only; not guaranteed to contain every international match. Verify missing matches against official scorecards."
    }
    (OUT/"build_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__ == "__main__":
    main()
