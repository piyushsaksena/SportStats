# SportStats Cricket Historical Dataset Starter

## Scope
- Dates: 2023-01-01 to 2026-11-28 (inclusive)
- Gender: men's and women's
- Formats: Test, ODI, T20I
- Team filter: separate top-10 list for each gender and format

## Why this is a starter, not a completed scorecard dump
Cricsheet provides downloadable ball-by-ball JSON and experimental CSV. Coverage is not complete for every international match, and some matches are withheld. Also, ICC ranking snapshots must be frozen for the exact cutoff date before the top-10 team filter can be applied. The script therefore does not guess the team lists or fabricate missing matches.

## Run
1. Install Python 3.10+.
2. Copy `config/top10_teams.example.json` to `config/top10_teams.json`.
3. Fill each list with the exact teams from the ICC rankings snapshot you choose for 2026-11-28.
4. Run:
   `python build_dataset.py`
5. Outputs are written to `data/processed/`.

The first run downloads Cricsheet's full JSON archive (large; allow time and disk space).

## Outputs
- `matches.json`, `matches.csv`: match metadata and result
- `innings_score.csv`: innings totals
- `batting_scorecards.csv`: batter runs, balls, boundaries, strike rate, dismissal
- `bowling_scorecards.csv`: overs, maidens, conceded runs, wickets, economy
- `ball_by_ball.csv`: delivery-level data including extras and dismissals
- `raw_match_json/`: original source JSON for selected matches
- `build_report.json`: counts and coverage note

## Important data notes
- This is ball-by-ball-derived data, not an official complete scorecard feed.
- Bowling figures are derived from deliveries; validate edge cases (penalty runs, unusual dismissals, innings forfeits, super overs) before using for model training.
- The current script treats a legal delivery as one without wides/no-balls. Some scorecard conventions have edge cases; verify against source scorecards.
- Cricsheet does not guarantee full historical coverage. Cross-check match inventory with ICC/ESPNcricinfo and add missing official scorecards from a licensed source.
- Respect Cricsheet's terms/licence and attribution requirements before redistributing the resulting dataset.
