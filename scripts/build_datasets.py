"""Builds standard datasets for SportStats:
- cricket.json (ODI, T20, Test, Top 50 players, 2026 matches, upcoming/recent, records, history, major tournaments)
- football.json (Top 50 players, 2026 matches, upcoming/recent, records, history, major tournaments)
- tennis.json (Top 50 players, 2026 matches, upcoming/recent, records, history, major tournaments)
- basketball.json (Top 50 players, 2026 matches, upcoming/recent, records, history, major tournaments)
"""

import json
from pathlib import Path

DATASETS_DIR = Path(__file__).resolve().parent.parent / "data" / "datasets"
DATASETS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. CRICKET DATASET
# -------------------------------------------------------------
cricket_top_50 = [
    {"rank": 1, "name": "Virat Kohli", "country": "India", "flag": "🇮🇳", "role": "Top-Order Batter", "tests": 115, "test_runs": 8848, "test_avg": 49.15, "odis": 292, "odi_runs": 13848, "odi_avg": 58.67, "t20is": 125, "t20i_runs": 4188, "t20i_sr": 137.04, "hundreds": 80, "honors": "50 ODI 100s, 2011 CWC, 2013 CT, 2024 T20 WC"},
    {"rank": 2, "name": "Rohit Sharma", "country": "India", "flag": "🇮🇳", "role": "Opening Batter / Captain", "tests": 59, "test_runs": 4137, "test_avg": 45.46, "odis": 262, "odi_runs": 10709, "odi_avg": 49.12, "t20is": 159, "t20i_runs": 4231, "t20i_sr": 140.89, "hundreds": 48, "honors": "2024 T20 WC Winning Captain, 264 ODI Highest Score"},
    {"rank": 3, "name": "Jasprit Bumrah", "country": "India", "flag": "🇮🇳", "role": "Fast Bowler", "tests": 36, "test_wkts": 159, "test_avg": 20.69, "odis": 89, "odi_wkts": 149, "odi_avg": 23.55, "t20is": 70, "t20i_wkts": 89, "t20i_econ": 6.27, "hundreds": 0, "honors": "ICC Men's Player of the Tournament 2024, World #1 Bowler"},
    {"rank": 4, "name": "Travis Head", "country": "Australia", "flag": "🇦🇺", "role": "Opening Batter", "tests": 49, "test_runs": 3173, "test_avg": 41.75, "odis": 65, "odi_runs": 2392, "odi_avg": 42.71, "t20is": 38, "t20i_runs": 1092, "t20i_sr": 158.49, "hundreds": 12, "honors": "Player of the Match in 2023 WTC Final & 2023 CWC Final"},
    {"rank": 5, "name": "Pat Cummins", "country": "Australia", "flag": "🇦🇺", "role": "Fast Bowler / Captain", "tests": 62, "test_wkts": 269, "test_avg": 22.53, "odis": 88, "odi_wkts": 141, "odi_avg": 28.14, "t20is": 57, "t20i_wkts": 66, "t20i_econ": 7.42, "hundreds": 0, "honors": "2023 WTC & 2023 CWC Winning Captain, Allan Border Medalist"},
    {"rank": 6, "name": "Heinrich Klaasen", "country": "South Africa", "flag": "🇿🇦", "role": "Wicketkeeper-Batter", "tests": 4, "test_runs": 104, "test_avg": 13.00, "odis": 54, "odi_runs": 1716, "odi_avg": 42.90, "t20is": 52, "t20i_runs": 1000, "t20i_sr": 147.27, "hundreds": 4, "honors": "Highest T20 strike rate vs spin worldwide (174.5)"},
    {"rank": 7, "name": "Kane Williamson", "country": "New Zealand", "flag": "🇳🇿", "role": "Top-Order Batter", "tests": 100, "test_runs": 8743, "test_avg": 54.98, "odis": 165, "odi_runs": 6810, "odi_avg": 48.64, "t20is": 93, "t20i_runs": 2575, "t20i_sr": 123.08, "hundreds": 45, "honors": "Inaugural WTC 2021 Winning Captain, 2019 CWC Player of the Tourney"},
    {"rank": 8, "name": "Babar Azam", "country": "Pakistan", "flag": "🇵🇰", "role": "Top-Order Batter", "tests": 52, "test_runs": 3898, "test_avg": 45.85, "odis": 117, "odi_runs": 5729, "odi_avg": 56.72, "t20is": 123, "t20i_runs": 4145, "t20i_sr": 129.08, "hundreds": 31, "honors": "Former ICC #1 all formats, ICC ODI Cricketer of the Year 2021 & 2022"},
    {"rank": 9, "name": "Joe Root", "country": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "role": "Middle-Order Batter", "tests": 143, "test_runs": 12274, "test_avg": 50.71, "odis": 171, "odi_runs": 6522, "odi_avg": 47.60, "t20is": 32, "t20i_runs": 893, "t20i_sr": 126.30, "hundreds": 50, "honors": "England's all-time leading Test centurion, 2019 CWC Champion"},
    {"rank": 10, "name": "Rashid Khan", "country": "Afghanistan", "flag": "🇦🇫", "role": "Leg-Spin All-Rounder", "tests": 5, "test_wkts": 34, "test_avg": 22.35, "odis": 105, "odi_wkts": 190, "odi_avg": 20.03, "t20is": 93, "t20i_wkts": 150, "t20i_econ": 6.07, "hundreds": 0, "honors": "Fastest to 100 ODI wickets, 2024 T20 WC Semi-Final Captain"},
    {"rank": 11, "name": "Shubman Gill", "country": "India", "flag": "🇮🇳", "role": "Opening Batter", "tests": 25, "test_runs": 1492, "test_avg": 35.52, "odis": 47, "odi_runs": 2328, "odi_avg": 58.20, "t20is": 21, "t20i_runs": 578, "t20i_sr": 139.27, "hundreds": 10, "honors": "Double century in ODIs (208 vs NZ), Youngest ODI double-centurion"},
    {"rank": 12, "name": "Suryakumar Yadav", "country": "India", "flag": "🇮🇳", "role": "Batter (T20I Captain)", "tests": 1, "test_runs": 8, "test_avg": 8.00, "odis": 37, "odi_runs": 773, "odi_avg": 25.76, "t20is": 71, "t20i_runs": 2432, "t20i_sr": 169.47, "hundreds": 4, "honors": "2x ICC Men's T20I Cricketer of the Year, Iconic catch in 2024 final"},
    {"rank": 13, "name": "Ravindra Jadeja", "country": "India", "flag": "🇮🇳", "role": "All-Rounder", "tests": 72, "test_runs": 3036, "test_avg": 36.14, "odis": 197, "odi_runs": 2756, "odi_avg": 32.42, "t20is": 74, "t20i_runs": 515, "t20i_sr": 127.16, "hundreds": 4, "honors": "World #1 Test All-Rounder, 500+ intl wickets & 6,000+ runs"},
    {"rank": 14, "name": "Mitchell Starc", "country": "Australia", "flag": "🇦🇺", "role": "Fast Bowler", "tests": 89, "test_wkts": 358, "test_avg": 27.74, "odis": 121, "odi_wkts": 236, "odi_avg": 22.96, "t20is": 65, "t20i_wkts": 79, "t20i_econ": 7.74, "hundreds": 0, "honors": "Leading wicket-taker in 2015 & 2019 CWC, 2x World Champion"},
    {"rank": 15, "name": "Quinton de Kock", "country": "South Africa", "flag": "🇿🇦", "role": "Wicketkeeper-Batter", "tests": 54, "test_runs": 3300, "test_avg": 38.82, "odis": 155, "odi_runs": 6770, "odi_avg": 45.74, "t20is": 92, "t20i_runs": 2584, "t20i_sr": 138.32, "hundreds": 28, "honors": "4 centuries in single World Cup (2023), 2024 T20 WC Finalist"},
    {"rank": 16, "name": "Jos Buttler", "country": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "role": "Wicketkeeper-Batter / Captain", "tests": 57, "test_runs": 2907, "test_avg": 31.94, "odis": 181, "odi_runs": 5022, "odi_avg": 39.54, "t20is": 124, "t20i_runs": 3264, "t20i_sr": 146.30, "hundreds": 12, "honors": "2022 T20 WC Winning Captain, 2019 ODI World Champion"},
    {"rank": 17, "name": "Glenn Maxwell", "country": "Australia", "flag": "🇦🇺", "role": "Batting All-Rounder", "tests": 7, "test_runs": 339, "test_avg": 26.07, "odis": 142, "odi_runs": 3934, "odi_avg": 35.44, "t20is": 106, "t20i_runs": 2600, "t20i_sr": 155.50, "hundreds": 9, "honors": "Historic 201* vs Afghanistan (2023 CWC), fastest CWC 100 (40 balls)"},
    {"rank": 18, "name": "Trent Boult", "country": "New Zealand", "flag": "🇳🇿", "role": "Fast Bowler", "tests": 78, "test_wkts": 317, "test_avg": 27.49, "odis": 114, "odi_wkts": 211, "odi_avg": 24.31, "t20is": 61, "t20i_wkts": 83, "t20i_econ": 7.73, "hundreds": 0, "honors": "WTC 2021 Champion, World Cup hat-trick (2019)"},
    {"rank": 19, "name": "Shaheen Shah Afridi", "country": "Pakistan", "flag": "🇵🇰", "role": "Fast Bowler", "tests": 29, "test_wkts": 113, "test_avg": 26.69, "odis": 53, "odi_wkts": 104, "odi_avg": 23.94, "t20is": 70, "t20i_wkts": 96, "t20i_econ": 7.75, "hundreds": 0, "honors": "Garfield Sobers Trophy 2021, Elite opening-over strike bowler"},
    {"rank": 20, "name": "Hardik Pandya", "country": "India", "flag": "🇮🇳", "role": "Fast-Bowling All-Rounder", "tests": 11, "test_runs": 532, "test_avg": 31.29, "odis": 86, "odi_runs": 1769, "odi_avg": 34.01, "t20is": 102, "t20i_runs": 1523, "t20i_sr": 140.49, "hundreds": 1, "honors": "Defended final over in 2024 T20 WC Final (3/20), ICC #1 All-Rounder"},
    {"rank": 21, "name": "Kagiso Rabada", "country": "South Africa", "flag": "🇿🇦", "role": "Fast Bowler", "tests": 62, "test_wkts": 291, "test_avg": 22.05, "odis": 101, "odi_wkts": 157, "odi_avg": 27.77, "t20is": 65, "t20i_wkts": 71, "t20i_econ": 8.28, "hundreds": 0, "honors": "Fastest South African to 250 Test wickets, Purple Cap winner"},
    {"rank": 22, "name": "Ben Stokes", "country": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "role": "All-Rounder / Test Captain", "tests": 105, "test_runs": 6508, "test_avg": 35.75, "odis": 114, "odi_runs": 3159, "odi_avg": 38.99, "t20is": 43, "t20i_runs": 585, "t20i_sr": 128.00, "hundreds": 18, "honors": "Headingley 2019 miracle, 2019 CWC Final Player of Match, 2022 T20 WC Final"},
    {"rank": 23, "name": "Steve Smith", "country": "Australia", "flag": "🇦🇺", "role": "Middle-Order Batter", "tests": 109, "test_runs": 9685, "test_avg": 56.97, "odis": 158, "odi_runs": 5446, "odi_avg": 43.91, "t20is": 67, "t20i_runs": 1094, "t20i_sr": 125.45, "hundreds": 44, "honors": "2x ICC Test Cricketer of the Decade, 32 Test 100s, 2x CWC Champ"},
    {"rank": 24, "name": "KL Rahul", "country": "India", "flag": "🇮🇳", "role": "Wicketkeeper-Batter", "tests": 50, "test_runs": 2863, "test_avg": 34.08, "odis": 75, "odi_runs": 2820, "odi_avg": 50.35, "t20is": 72, "t20i_runs": 2265, "t20i_sr": 139.12, "hundreds": 17, "honors": "Fastest 100 by an Indian in World Cup (62 balls)"},
    {"rank": 25, "name": "Mohammed Shami", "country": "India", "flag": "🇮🇳", "role": "Fast Bowler", "tests": 64, "test_wkts": 229, "test_avg": 27.71, "odis": 101, "odi_wkts": 195, "odi_avg": 23.68, "t20is": 23, "t20i_wkts": 24, "t20i_econ": 8.94, "hundreds": 0, "honors": "Leading wicket-taker 2023 CWC (24 wickets in 7 matches)"},
    {"rank": 26, "name": "Rishabh Pant", "country": "India", "flag": "🇮🇳", "role": "Wicketkeeper-Batter", "tests": 33, "test_runs": 2271, "test_avg": 43.67, "odis": 30, "odi_runs": 865, "odi_avg": 34.60, "t20is": 76, "t20i_runs": 1209, "t20i_sr": 127.26, "hundreds": 6, "honors": "Gabba 2021 hero (89*), 2024 T20 World Cup Champion"},
    {"rank": 27, "name": "David Warner", "country": "Australia", "flag": "🇦🇺", "role": "Opening Batter", "tests": 112, "test_runs": 8786, "test_avg": 44.59, "odis": 161, "odi_runs": 6932, "odi_avg": 45.30, "t20is": 110, "t20i_runs": 3277, "t20i_sr": 142.47, "hundreds": 49, "honors": "2x ODI CWC, 1x T20 WC, 1x WTC, 335* vs Pakistan"},
    {"rank": 28, "name": "Mitchell Marsh", "country": "Australia", "flag": "🇦🇺", "role": "All-Rounder / T20 Captain", "tests": 40, "test_runs": 2008, "test_avg": 30.89, "odis": 89, "odi_runs": 2788, "odi_avg": 36.68, "t20is": 60, "t20i_runs": 1500, "t20i_sr": 135.00, "hundreds": 6, "honors": "2021 T20 WC Final Player of Match, Allan Border Medal 2024"},
    {"rank": 29, "name": "Josh Hazlewood", "country": "Australia", "flag": "🇦🇺", "role": "Fast Bowler", "tests": 70, "test_wkts": 273, "test_avg": 24.82, "odis": 88, "odi_wkts": 132, "odi_avg": 26.28, "t20is": 51, "t20i_wkts": 67, "t20i_econ": 7.40, "hundreds": 0, "honors": "World #1 in Test, ODI, and T20I simultaneously (2022)"},
    {"rank": 30, "name": "Harry Brook", "country": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "role": "Middle-Order Batter", "tests": 19, "test_runs": 1819, "test_avg": 56.84, "odis": 20, "odi_runs": 612, "odi_avg": 34.00, "t20is": 39, "t20i_runs": 707, "t20i_sr": 145.77, "hundreds": 7, "honors": "Fastest to 1,000 Test runs by balls faced in history"},
    {"rank": 31, "name": "Rinku Singh", "country": "India", "flag": "🇮🇳", "role": "Finisher / Batter", "tests": 0, "test_runs": 0, "test_avg": 0, "odis": 2, "odi_runs": 55, "odi_avg": 55.00, "t20is": 23, "t20i_runs": 418, "t20i_sr": 174.16, "hundreds": 0, "honors": "Unbeaten finisher with 174+ T20I strike rate, 5 consecutive sixes in IPL"},
    {"rank": 32, "name": "Wanindu Hasaranga", "country": "Sri Lanka", "flag": "🇱🇰", "role": "Leg-Spin All-Rounder", "tests": 4, "test_wkts": 4, "test_avg": 100.0, "odis": 54, "odi_wkts": 84, "odi_avg": 25.86, "t20is": 68, "t20i_wkts": 110, "t20i_econ": 6.88, "hundreds": 1, "honors": "Leading wicket-taker in 2021 & 2022 T20 World Cups, Asia Cup 2022 MVP"},
    {"rank": 33, "name": "Kuldeep Yadav", "country": "India", "flag": "🇮🇳", "role": "Left-Arm Wrist Spinner", "tests": 12, "test_wkts": 53, "test_avg": 21.05, "odis": 106, "odi_wkts": 172, "odi_avg": 26.01, "t20is": 40, "t20i_wkts": 69, "t20i_econ": 6.74, "hundreds": 0, "honors": "2x ODI Hat-tricks, 2024 T20 WC Champion"},
    {"rank": 34, "name": "Daryl Mitchell", "country": "New Zealand", "flag": "🇳🇿", "role": "Batting All-Rounder", "tests": 24, "test_runs": 1608, "test_avg": 48.72, "odis": 39, "odi_runs": 1577, "odi_avg": 52.56, "t20is": 66, "t20i_runs": 1260, "t20i_sr": 137.99, "hundreds": 8, "honors": "ICC Men's Cricketer of the Month, 552 runs in 2023 CWC"},
    {"rank": 35, "name": "Devon Conway", "country": "New Zealand", "flag": "🇳🇿", "role": "Opening Batter / Keeper", "tests": 20, "test_runs": 1497, "test_avg": 41.58, "odis": 32, "odi_runs": 1221, "odi_avg": 45.22, "t20is": 47, "t20i_runs": 1408, "t20i_sr": 128.58, "hundreds": 9, "honors": "Double century on Test debut at Lord's (200), WTC Champion"},
    {"rank": 36, "name": "Adam Zampa", "country": "Australia", "flag": "🇦🇺", "role": "Leg-Spin Bowler", "tests": 0, "test_wkts": 0, "test_avg": 0, "odis": 99, "odi_wkts": 169, "odi_avg": 28.00, "t20is": 88, "t20i_wkts": 111, "t20i_econ": 7.20, "hundreds": 0, "honors": "2021 T20 WC & 2023 CWC Winner, Australia's all-time leading T20I spinner"},
    {"rank": 37, "name": "Aiden Markram", "country": "South Africa", "flag": "🇿🇦", "role": "Top-Order Batter / Captain", "tests": 39, "test_runs": 2465, "test_avg": 35.72, "odis": 68, "odi_runs": 2185, "odi_avg": 37.03, "t20is": 49, "t20i_runs": 1256, "t20i_sr": 145.70, "hundreds": 8, "honors": "Captain of SA 2024 T20 WC Finalists, U19 CWC Winning Captain"},
    {"rank": 38, "name": "Anrich Nortje", "country": "South Africa", "flag": "🇿🇦", "role": "Express Fast Bowler", "tests": 19, "test_wkts": 70, "test_avg": 26.71, "odis": 31, "odi_wkts": 36, "odi_avg": 27.27, "t20is": 37, "t20i_wkts": 48, "t20i_econ": 7.02, "hundreds": 0, "honors": "Fastest ball recorded in T20 WC (153.3 km/h), 2024 T20 WC Finalist"},
    {"rank": 39, "name": "Shreyas Iyer", "country": "India", "flag": "🇮🇳", "role": "Middle-Order Batter", "tests": 14, "test_runs": 811, "test_avg": 36.86, "odis": 62, "odi_runs": 2421, "odi_avg": 47.47, "t20is": 51, "t20i_runs": 1104, "t20i_sr": 136.12, "hundreds": 6, "honors": "530 runs in 2023 CWC including 105 in semi-final vs NZ, IPL winning captain"},
    {"rank": 40, "name": "Axar Patel", "country": "India", "flag": "🇮🇳", "role": "Left-Arm All-Rounder", "tests": 14, "test_runs": 646, "test_avg": 35.88, "odis": 57, "odi_runs": 481, "odi_avg": 20.04, "t20is": 60, "t20i_runs": 450, "t20i_sr": 142.40, "hundreds": 0, "honors": "Match-defining 47 runs & 3 wickets in 2024 T20 WC Final, 50+ Test wickets"},
    {"rank": 41, "name": "Lockie Ferguson", "country": "New Zealand", "flag": "🇳🇿", "role": "Fast Bowler", "tests": 1, "test_wkts": 0, "test_avg": 0, "odis": 65, "odi_wkts": 99, "odi_avg": 31.78, "t20is": 42, "t20i_wkts": 61, "t20i_econ": 7.06, "hundreds": 0, "honors": "World Record: 4 overs, 4 maidens, 3 wickets vs PNG in 2024 T20 WC"},
    {"rank": 42, "name": "Marco Jansen", "country": "South Africa", "flag": "🇿🇦", "role": "Left-Arm Fast All-Rounder", "tests": 13, "test_wkts": 49, "test_avg": 22.79, "odis": 23, "odi_runs": 410, "odi_avg": 29.28, "t20is": 17, "t20i_wkts": 17, "t20i_econ": 8.70, "hundreds": 0, "honors": "2024 T20 WC Finalist, 6ft 8in left-arm pace & powerful lower-order hitting"},
    {"rank": 43, "name": "Sikandar Raza", "country": "Zimbabwe", "flag": "🇿🇼", "role": "All-Rounder / Captain", "tests": 17, "test_runs": 1187, "test_avg": 35.96, "odis": 142, "odi_runs": 4154, "odi_avg": 36.43, "t20is": 91, "t20i_runs": 2037, "t20i_sr": 134.54, "hundreds": 8, "honors": "ICC T20I Team of the Year 2022 & 2023, Zimbabwe's greatest modern match-winner"},
    {"rank": 44, "name": "Nicholas Pooran", "country": "West Indies", "flag": "🌴", "role": "Wicketkeeper-Batter", "tests": 0, "test_runs": 0, "test_avg": 0, "odis": 61, "odi_runs": 1983, "odi_avg": 39.66, "t20is": 98, "t20i_runs": 2188, "t20i_sr": 136.32, "hundreds": 3, "honors": "Most T20 sixes in a calendar year worldwide (150+ in 2024)"},
    {"rank": 45, "name": "Shai Hope", "country": "West Indies", "flag": "🌴", "role": "Top-Order Batter / ODI Captain", "tests": 38, "test_runs": 1726, "test_avg": 25.01, "odis": 124, "odi_runs": 5177, "odi_avg": 50.26, "t20is": 32, "t20i_runs": 692, "t20i_sr": 133.59, "hundreds": 16, "honors": "Averages 50+ in ODIs with 16 hundreds, Twin hundreds at Headingley (2017)"},
    {"rank": 46, "name": "Rahmanullah Gurbaz", "country": "Afghanistan", "flag": "🇦🇫", "role": "Opening Batter / Keeper", "tests": 1, "test_runs": 51, "test_avg": 25.50, "odis": 40, "odi_runs": 1467, "odi_avg": 38.60, "t20is": 63, "t20i_runs": 1657, "t20i_sr": 135.37, "hundreds": 6, "honors": "Leading run-scorer in 2024 T20 World Cup (281 runs)"},
    {"rank": 47, "name": "Ibrahim Zadran", "country": "Afghanistan", "flag": "🇦🇫", "role": "Opening Batter", "tests": 7, "test_runs": 541, "test_avg": 38.64, "odis": 30, "odi_runs": 1374, "odi_avg": 49.07, "t20is": 47, "t20i_runs": 1133, "t20i_sr": 111.40, "hundreds": 5, "honors": "First Afghan to score a World Cup century (129* vs Australia 2023)"},
    {"rank": 48, "name": "Pathum Nissanka", "country": "Sri Lanka", "flag": "🇱🇰", "role": "Opening Batter", "tests": 11, "test_runs": 673, "test_avg": 39.58, "odis": 55, "odi_runs": 2225, "odi_avg": 43.62, "t20is": 54, "t20i_runs": 1380, "t20i_sr": 118.86, "hundreds": 6, "honors": "First Sri Lankan to score an ODI double hundred (210* vs AFG 2024)"},
    {"rank": 49, "name": "Maheesh Theekshana", "country": "Sri Lanka", "flag": "🇱🇰", "role": "Mystery Spinner", "tests": 2, "test_wkts": 5, "test_avg": 36.40, "odis": 45, "odi_wkts": 55, "odi_avg": 30.00, "t20is": 49, "t20i_wkts": 50, "t20i_econ": 6.64, "hundreds": 0, "honors": "Asia Cup 2022 Champion, elite defensive powerplay economy"},
    {"rank": 50, "name": "Shakib Al Hasan", "country": "Bangladesh", "flag": "🇧🇩", "role": "All-Rounder", "tests": 67, "test_runs": 4505, "test_avg": 38.50, "odis": 247, "odi_runs": 7570, "odi_avg": 37.29, "t20is": 129, "t20i_runs": 2551, "t20i_sr": 121.18, "hundreds": 14, "honors": "Only cricketer with 7,000+ runs & 300+ wickets in ODIs, 600+ runs & 10 wkts in 2019 CWC"}
]

cricket_data = {
    "sport": "Cricket",
    "governing_body": "International Cricket Council (ICC)",
    "headquarters": "Dubai, United Arab Emirates",
    "founded_year": 1909,
    "history": {
        "summary": "Cricket originated in southeast England in the late 16th century, becoming England's national sport in the 18th century and spreading globally via the British Empire. The inaugural international match was played between the United States and Canada in 1844 in Manhattan. The first recognized Test match took place in 1877 between Australia and England at the Melbourne Cricket Ground.",
        "key_eras": [
            {"era": "The Golden Age (1890–1914)", "description": "Formative international rivalries, timeless Test matches, and the establishment of the Imperial Cricket Conference (now ICC) in 1909."},
            {"era": "The Bradman & Post-War Era (1928–1970)", "description": "Sir Donald Bradman's unbeatable 99.94 Test average; introduction of defensive tactics and expanded Commonwealth membership."},
            {"era": "Limited Overs Revolution (1971–2002)", "description": "Birth of One Day Internationals in 1971, the inaugural 1975 Prudential World Cup, and Kerry Packer's World Series Cricket introducing colored clothing, white balls, and floodlights."},
            {"era": "T20 Era & Franchise Boom (2003–Present)", "description": "Introduction of Twenty20 in 2003, the inaugural 2007 ICC World Twenty20 won by India, launch of the Indian Premier League (2008), and formation of the World Test Championship (2019)."}
        ]
    },
    "major_tournaments": [
        {"name": "ICC Men's Cricket World Cup", "format": "ODI (50-over)", "frequency": "Every 4 Years", "first_edition": 1975, "current_holder": "Australia (2023)", "description": "The premier championship of international cricket with 50-over innings. Australia has won a record 6 titles."},
        {"name": "ICC Men's T20 World Cup", "format": "T20 (20-over)", "frequency": "Every 2 Years", "first_edition": 2007, "current_holder": "India (2024)", "description": "High-octane 20-over world championship. India became 2-time champions in 2024 after an undefeated campaign."},
        {"name": "ICC World Test Championship (WTC)", "format": "Test (5-Day)", "frequency": "2-Year Cycle", "first_edition": 2019, "current_holder": "Australia (2023)", "description": "Two-year league table of premier Test nations culminating in a grand one-off final at Lord's or The Oval."},
        {"name": "ICC Champions Trophy", "format": "ODI (50-over)", "frequency": "Every 4 Years", "first_edition": 1998, "current_holder": "Pakistan (2017)", "description": "Elite 8-nation ODI shootout featuring only top-ranked national teams."},
        {"name": "The Ashes", "format": "Test (5-Day)", "frequency": "Biennial", "first_edition": 1882, "current_holder": "Australia (Retained 2023)", "description": "Cricket's oldest and most historic bilateral Test rivalry between England and Australia."},
        {"name": "Indian Premier League (IPL)", "format": "T20 Franchise", "frequency": "Annual", "first_edition": 2008, "current_holder": "Kolkata Knight Riders (2024)", "description": "The world's richest and most followed domestic franchise cricket league."}
    ],
    "formats": {
        "ODI": {
            "name": "One Day International",
            "overs": "50 overs per side",
            "duration": "8 hours",
            "rankings": [
                {"rank": 1, "team": "India", "rating": 118, "pts": "5,200"},
                {"rank": 2, "team": "Australia", "rating": 116, "pts": "4,408"},
                {"rank": 3, "team": "South Africa", "rating": 110, "pts": "3,410"},
                {"rank": 4, "team": "Pakistan", "rating": 106, "pts": "3,180"},
                {"rank": 5, "team": "New Zealand", "rating": 101, "pts": "3,636"}
            ]
        },
        "T20": {
            "name": "Twenty20 International",
            "overs": "20 overs per side",
            "duration": "3 hours 20 mins",
            "rankings": [
                {"rank": 1, "team": "India", "rating": 268, "pts": "18,480"},
                {"rank": 2, "team": "Australia", "rating": 258, "pts": "12,912"},
                {"rank": 3, "team": "England", "rating": 252, "pts": "11,854"},
                {"rank": 4, "team": "South Africa", "rating": 250, "pts": "11,250"},
                {"rank": 5, "team": "West Indies", "rating": 248, "pts": "12,410"}
            ]
        },
        "Test": {
            "name": "Test Match Cricket",
            "overs": "Unlimited (90 overs/day, up to 5 days)",
            "duration": "5 Days",
            "rankings": [
                {"rank": 1, "team": "Australia", "rating": 124, "pts": "4,328"},
                {"rank": 2, "team": "India", "rating": 120, "pts": "4,560"},
                {"rank": 3, "team": "England", "rating": 108, "pts": "4,644"},
                {"rank": 4, "team": "South Africa", "rating": 103, "pts": "2,472"},
                {"rank": 5, "team": "New Zealand", "rating": 96, "pts": "2,688"}
            ]
        }
    },
    "matches_2026": [
        {
            "id": "c-match-1",
            "title": "ICC Men's T20 World Cup 2026 — Semi-Final 1",
            "format": "T20",
            "date": "14 Nov 2026",
            "venue": "Eden Gardens, Kolkata",
            "status": "LIVE",
            "team1": {"name": "India", "flag": "🇮🇳", "score": "198/4", "overs": "20.0"},
            "team2": {"name": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "score": "142/5", "overs": "15.2"},
            "note": "England need 57 runs from 28 balls (Required Run Rate: 12.21)",
            "key_performers": "Suryakumar Yadav 74* (38b), Jasprit Bumrah 3/18 (3.0 ov) | Jos Buttler 52 (29b)"
        },
        {
            "id": "c-match-2",
            "title": "Border-Gavaskar Trophy 2026 — 1st Test (Day 3)",
            "format": "Test",
            "date": "22 Nov 2026",
            "venue": "Optus Stadium, Perth",
            "status": "SCHEDULED",
            "team1": {"name": "Australia", "flag": "🇦🇺", "score": "Upcoming", "overs": ""},
            "team2": {"name": "India", "flag": "🇮🇳", "score": "Upcoming", "overs": ""},
            "note": "World Test Championship 2025-27 cycle fixture",
            "key_performers": "Pat Cummins vs Jasprit Bumrah • Virat Kohli vs Steve Smith"
        },
        {
            "id": "c-match-3",
            "title": "ICC Champions Trophy 2026 — Group A",
            "format": "ODI",
            "date": "08 Nov 2026",
            "venue": "Gaddafi Stadium, Lahore",
            "status": "COMPLETED",
            "team1": {"name": "India", "flag": "🇮🇳", "score": "312/6", "overs": "50.0"},
            "team2": {"name": "Pakistan", "flag": "🇵🇰", "score": "268 all out", "overs": "47.2"},
            "note": "India won by 44 runs • Player of the Match: Shubman Gill (112)",
            "key_performers": "Shubman Gill 112 (104b), Kuldeep Yadav 4/42 | Babar Azam 78 (82b)"
        }
    ],
    "team_fixtures": {
        "india": {
            "upcoming": [
                {"opp": "vs England (T20 WC Semi-Final)", "date": "14 Nov 2026", "venue": "Kolkata", "comp": "ICC T20 World Cup"},
                {"opp": "vs Australia (1st Test)", "date": "22 Nov 2026", "venue": "Perth", "comp": "Border-Gavaskar Trophy"},
                {"opp": "vs Australia (2nd Test)", "date": "06 Dec 2026", "venue": "Adelaide Oval", "comp": "Border-Gavaskar Trophy"}
            ],
            "recent": [
                {"opp": "vs Pakistan (T20 Super 8)", "date": "08 Nov 2026", "res": "WON", "score": "181/6 vs 163/8 (by 18 runs)", "hero": "Hardik Pandya 42* & 2/24"},
                {"opp": "vs South Africa (ODI)", "date": "02 Nov 2026", "res": "WON", "score": "296/5 vs 245 (by 51 runs)", "hero": "Virat Kohli 104*"},
                {"opp": "vs New Zealand (3rd Test)", "date": "28 Oct 2026", "res": "WON", "score": "India won by 7 wickets", "hero": "Ravindra Jadeja 5/48 & 4/33"},
                {"opp": "vs Australia (T20 Super 8)", "date": "22 Oct 2026", "res": "WON", "score": "205/5 vs 181/7 (by 24 runs)", "hero": "Rohit Sharma 92 (41)"},
                {"opp": "vs Sri Lanka (ODI)", "date": "15 Oct 2026", "res": "WON", "score": "320/4 vs 210 (by 110 runs)", "hero": "Shubman Gill 121"}
            ]
        }
    },
    "top_50_players": cricket_top_50
}

with open(DATASETS_DIR / "cricket.json", "w", encoding="utf-8") as f:
    json.dump(cricket_data, f, indent=2, ensure_ascii=False)
print("Saved data/datasets/cricket.json")
# -------------------------------------------------------------
# 2. FOOTBALL DATASET
# -------------------------------------------------------------
football_top_50 = [
    {"rank": 1, "name": "Vinícius Júnior", "country": "Brazil", "flag": "🇧🇷", "club": "Real Madrid", "pos": "Left Winger", "goals": 24, "assists": 11, "trophies": "2x Champions League, 3x La Liga", "honors": "UCL Player of the Season 2023-24, Real Madrid #7"},
    {"rank": 2, "name": "Rodri", "country": "Spain", "flag": "🇪🇸", "club": "Manchester City", "pos": "Defensive Midfielder", "goals": 9, "assists": 14, "trophies": "Ballon d'Or 2024, EURO 2024 MVP, 4x Premier League", "honors": "74-game unbeaten club streak, World #1 Midfielder"},
    {"rank": 3, "name": "Erling Haaland", "country": "Norway", "flag": "🇳🇴", "club": "Manchester City", "pos": "Striker", "goals": 38, "assists": 6, "trophies": "Treble 2023, 2x Premier League Golden Boot", "honors": "Fastest to 100 Premier League goals in history"},
    {"rank": 4, "name": "Kylian Mbappé", "country": "France", "flag": "🇫🇷", "club": "Real Madrid", "pos": "Forward", "goals": 34, "assists": 9, "trophies": "2018 World Cup Winner, 2022 Golden Boot (8 goals)", "honors": "World Cup Final Hat-Trick, 6x Ligue 1 Golden Boot"},
    {"rank": 5, "name": "Jude Bellingham", "country": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "club": "Real Madrid", "pos": "Attacking Midfielder", "goals": 23, "assists": 13, "trophies": "La Liga Player of the Year, Champions League 2024", "honors": "Golden Boy 2023, Kopa Trophy"},
    {"rank": 6, "name": "Lamine Yamal", "country": "Spain", "flag": "🇪🇸", "club": "FC Barcelona", "pos": "Right Winger", "goals": 10, "assists": 17, "trophies": "EURO 2024 Champion & Young Player of the Tournament", "honors": "Youngest goalscorer in EURO history (16y 362d), Kopa Trophy 2024"},
    {"rank": 7, "name": "Harry Kane", "country": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "club": "Bayern Munich", "pos": "Striker", "goals": 44, "assists": 12, "trophies": "European Golden Shoe 2024, Bundesliga Top Scorer", "honors": "England's all-time leading goalscorer (68+ goals)"},
    {"rank": 8, "name": "Kevin De Bruyne", "country": "Belgium", "flag": "🇧🇪", "club": "Manchester City", "pos": "Central Midfielder", "goals": 8, "assists": 22, "trophies": "6x Premier League, 1x Champions League", "honors": "2x PFA Players' Player of the Year, 100+ PL assists"},
    {"rank": 9, "name": "Mohamed Salah", "country": "Egypt", "flag": "🇪🇬", "club": "Liverpool", "pos": "Right Winger", "goals": 25, "assists": 14, "trophies": "Premier League, Champions League, 3x Golden Boot", "honors": "Liverpool's all-time top Premier League goalscorer"},
    {"rank": 10, "name": "Florian Wirtz", "country": "Germany", "flag": "🇩🇪", "club": "Bayer Leverkusen", "pos": "Attacking Midfielder", "goals": 18, "assists": 20, "trophies": "Undefeated Bundesliga 2024, DFB-Pokal", "honors": "Bundesliga Player of the Season 2023-24"},
    {"rank": 11, "name": "Phil Foden", "country": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "club": "Manchester City", "pos": "Winger / Playmaker", "goals": 27, "assists": 12, "trophies": "6x Premier League, PFA Player of the Year 2024", "honors": "FWA Footballer of the Year 2024"},
    {"rank": 12, "name": "Bukayo Saka", "country": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "club": "Arsenal", "pos": "Right Winger", "goals": 20, "assists": 14, "trophies": "FA Cup, 2x England Men's Player of the Year", "honors": "Arsenal Player of the Season 2x"},
    {"rank": 13, "name": "Lautaro Martínez", "country": "Argentina", "flag": "🇦🇷", "club": "Inter Milan", "pos": "Striker", "goals": 27, "assists": 7, "trophies": "World Cup 2022, 2x Copa América, Serie A MVP 2024", "honors": "Copa América 2024 Golden Boot & Final match-winner"},
    {"rank": 14, "name": "Lionel Messi", "country": "Argentina", "flag": "🇦🇷", "club": "Inter Miami", "pos": "Playmaker / Forward", "goals": 22, "assists": 16, "trophies": "8x Ballon d'Or, 2022 World Cup Winner, 2x Copa América", "honors": "46 career trophies (most in football history)"},
    {"rank": 15, "name": "Cristiano Ronaldo", "country": "Portugal", "flag": "🇵🇹", "club": "Al Nassr", "pos": "Striker", "goals": 35, "assists": 8, "trophies": "5x Ballon d'Or, 5x Champions League, EURO 2016", "honors": "900+ official career goals (all-time top scorer)"},
    {"rank": 16, "name": "Jamal Musiala", "country": "Germany", "flag": "🇩🇪", "club": "Bayern Munich", "pos": "Attacking Midfielder", "goals": 15, "assists": 11, "trophies": "4x Bundesliga, EURO 2024 Joint Top Scorer", "honors": "Elite dribbling succession rate (71.4%)"},
    {"rank": 17, "name": "Antoine Griezmann", "country": "France", "flag": "🇫🇷", "club": "Atlético Madrid", "pos": "Forward / Playmaker", "goals": 24, "assists": 12, "trophies": "World Cup 2018, UEFA Nations League", "honors": "Atlético Madrid's all-time record goalscorer"},
    {"rank": 18, "name": "Cole Palmer", "country": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "club": "Chelsea", "pos": "Attacking Midfielder", "goals": 25, "assists": 15, "trophies": "Premier League Young Player of the Season 2024", "honors": "4 goals in single first-half vs Brighton (PL record)"},
    {"rank": 19, "name": "Declan Rice", "country": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "club": "Arsenal", "pos": "Defensive Midfielder", "goals": 7, "assists": 10, "trophies": "UEFA Europa Conference League Champion", "honors": "Premier League Team of the Year 2024"},
    {"rank": 20, "name": "William Saliba", "country": "France", "flag": "🇫🇷", "club": "Arsenal", "pos": "Centre-Back", "goals": 2, "assists": 1, "trophies": "EURO 2024 Team of the Tournament", "honors": "Played every single minute of Premier League season"},
    {"rank": 21, "name": "Virgil van Dijk", "country": "Netherlands", "flag": "🇳🇱", "club": "Liverpool", "pos": "Centre-Back / Captain", "goals": 4, "assists": 2, "trophies": "Champions League, Premier League, UEFA Best Player", "honors": "Premier League Player of the Season 2019"},
    {"rank": 22, "name": "Federico Valverde", "country": "Uruguay", "flag": "🇺🇾", "club": "Real Madrid", "pos": "Box-to-Box Midfielder", "goals": 6, "assists": 8, "trophies": "2x Champions League, 3x La Liga", "honors": "Real Madrid #8, 12.4 km distance covered per match"},
    {"rank": 23, "name": "Bernardo Silva", "country": "Portugal", "flag": "🇵🇹", "club": "Manchester City", "pos": "Midfielder / Winger", "goals": 11, "assists": 10, "trophies": "6x Premier League, 1x Champions League", "honors": "3x PFA Team of the Year"},
    {"rank": 24, "name": "Martin Ødegaard", "country": "Norway", "flag": "🇳🇴", "club": "Arsenal", "pos": "Central Midfielder / Captain", "goals": 11, "assists": 11, "trophies": "2x Arsenal Player of the Season", "honors": "Most chances created from open play in PL (102)"},
    {"rank": 25, "name": "Bruno Fernandes", "country": "Portugal", "flag": "🇵🇹", "club": "Manchester United", "pos": "Attacking Midfielder", "goals": 15, "assists": 13, "trophies": "FA Cup 2024, Carabao Cup 2023", "honors": "Most key passes created across Europe's top 5 leagues"},
    {"rank": 26, "name": "Robert Lewandowski", "country": "Poland", "flag": "🇵🇱", "club": "FC Barcelona", "pos": "Striker", "goals": 26, "assists": 9, "trophies": "Champions League 2020, 2x The Best FIFA Men's Player", "honors": "100+ Champions League goals club (all-time #3)"},
    {"rank": 27, "name": "Ruben Dias", "country": "Portugal", "flag": "🇵🇹", "club": "Manchester City", "pos": "Centre-Back", "goals": 1, "assists": 1, "trophies": "Treble 2023, 4x Premier League", "honors": "FWA Footballer of the Year 2021"},
    {"rank": 28, "name": "Thibaut Courtois", "country": "Belgium", "flag": "🇧🇪", "club": "Real Madrid", "pos": "Goalkeeper", "goals": 0, "assists": 0, "trophies": "2x Champions League, 3x La Liga", "honors": "9 saves in 2022 Champions League Final (record)"},
    {"rank": 29, "name": "Alisson Becker", "country": "Brazil", "flag": "🇧🇷", "club": "Liverpool", "pos": "Goalkeeper", "goals": 1, "assists": 3, "trophies": "Champions League, Premier League, Copa América", "honors": "Yashin Trophy 2019, 2x Premier League Golden Glove"},
    {"rank": 30, "name": "Emiliano Martínez", "country": "Argentina", "flag": "🇦🇷", "club": "Aston Villa", "pos": "Goalkeeper", "goals": 0, "assists": 0, "trophies": "World Cup 2022, 2x Copa América, 2x Yashin Trophy", "honors": "World Cup 2022 Golden Glove & historic 123' save"},
    {"rank": 31, "name": "Rodrygo", "country": "Brazil", "flag": "🇧🇷", "club": "Real Madrid", "pos": "Forward / Winger", "goals": 17, "assists": 9, "trophies": "2x Champions League, 3x La Liga", "honors": "Iconic double in 90th & 91st minute vs Man City (2022)"},
    {"rank": 32, "name": "Nico Williams", "country": "Spain", "flag": "🇪🇸", "club": "Athletic Bilbao", "pos": "Left Winger", "goals": 8, "assists": 16, "trophies": "EURO 2024 Champion & Final Player of Match", "honors": "Copa del Rey Champion 2024 with Athletic Club"},
    {"rank": 33, "name": "Dani Carvajal", "country": "Spain", "flag": "🇪🇸", "club": "Real Madrid", "pos": "Right-Back", "goals": 5, "assists": 6, "trophies": "6x Champions League, EURO 2024 Champion", "honors": "Scored opening goal in 2024 Champions League Final"},
    {"rank": 34, "name": "Theo Hernández", "country": "France", "flag": "🇫🇷", "club": "AC Milan", "pos": "Left-Back", "goals": 6, "assists": 11, "trophies": "Serie A Champion, Nations League Champion", "honors": "Fastest sprint speed in Serie A (35.7 km/h)"},
    {"rank": 35, "name": "Joshua Kimmich", "country": "Germany", "flag": "🇩🇪", "club": "Bayern Munich", "pos": "Right-Back / Midfielder", "goals": 4, "assists": 12, "trophies": "8x Bundesliga, 1x Champions League", "honors": "UEFA Champions League Defender of the Season"},
    {"rank": 36, "name": "Luka Modrić", "country": "Croatia", "flag": "🇭🇷", "club": "Real Madrid", "pos": "Central Midfielder / Captain", "goals": 3, "assists": 8, "trophies": "Ballon d'Or 2018, 6x Champions League", "honors": "Most decorated player in Real Madrid history (27 titles)"},
    {"rank": 37, "name": "Son Heung-min", "country": "South Korea", "flag": "🇰🇷", "club": "Tottenham Hotspur", "pos": "Forward / Captain", "goals": 17, "assists": 10, "trophies": "Premier League Golden Boot 2022, Puskás Award 2020", "honors": "First Asian player to win Premier League Golden Boot"},
    {"rank": 38, "name": "Victor Osimhen", "country": "Nigeria", "flag": "🇳🇬", "club": "Galatasaray", "pos": "Striker", "goals": 26, "assists": 5, "trophies": "Serie A Champion 2023, African Footballer of the Year", "honors": "Capocannoniere with 26 goals leading Napoli to Scudetto"},
    {"rank": 39, "name": "Alexander Isak", "country": "Sweden", "flag": "🇸🇪", "club": "Newcastle United", "pos": "Striker", "goals": 25, "assists": 4, "trophies": "Copa del Rey with Real Sociedad", "honors": "21 Premier League goals in 2023-24 season"},
    {"rank": 40, "name": "Khvicha Kvaratskhelia", "country": "Georgia", "flag": "🇬🇪", "club": "Napoli", "pos": "Left Winger", "goals": 11, "assists": 9, "trophies": "Serie A MVP 2023, EURO 2024 Round of 16 with Georgia", "honors": "Serie A Champion, Champions League Young Player 2023"},
    {"rank": 41, "name": "Rafael Leão", "country": "Portugal", "flag": "🇵🇹", "club": "AC Milan", "pos": "Left Winger", "goals": 15, "assists": 14, "trophies": "Serie A MVP 2022, Serie A Champion", "honors": "Fastest goal in Serie A history (6.2 seconds)"},
    {"rank": 42, "name": "Julián Álvarez", "country": "Argentina", "flag": "🇦🇷", "club": "Atlético Madrid", "pos": "Forward", "goals": 19, "assists": 11, "trophies": "World Cup 2022, 2x Copa América, Treble 2023", "honors": "Won World Cup & Treble in same season (age 23)"},
    {"rank": 43, "name": "Eduardo Camavinga", "country": "France", "flag": "🇫🇷", "club": "Real Madrid", "pos": "Midfielder", "goals": 2, "assists": 4, "trophies": "2x Champions League, 2x La Liga", "honors": "Won every single club trophy possible with Real Madrid by age 21"},
    {"rank": 44, "name": "Aurélien Tchouaméni", "country": "France", "flag": "🇫🇷", "club": "Real Madrid", "pos": "Defensive Midfielder", "goals": 3, "assists": 3, "trophies": "Champions League 2024, World Cup Finalist 2022", "honors": "Elite defensive duel win rate (68.9%)"},
    {"rank": 45, "name": "Pedri", "country": "Spain", "flag": "🇪🇸", "club": "FC Barcelona", "pos": "Central Midfielder", "goals": 5, "assists": 7, "trophies": "EURO 2024 Champion, Golden Boy 2021", "honors": "EURO 2020 Young Player of the Tournament, La Liga Champion"},
    {"rank": 46, "name": "Gavi", "country": "Spain", "flag": "🇪🇸", "club": "FC Barcelona", "pos": "Central Midfielder", "goals": 3, "assists": 4, "trophies": "Nations League 2023, Golden Boy 2022", "honors": "Kopa Trophy 2022, La Liga Champion"},
    {"rank": 47, "name": "Alphonso Davies", "country": "Canada", "flag": "🇨🇦", "club": "Bayern Munich", "pos": "Left-Back", "goals": 3, "assists": 6, "trophies": "5x Bundesliga, Champions League 2020", "honors": "Top sprint speed recorded: 36.51 km/h"},
    {"rank": 48, "name": "Achraf Hakimi", "country": "Morocco", "flag": "🇲🇦", "club": "Paris Saint-Germain", "pos": "Right-Back", "goals": 5, "assists": 9, "trophies": "World Cup Semi-Finalist 2022, 3x Ligue 1", "honors": "Panenka penalty to knock out Spain in World Cup 2022"},
    {"rank": 49, "name": "Mike Maignan", "country": "France", "flag": "🇫🇷", "club": "AC Milan", "pos": "Goalkeeper", "goals": 0, "assists": 1, "trophies": "Serie A Best Goalkeeper, Nations League Winner", "honors": "EURO 2024 Team of the Tournament with 4 clean sheets"},
    {"rank": 50, "name": "Toni Kroos", "country": "Germany", "flag": "🇩🇪", "club": "Legend / Real Madrid", "pos": "Central Midfielder", "goals": 1, "assists": 10, "trophies": "6x Champions League, 2014 World Cup Winner", "honors": "Retired at peak after winning 2024 Champions League with 95% passing"}
]

football_data = {
    "sport": "Football (Soccer)",
    "governing_body": "Fédération Internationale de Football Association (FIFA)",
    "headquarters": "Zürich, Switzerland",
    "founded_year": 1904,
    "history": {
        "summary": "While ancient ball-kicking games like Cuju (China, 3rd century BC) and Episkyros (Greece) existed, modern association football was codified in 1863 in London at the Freemasons' Tavern by the newly formed Football Association (FA). The global governing body FIFA was founded in 1904 in Paris. The inaugural FIFA World Cup was held in Uruguay in 1930 with 13 nations.",
        "key_eras": [
            {"era": "The Early International Era (1872–1930)", "description": "First international match between Scotland and England in 1872; Olympic football dominance; Uruguay winning 1924 and 1928 Olympic Golds."},
            {"era": "Pelé & The Golden Brazilian Era (1958–1970)", "description": "Brazil winning 3 World Cups in 12 years; tactical evolution to 4-2-4 and 4-3-3; Pelé scoring over 1,000 career goals."},
            {"era": "Total Football & European Expansion (1974–1992)", "description": "Rinus Michels and Johan Cruyff's Dutch 'Total Football'; Diego Maradona's 1986 heroics; introduction of the UEFA Champions League in 1992."},
            {"era": "The Messi-Ronaldo Duopoly & Pressing Revolution (2006–Present)", "description": "Spain's tiki-taka treble (2008-2012); Messi and Ronaldo claiming 13 Ballon d'Ors; Pep Guardiola and Jürgen Klopp's high-pressing positional play; Argentina's 2022 World Cup triumph."}
        ]
    },
    "major_tournaments": [
        {"name": "FIFA World Cup", "governing_body": "FIFA", "frequency": "Every 4 Years", "first_edition": 1930, "current_holder": "Argentina (2022)", "description": "The world's most prestigious and watched sporting event. Brazil holds a record 5 titles."},
        {"name": "UEFA Champions League", "governing_body": "UEFA", "frequency": "Annual", "first_edition": 1955, "current_holder": "Real Madrid (2024)", "description": "The pinnacle of European club football. Real Madrid has won a record 15 European Cups."},
        {"name": "UEFA European Championship (EURO)", "governing_body": "UEFA", "frequency": "Every 4 Years", "first_edition": 1960, "current_holder": "Spain (2024)", "description": "Championship of European national teams. Spain holds the record with 4 titles."},
        {"name": "Copa América", "governing_body": "CONMEBOL", "frequency": "Every 4 Years", "first_edition": 1916, "current_holder": "Argentina (2024)", "description": "The oldest continental football competition. Argentina leads with 16 titles."},
        {"name": "Premier League", "governing_body": "The FA", "frequency": "Annual", "first_edition": 1992, "current_holder": "Manchester City (2024)", "description": "The most watched and commercialized domestic league in the world."},
        {"name": "FIFA Club World Cup", "governing_body": "FIFA", "frequency": "Quadrennial (Expanded 32-team)", "first_edition": 2000, "current_holder": "Manchester City (2023)", "description": "Global competition pitting top clubs from every continental confederation."}
    ],
    "matches_2026": [
        {
            "id": "f-match-1",
            "title": "UEFA Champions League 2026/27 — Matchday 4",
            "date": "14 Nov 2026",
            "venue": "Santiago Bernabéu, Madrid",
            "status": "LIVE",
            "team1": {"name": "Real Madrid", "flag": "🇪🇸", "score": "2"},
            "team2": {"name": "Manchester City", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "score": "2"},
            "note": "LIVE 74' Second Half • Possession: 51% - 49% • Shots: 14 - 12",
            "key_performers": "Vinícius Jr 32', Jude Bellingham 58' | Erling Haaland 19', Kevin De Bruyne 66'"
        },
        {
            "id": "f-match-2",
            "title": "FIFA World Cup 2026 CONMEBOL Qualifier",
            "date": "19 Nov 2026",
            "venue": "Estádio do Maracanã, Rio de Janeiro",
            "status": "SCHEDULED",
            "team1": {"name": "Brazil", "flag": "🇧🇷", "score": "Upcoming"},
            "team2": {"name": "Argentina", "flag": "🇦🇷", "score": "Upcoming"},
            "note": "South American Superclásico • Sold-out crowd of 78,000",
            "key_performers": "Vinícius Jr, Rodrygo vs Lionel Messi, Lautaro Martínez"
        },
        {
            "id": "f-match-3",
            "title": "UEFA Champions League 2026/27 — Matchday 4",
            "date": "06 Nov 2026",
            "venue": "Camp Nou, Barcelona",
            "status": "COMPLETED",
            "team1": {"name": "FC Barcelona", "flag": "🇪🇸", "score": "3"},
            "team2": {"name": "AC Milan", "flag": "🇮🇹", "score": "1"},
            "note": "Full Time • Lamine Yamal 2 assists & 1 goal",
            "key_performers": "Lamine Yamal 21', Robert Lewandowski 49', Pedri 78' | Rafael Leão 34'"
        }
    ],
    "team_fixtures": {
        "argentina": {
            "upcoming": [
                {"opp": "vs Brazil (WC 2026 Qualifier)", "date": "19 Nov 2026", "venue": "Maracanã, Rio de Janeiro", "comp": "FIFA World Cup Qualifiers"},
                {"opp": "vs Uruguay (WC 2026 Qualifier)", "date": "24 Nov 2026", "venue": "Estadio Monumental, Buenos Aires", "comp": "FIFA World Cup Qualifiers"},
                {"opp": "vs Colombia (International Friendly)", "date": "22 Mar 2027", "venue": "Miami, USA", "comp": "International Friendly"}
            ],
            "recent": [
                {"opp": "vs Colombia (Copa América Final)", "date": "14 Jul 2024", "res": "WON", "score": "1 - 0 (AET)", "hero": "Lautaro Martínez 112'"},
                {"opp": "vs Canada (Copa América Semi)", "date": "09 Jul 2024", "res": "WON", "score": "2 - 0", "hero": "Lionel Messi 51', Julian Alvarez 22'"},
                {"opp": "vs Ecuador (Copa América QF)", "date": "04 Jul 2024", "res": "WON", "score": "1 - 1 (4-2 pens)", "hero": "Emi Martínez (2 shootout saves)"},
                {"opp": "vs Peru (Copa Group A)", "date": "29 Jun 2024", "res": "WON", "score": "2 - 0", "hero": "Lautaro Martínez (2 goals)"},
                {"opp": "vs Chile (Copa Group A)", "date": "25 Jun 2024", "res": "WON", "score": "1 - 0", "hero": "Lautaro Martínez 88'"}
            ]
        }
    },
    "top_50_players": football_top_50
}

with open(DATASETS_DIR / "football.json", "w", encoding="utf-8") as f:
    json.dump(football_data, f, indent=2, ensure_ascii=False)
print("Saved data/datasets/football.json")
# -------------------------------------------------------------
# 3. TENNIS DATASET
# -------------------------------------------------------------
tennis_top_50 = [
    {"rank": 1, "name": "Jannik Sinner", "country": "Italy", "flag": "🇮🇹", "age": 25, "plays": "Right-Handed", "titles": 18, "slams": 2, "points": 11830, "honors": "2024 Australian Open & US Open Champion, Year-End #1"},
    {"rank": 2, "name": "Alexander Zverev", "country": "Germany", "flag": "🇩🇪", "age": 29, "plays": "Right-Handed", "titles": 23, "slams": 0, "points": 7915, "honors": "Olympic Gold 2021, 2x ATP Finals Champion, 7x Masters 1000"},
    {"rank": 3, "name": "Carlos Alcaraz", "country": "Spain", "flag": "🇪🇸", "age": 23, "plays": "Right-Handed", "titles": 16, "slams": 4, "points": 7010, "honors": "4 Grand Slams on 3 surfaces (Wimbledon x2, Roland Garros, US Open)"},
    {"rank": 4, "name": "Novak Djokovic", "country": "Serbia", "flag": "🇷🇸", "age": 39, "plays": "Right-Handed", "titles": 99, "slams": 24, "points": 6210, "honors": "Career Golden Slam, 24 Grand Slams (all-time record), 428 weeks at #1"},
    {"rank": 5, "name": "Daniil Medvedev", "country": "Russia", "flag": "🇷🇺", "age": 30, "plays": "Right-Handed", "titles": 20, "slams": 1, "points": 5030, "honors": "2021 US Open Champion, 6x Grand Slam Finalist, ATP Finals Champ"},
    {"rank": 6, "name": "Taylor Fritz", "country": "United States", "flag": "🇺🇸", "age": 29, "plays": "Right-Handed", "titles": 8, "slams": 0, "points": 4300, "honors": "2024 US Open Finalist, Indian Wells Champion"},
    {"rank": 7, "name": "Andrey Rublev", "country": "Russia", "flag": "🇷🇺", "age": 29, "plays": "Right-Handed", "titles": 16, "slams": 0, "points": 4120, "honors": "2x Masters 1000 Champion (Monte-Carlo, Madrid)"},
    {"rank": 8, "name": "Casper Ruud", "country": "Norway", "flag": "🇳🇴", "age": 27, "plays": "Right-Handed", "titles": 12, "slams": 0, "points": 3855, "honors": "3x Grand Slam Finalist (Roland Garros x2, US Open)"},
    {"rank": 9, "name": "Alex de Minaur", "country": "Australia", "flag": "🇦🇺", "age": 27, "plays": "Right-Handed", "titles": 9, "slams": 0, "points": 3745, "honors": "Acapulco Champion, 3 consecutive Grand Slam quarter-finals"},
    {"rank": 10, "name": "Grigor Dimitrov", "country": "Bulgaria", "flag": "🇧🇬", "age": 35, "plays": "Right-Handed (1H)", "titles": 9, "slams": 0, "points": 3350, "honors": "ATP Finals Champion, 3x Grand Slam Semi-Finalist"},
    {"rank": 11, "name": "Stefanos Tsitsipas", "country": "Greece", "flag": "🇬🇷", "age": 28, "plays": "Right-Handed (1H)", "titles": 11, "slams": 0, "points": 3165, "honors": "3x Monte-Carlo Masters Champion, 2x Grand Slam Finalist"},
    {"rank": 12, "name": "Tommy Paul", "country": "United States", "flag": "🇺🇸", "age": 29, "plays": "Right-Handed", "titles": 3, "slams": 0, "points": 3145, "honors": "Australian Open Semi-Finalist, Queen's Club Champion"},
    {"rank": 13, "name": "Holger Rune", "country": "Denmark", "flag": "🇩🇰", "age": 23, "plays": "Right-Handed", "titles": 4, "slams": 0, "points": 3025, "honors": "Paris Masters Champion 2022 (defeated 5 top-10 players)"},
    {"rank": 14, "name": "Hubert Hurkacz", "country": "Poland", "flag": "🇵🇱", "age": 29, "plays": "Right-Handed", "titles": 8, "slams": 0, "points": 2980, "honors": "2x Masters 1000 Champion (Miami, Shanghai), Wimbledon Semi-Finalist"},
    {"rank": 15, "name": "Frances Tiafoe", "country": "United States", "flag": "🇺🇸", "age": 28, "plays": "Right-Handed", "titles": 3, "slams": 0, "points": 2685, "honors": "2x US Open Semi-Finalist, Cincinnati Masters Finalist"},
    {"rank": 16, "name": "Jack Draper", "country": "Great Britain", "flag": "🇬🇧", "age": 24, "plays": "Left-Handed", "titles": 2, "slams": 0, "points": 2540, "honors": "US Open Semi-Finalist 2024, Vienna 500 Champion"},
    {"rank": 17, "name": "Lorenzo Musetti", "country": "Italy", "flag": "🇮🇹", "age": 24, "plays": "Right-Handed (1H)", "titles": 2, "slams": 0, "points": 2480, "honors": "Olympic Bronze Medalist Paris 2024, Wimbledon Semi-Finalist"},
    {"rank": 18, "name": "Ugo Humbert", "country": "France", "flag": "🇫🇷", "age": 28, "plays": "Left-Handed", "titles": 6, "slams": 0, "points": 2435, "honors": "Dubai 500 Champion, Paris Masters Finalist"},
    {"rank": 19, "name": "Sebastian Korda", "country": "United States", "flag": "🇺🇸", "age": 26, "plays": "Right-Handed", "titles": 2, "slams": 0, "points": 2380, "honors": "Washington 500 Champion 2024, Australian Open QF"},
    {"rank": 20, "name": "Ben Shelton", "country": "United States", "flag": "🇺🇸", "age": 24, "plays": "Left-Handed", "titles": 2, "slams": 0, "points": 2340, "honors": "US Open Semi-Finalist, 149 mph serve world record holder"},
    {"rank": 21, "name": "Arthur Fils", "country": "France", "flag": "🇫🇷", "age": 22, "plays": "Right-Handed", "titles": 3, "slams": 0, "points": 2290, "honors": "Hamburg & Tokyo 500 Champion 2024, Youngest in Top 25"},
    {"rank": 22, "name": "Félix Auger-Aliassime", "country": "Canada", "flag": "🇨🇦", "age": 26, "plays": "Right-Handed", "titles": 5, "slams": 0, "points": 2200, "honors": "US Open Semi-Finalist, Olympic Bronze Mixed Doubles 2024"},
    {"rank": 23, "name": "Alejandro Tabilo", "country": "Chile", "flag": "🇨🇱", "age": 29, "plays": "Left-Handed", "titles": 2, "slams": 0, "points": 2150, "honors": "Rome Masters Semi-Finalist (defeated Djokovic in straight sets)"},
    {"rank": 24, "name": "Karen Khachanov", "country": "Russia", "flag": "🇷🇺", "age": 30, "plays": "Right-Handed", "titles": 7, "slams": 0, "points": 2080, "honors": "Paris Masters Champion, Olympic Silver Medalist, 2x Slam Semi-Finalist"},
    {"rank": 25, "name": "Alexei Popyrin", "country": "Australia", "flag": "🇦🇺", "age": 27, "plays": "Right-Handed", "titles": 3, "slams": 0, "points": 2010, "honors": "Montreal Masters 1000 Champion 2024"},
    {"rank": 26, "name": "Jordan Thompson", "country": "Australia", "flag": "🇦🇺", "age": 32, "plays": "Right-Handed", "titles": 1, "slams": 0, "points": 1950, "honors": "US Open Doubles Champion, Los Cabos Singles Champion"},
    {"rank": 27, "name": "Sebastián Báez", "country": "Argentina", "flag": "🇦🇷", "age": 25, "plays": "Right-Handed", "titles": 6, "slams": 0, "points": 1890, "honors": "Rio Open 500 Champion, Clay court specialist"},
    {"rank": 28, "name": "Jiří Lehečka", "country": "Czech Republic", "flag": "🇨🇿", "age": 25, "plays": "Right-Handed", "titles": 1, "slams": 0, "points": 1820, "honors": "Adelaide Champion, Australian Open Quarter-Finalist"},
    {"rank": 29, "name": "Francisco Cerúndolo", "country": "Argentina", "flag": "🇦🇷", "age": 28, "plays": "Right-Handed", "titles": 3, "slams": 0, "points": 1780, "honors": "Umag Champion 2024, Miami Masters Semi-Finalist"},
    {"rank": 30, "name": "Flavio Cobolli", "country": "Italy", "flag": "🇮🇹", "age": 24, "plays": "Right-Handed", "titles": 0, "slams": 0, "points": 1720, "honors": "Washington 500 Finalist 2024, Rapid rise into Top 30"},
    {"rank": 31, "name": "Tomáš Macháč", "country": "Czech Republic", "flag": "🇨🇿", "age": 26, "plays": "Right-Handed", "titles": 0, "slams": 0, "points": 1680, "honors": "Olympic Gold Mixed Doubles Paris 2024, Shanghai Masters Semi-Finalist"},
    {"rank": 32, "name": "Matteo Berrettini", "country": "Italy", "flag": "🇮🇹", "age": 30, "plays": "Right-Handed", "titles": 10, "slams": 0, "points": 1640, "honors": "Wimbledon Finalist 2021, 3 ATP titles in 2024 comeback"},
    {"rank": 33, "name": "Cameron Norrie", "country": "Great Britain", "flag": "🇬🇧", "age": 31, "plays": "Left-Handed", "titles": 5, "slams": 0, "points": 1590, "honors": "Indian Wells Masters Champion, Wimbledon Semi-Finalist"},
    {"rank": 34, "name": "Jan-Lennard Struff", "country": "Germany", "flag": "🇩🇪", "age": 36, "plays": "Right-Handed", "titles": 1, "slams": 0, "points": 1540, "honors": "Munich Champion 2024, Madrid Masters Finalist"},
    {"rank": 35, "name": "Mariano Navone", "country": "Argentina", "flag": "🇦🇷", "age": 25, "plays": "Right-Handed", "titles": 0, "slams": 0, "points": 1500, "honors": "Rio 500 & Bucharest Finalist in breakthrough 2024 season"},
    {"rank": 36, "name": "Luciano Darderi", "country": "Italy", "flag": "🇮🇹", "age": 24, "plays": "Right-Handed", "titles": 1, "slams": 0, "points": 1460, "honors": "Cordoba Open Champion 2024"},
    {"rank": 37, "name": "Nuno Borges", "country": "Portugal", "flag": "🇵🇹", "age": 29, "plays": "Right-Handed", "titles": 1, "slams": 0, "points": 1420, "honors": "Bastad Champion (defeated Nadal in final), Australian Open 4R"},
    {"rank": 38, "name": "Tallon Griekspoor", "country": "Netherlands", "flag": "🇳🇱", "age": 30, "plays": "Right-Handed", "titles": 2, "slams": 0, "points": 1390, "honors": "Rotterdam 500 Semi-Finalist, 2 ATP 250 titles"},
    {"rank": 39, "name": "Pedro Martínez", "country": "Spain", "flag": "🇪🇸", "age": 29, "plays": "Right-Handed", "titles": 1, "slams": 0, "points": 1350, "honors": "Santiago Champion, Estoril Finalist"},
    {"rank": 40, "name": "Alex Michelsen", "country": "United States", "flag": "🇺🇸", "age": 22, "plays": "Right-Handed", "titles": 0, "slams": 0, "points": 1320, "honors": "3x ATP 250 Finalist, Youngest American in Top 40"},
    {"rank": 41, "name": "Gaël Monfils", "country": "France", "flag": "🇫🇷", "age": 40, "plays": "Right-Handed", "titles": 12, "slams": 0, "points": 1280, "honors": "2x Grand Slam Semi-Finalist, 500+ career match wins"},
    {"rank": 42, "name": "Marcos Giron", "country": "United States", "flag": "🇺🇸", "age": 33, "plays": "Right-Handed", "titles": 1, "slams": 0, "points": 1250, "honors": "Newport Champion 2024, NCAA Singles Champion"},
    {"rank": 43, "name": "David Goffin", "country": "Belgium", "flag": "🇧🇪", "age": 35, "plays": "Right-Handed", "titles": 6, "slams": 0, "points": 1220, "honors": "ATP Finals Finalist, 4x Grand Slam Quarter-Finalist"},
    {"rank": 44, "name": "Miomir Kecmanović", "country": "Serbia", "flag": "🇷🇸", "age": 27, "plays": "Right-Handed", "titles": 1, "slams": 0, "points": 1190, "honors": "Kitzbuhel Champion, Australian Open 4R"},
    {"rank": 45, "name": "Lorenzo Sonego", "country": "Italy", "flag": "🇮🇹", "age": 31, "plays": "Right-Handed", "titles": 4, "slams": 0, "points": 1160, "honors": "Winston-Salem Champion 2024, Rome Masters Semi-Finalist"},
    {"rank": 46, "name": "Roberto Bautista Agut", "country": "Spain", "flag": "🇪🇸", "age": 38, "plays": "Right-Handed", "titles": 12, "slams": 0, "points": 1130, "honors": "Antwerp Champion 2024, Wimbledon Semi-Finalist"},
    {"rank": 47, "name": "Arthur Rinderknech", "country": "France", "flag": "🇫🇷", "age": 31, "plays": "Right-Handed", "titles": 0, "slams": 0, "points": 1100, "honors": "Adelaide Finalist, Montreal Masters QF"},
    {"rank": 48, "name": "Roman Safiullin", "country": "Russia", "flag": "🇷🇺", "age": 29, "plays": "Right-Handed", "titles": 0, "slams": 0, "points": 1070, "honors": "Wimbledon Quarter-Finalist, Chengdu Finalist"},
    {"rank": 49, "name": "Fabian Marozsán", "country": "Hungary", "flag": "🇭🇺", "age": 27, "plays": "Right-Handed", "titles": 0, "slams": 0, "points": 1040, "honors": "Defeated Alcaraz at Rome, 3x Masters 1000 Quarter-Finalist"},
    {"rank": 50, "name": "Kei Nishikori", "country": "Japan", "flag": "🇯🇵", "age": 36, "plays": "Right-Handed", "titles": 12, "slams": 0, "points": 1010, "honors": "2014 US Open Finalist, Olympic Bronze 2016, Former World #4"}
]

tennis_data = {
    "sport": "Tennis",
    "governing_body": "International Tennis Federation (ITF) / Association of Tennis Professionals (ATP)",
    "headquarters": "London, UK / Monte Carlo, Monaco",
    "founded_year": 1913,
    "history": {
        "summary": "Modern lawn tennis was patented and codified in 1874 by Major Walter Clopton Wingfield in Wales. The inaugural Wimbledon Championship was held in 1877 on the grass courts of the All England Croquet and Lawn Tennis Club. In 1968, the commercial 'Open Era' arrived, permitting professionals and amateurs to compete together in the four Grand Slam tournaments.",
        "key_eras": [
            {"era": "The Early Amateur & Challenge Era (1877–1967)", "description": "Rod Laver completing two calendar-year Grand Slams (1962, 1969); amateur rules barring professional stars until the historic vote in 1968."},
            {"era": "Borg, McEnroe & Connors Era (1970–1989)", "description": "Fiery rivalries, rockstar popularity, wooden rackets giving way to graphite and composite technologies."},
            {"era": "Sampras-Agassi & Serve-and-Volley Era (1990–2002)", "description": "Pete Sampras's record 14 Grand Slams; Andre Agassi's Career Golden Slam; rapid power serves and baseline defense."},
            {"era": "The Big Three & The Golden Era (2003–2023)", "description": "Roger Federer (20 slams), Rafael Nadal (22 slams), and Novak Djokovic (24 slams) winning an astonishing 66 of 80 Grand Slams over two decades."},
            {"era": "The New Generation Vanguard (2024–Present)", "description": "Jannik Sinner and Carlos Alcaraz sweeping all 4 Grand Slams in 2024, ushering in the post-Big Three supremacy."}
        ]
    },
    "major_tournaments": [
        {"name": "The Championships, Wimbledon", "surface": "Grass", "location": "London, England", "first_edition": 1877, "current_holder": "Carlos Alcaraz (2024)", "description": "Tennis's oldest and most prestigious tournament. Strict all-white dress code and traditional grass court play."},
        {"name": "Roland-Garros (French Open)", "surface": "Clay (Terre Battue)", "location": "Paris, France", "first_edition": 1891, "current_holder": "Carlos Alcaraz (2024)", "description": "The ultimate physical test of sliding and endurance. Rafael Nadal holds an untouchable 14 titles."},
        {"name": "US Open", "surface": "Hard (DecoTurf / Laykold)", "location": "New York, USA", "first_edition": 1881, "current_holder": "Jannik Sinner (2024)", "description": "The electric, night-session Grand Slam held at Arthur Ashe Stadium in Flushing Meadows."},
        {"name": "Australian Open", "surface": "Hard (GreenSet)", "location": "Melbourne, Australia", "first_edition": 1905, "current_holder": "Jannik Sinner (2024)", "description": "The 'Happy Slam' kicking off the tennis calendar each January. Novak Djokovic holds a record 10 titles."},
        {"name": "Nitto ATP Finals", "surface": "Indoor Hard", "location": "Turin, Italy", "first_edition": 1970, "current_holder": "Jannik Sinner (2024)", "description": "Year-end shootout featuring exclusively the top 8 singles players in the world."},
        {"name": "ATP Masters 1000", "surface": "Multi-Surface", "location": "9 Global Cities", "first_edition": 1990, "current_holder": "Various", "description": "The elite nine tournaments directly below the Grand Slams offering 1,000 ranking points."}
    ],
    "matches_2026": [
        {
            "id": "t-match-1",
            "title": "Nitto ATP Finals 2026 Turin — Championship Match",
            "date": "14 Nov 2026",
            "venue": "Pala Alpitour, Turin, Italy",
            "status": "LIVE",
            "team1": {"name": "Carlos Alcaraz", "flag": "🇪🇸", "score": "6, 5, 4*"},
            "team2": {"name": "Jannik Sinner", "flag": "🇮🇹", "score": "4, 7, 3"},
            "note": "LIVE Set 3 Game 8 • Sinner serving 30-40 (Break Point) • Match Time: 2h 38m",
            "key_performers": "Alcaraz: 11 aces, 34 winners | Sinner: 14 aces, 31 winners"
        },
        {
            "id": "t-match-2",
            "title": "Australian Open 2027 Men's Singles Final Preview",
            "date": "31 Jan 2027",
            "venue": "Rod Laver Arena, Melbourne",
            "status": "SCHEDULED",
            "team1": {"name": "Jannik Sinner", "flag": "🇮🇹", "score": "Upcoming"},
            "team2": {"name": "Alexander Zverev", "flag": "🇩🇪", "score": "Upcoming"},
            "note": "Defending Champion Sinner seeks 3rd Grand Slam title",
            "key_performers": "Jannik Sinner vs Alexander Zverev"
        },
        {
            "id": "t-match-3",
            "title": "Wimbledon 2026 Men's Singles Final",
            "date": "12 Jul 2026",
            "venue": "Centre Court, Wimbledon",
            "status": "COMPLETED",
            "team1": {"name": "Carlos Alcaraz", "flag": "🇪🇸", "score": "6, 6, 7 (7)"},
            "team2": {"name": "Novak Djokovic", "flag": "🇷🇸", "score": "2, 2, 6 (4)"},
            "note": "Alcaraz defends Wimbledon title in straight sets",
            "key_performers": "Carlos Alcaraz: 42 winners, 84% first-serve points won"
        }
    ],
    "top_50_players": tennis_top_50
}

with open(DATASETS_DIR / "tennis.json", "w", encoding="utf-8") as f:
    json.dump(tennis_data, f, indent=2, ensure_ascii=False)
print("Saved data/datasets/tennis.json")


# -------------------------------------------------------------
# 4. BASKETBALL DATASET
# -------------------------------------------------------------
basketball_top_50 = [
    {"rank": 1, "name": "Nikola Jokić", "country": "Serbia", "flag": "🇷🇸", "team": "Denver Nuggets", "pos": "Center", "ppg": 26.4, "rpg": 12.4, "apg": 9.0, "rings": 1, "honors": "3x NBA MVP (2021, 2022, 2024), 2023 Finals MVP, Olympic Bronze 2024"},
    {"rank": 2, "name": "Luka Dončić", "country": "Slovenia", "flag": "🇸🇮", "team": "Dallas Mavericks", "pos": "Point Guard", "ppg": 33.9, "rpg": 9.2, "apg": 9.8, "rings": 0, "honors": "2024 NBA Scoring Champion, 5x All-NBA First Team, 73-pt game"},
    {"rank": 3, "name": "Giannis Antetokounmpo", "country": "Greece", "flag": "🇬🇷", "team": "Milwaukee Bucks", "pos": "Power Forward", "ppg": 30.4, "rpg": 11.5, "apg": 6.5, "rings": 1, "honors": "2x NBA MVP, 2021 Finals MVP (50-pt Game 6), DPOY"},
    {"rank": 4, "name": "Shai Gilgeous-Alexander", "country": "Canada", "flag": "🇨🇦", "team": "Oklahoma City Thunder", "pos": "Point Guard", "ppg": 30.1, "rpg": 5.5, "apg": 6.2, "rings": 0, "honors": "2x All-NBA First Team, 2024 MVP Runner-Up, FIBA World Cup Bronze"},
    {"rank": 5, "name": "Jayson Tatum", "country": "United States", "flag": "🇺🇸", "team": "Boston Celtics", "pos": "Small Forward", "ppg": 26.9, "rpg": 8.1, "apg": 4.9, "rings": 1, "honors": "2024 NBA Champion, 3x All-NBA First Team, 2x Olympic Gold"},
    {"rank": 6, "name": "Stephen Curry", "country": "United States", "flag": "🇺🇸", "team": "Golden State Warriors", "pos": "Point Guard", "ppg": 26.4, "rpg": 4.5, "apg": 5.1, "rings": 4, "honors": "All-time 3-point leader (3,700+ 3PM), 2x MVP (unanimous), 2022 Finals MVP, Paris 2024 Gold"},
    {"rank": 7, "name": "Anthony Edwards", "country": "United States", "flag": "🇺🇸", "team": "Minnesota Timberwolves", "pos": "Shooting Guard", "ppg": 25.9, "rpg": 5.4, "apg": 5.1, "rings": 0, "honors": "All-NBA Second Team 2024, Olympic Gold Paris 2024"},
    {"rank": 8, "name": "Joel Embiid", "country": "United States", "flag": "🇺🇸", "team": "Philadelphia 76ers", "pos": "Center", "ppg": 34.7, "rpg": 11.0, "apg": 5.6, "rings": 0, "honors": "2023 NBA MVP, 2x Scoring Champion, 70-point game"},
    {"rank": 9, "name": "Victor Wembanyama", "country": "France", "flag": "🇫🇷", "team": "San Antonio Spurs", "pos": "Center", "ppg": 21.4, "rpg": 10.6, "apg": 3.9, "rings": 0, "honors": "Unanimous Rookie of the Year 2024, NBA Blocks Leader (3.6 BPG), Olympic Silver"},
    {"rank": 10, "name": "Kevin Durant", "country": "United States", "flag": "🇺🇸", "team": "Phoenix Suns", "pos": "Forward", "ppg": 27.1, "rpg": 6.6, "apg": 5.0, "rings": 2, "honors": "4x Olympic Gold Medalist (USA all-time leading scorer), 2x Finals MVP, 2014 MVP"},
    {"rank": 11, "name": "LeBron James", "country": "United States", "flag": "🇺🇸", "team": "Los Angeles Lakers", "pos": "Forward", "ppg": 25.7, "rpg": 7.3, "apg": 8.3, "rings": 4, "honors": "NBA All-time leading scorer (40,000+ points), 4x MVP, 4x Finals MVP, Olympic MVP 2024"},
    {"rank": 12, "name": "Jalen Brunson", "country": "United States", "flag": "🇺🇸", "team": "New York Knicks", "pos": "Point Guard", "ppg": 28.7, "rpg": 3.6, "apg": 6.7, "rings": 0, "honors": "All-NBA Second Team 2024, 5 consecutive 40-pt playoff games"},
    {"rank": 13, "name": "Donovan Mitchell", "country": "United States", "flag": "🇺🇸", "team": "Cleveland Cavaliers", "pos": "Shooting Guard", "ppg": 26.6, "rpg": 5.1, "apg": 6.1, "rings": 0, "honors": "5x All-Star, 71-point game in 2023"},
    {"rank": 14, "name": "Anthony Davis", "country": "United States", "flag": "🇺🇸", "team": "Los Angeles Lakers", "pos": "Center / Power Forward", "ppg": 24.7, "rpg": 12.6, "apg": 3.5, "rings": 1, "honors": "2020 NBA Champion, 2x Olympic Gold, All-Defensive First Team"},
    {"rank": 15, "name": "Devin Booker", "country": "United States", "flag": "🇺🇸", "team": "Phoenix Suns", "pos": "Shooting Guard", "ppg": 27.1, "rpg": 4.5, "apg": 6.9, "rings": 0, "honors": "2x Olympic Gold, 70-point game, All-NBA First Team"},
    {"rank": 16, "name": "Jaylen Brown", "country": "United States", "flag": "🇺🇸", "team": "Boston Celtics", "pos": "Shooting Guard / Forward", "ppg": 23.0, "rpg": 5.5, "apg": 3.6, "rings": 1, "honors": "2024 NBA Finals MVP & Eastern Conference Finals MVP"},
    {"rank": 17, "name": "Tyrese Haliburton", "country": "United States", "flag": "🇺🇸", "team": "Indiana Pacers", "pos": "Point Guard", "ppg": 20.1, "rpg": 3.9, "apg": 10.9, "rings": 0, "honors": "2024 NBA Assists Leader, All-NBA Third Team, Olympic Gold"},
    {"rank": 18, "name": "Bam Adebayo", "country": "United States", "flag": "🇺🇸", "team": "Miami Heat", "pos": "Center", "ppg": 19.3, "rpg": 10.4, "apg": 3.9, "rings": 0, "honors": "5x All-Defensive Team, 2x Olympic Gold, 2x NBA Finals"},
    {"rank": 19, "name": "Domantas Sabonis", "country": "Lithuania", "flag": "🇱🇹", "team": "Sacramento Kings", "pos": "Center / Power Forward", "ppg": 19.4, "rpg": 13.7, "apg": 8.2, "rings": 0, "honors": "2x Rebounding Leader, 61 consecutive double-doubles (modern record)"},
    {"rank": 20, "name": "De'Aaron Fox", "country": "United States", "flag": "🇺🇸", "team": "Sacramento Kings", "pos": "Point Guard", "ppg": 26.6, "rpg": 4.6, "apg": 5.6, "rings": 0, "honors": "Inaugural Clutch Player of the Year 2023, 60-point game in 2024"},
    {"rank": 21, "name": "Kawhi Leonard", "country": "United States", "flag": "🇺🇸", "team": "LA Clippers", "pos": "Small Forward", "ppg": 23.7, "rpg": 6.1, "apg": 3.6, "rings": 2, "honors": "2x NBA Champion & Finals MVP (Spurs 2014, Raptors 2019), 2x DPOY"},
    {"rank": 22, "name": "Paul George", "country": "United States", "flag": "🇺🇸", "team": "Philadelphia 76ers", "pos": "Forward", "ppg": 22.6, "rpg": 5.2, "apg": 3.5, "rings": 0, "honors": "9x All-Star, 6x All-NBA, Olympic Gold 2016"},
    {"rank": 23, "name": "Jimmy Butler", "country": "United States", "flag": "🇺🇸", "team": "Miami Heat", "pos": "Small Forward", "ppg": 20.8, "rpg": 5.3, "apg": 5.0, "rings": 0, "honors": "2x NBA Finals Leader, Eastern Conference Finals MVP 2023"},
    {"rank": 24, "name": "Damian Lillard", "country": "United States", "flag": "🇺🇸", "team": "Milwaukee Bucks", "pos": "Point Guard", "ppg": 24.3, "rpg": 4.4, "apg": 7.0, "rings": 0, "honors": "NBA 75th Anniversary Team, 8x All-Star, 2x 3-Point Contest Champ"},
    {"rank": 25, "name": "Kyrie Irving", "country": "United States", "flag": "🇺🇸", "team": "Dallas Mavericks", "pos": "Point Guard", "ppg": 25.6, "rpg": 5.0, "apg": 5.2, "rings": 1, "honors": "2016 NBA Champion (Game 7 game-winning 3), 8x All-Star, 50-40-90 club"},
    {"rank": 26, "name": "Paolo Banchero", "country": "United States", "flag": "🇺🇸", "team": "Orlando Magic", "pos": "Power Forward", "ppg": 22.6, "rpg": 6.9, "apg": 5.4, "rings": 0, "honors": "Rookie of the Year 2023, All-Star 2024, 50-pt game 2024"},
    {"rank": 27, "name": "Chet Holmgren", "country": "United States", "flag": "🇺🇸", "team": "Oklahoma City Thunder", "pos": "Center / Forward", "ppg": 16.5, "rpg": 7.9, "apg": 2.4, "rings": 0, "honors": "2.3 BPG, 79 3PM as rookie center, All-Rookie First Team"},
    {"rank": 28, "name": "Tyrese Maxey", "country": "United States", "flag": "🇺🇸", "team": "Philadelphia 76ers", "pos": "Guard", "ppg": 25.9, "rpg": 3.7, "apg": 6.2, "rings": 0, "honors": "Most Improved Player 2024, All-Star, 3x 50-pt games in 2024"},
    {"rank": 29, "name": "Zion Williamson", "country": "United States", "flag": "🇺🇸", "team": "New Orleans Pelicans", "pos": "Power Forward", "ppg": 22.9, "rpg": 5.8, "apg": 5.0, "rings": 0, "honors": "2x All-Star, 58.7% career field goal percentage"},
    {"rank": 30, "name": "Lauri Markkanen", "country": "Finland", "flag": "🇫🇮", "team": "Utah Jazz", "pos": "Forward", "ppg": 23.2, "rpg": 8.2, "apg": 2.0, "rings": 0, "honors": "Most Improved Player 2023, All-Star, 39.9% career 3PT"},
    {"rank": 31, "name": "Karl-Anthony Towns", "country": "Dominican Republic", "flag": "🇩🇴", "team": "New York Knicks", "pos": "Center", "ppg": 21.8, "rpg": 8.3, "apg": 3.0, "rings": 0, "honors": "4x All-Star, 2x All-NBA, 3-Point Contest Champion (62-pt game)"},
    {"rank": 32, "name": "Trae Young", "country": "United States", "flag": "🇺🇸", "team": "Atlanta Hawks", "pos": "Point Guard", "ppg": 25.7, "rpg": 2.8, "apg": 10.8, "rings": 0, "honors": "3x All-Star, led league in total points & assists in same season"},
    {"rank": 33, "name": "Jamal Murray", "country": "Canada", "flag": "🇨🇦", "team": "Denver Nuggets", "pos": "Point Guard", "ppg": 21.2, "rpg": 4.1, "apg": 6.5, "rings": 1, "honors": "2023 NBA Champion, 2x Playoff Buzzer-Beater Game Winners vs Lakers (2024)"},
    {"rank": 34, "name": "Rudy Gobert", "country": "France", "flag": "🇫🇷", "team": "Minnesota Timberwolves", "pos": "Center", "ppg": 14.0, "rpg": 12.9, "apg": 1.3, "rings": 0, "honors": "4x NBA Defensive Player of the Year (tied all-time record), 2x Olympic Silver"},
    {"rank": 35, "name": "Alperen Şengün", "country": "Turkey", "flag": "🇹🇷", "team": "Houston Rockets", "pos": "Center", "ppg": 21.1, "rpg": 9.3, "apg": 5.0, "rings": 0, "honors": "Most points by a Turkish player in NBA history (45 vs Spurs)"},
    {"rank": 36, "name": "Pascal Siakam", "country": "Cameroon", "flag": "🇨🇲", "team": "Indiana Pacers", "pos": "Power Forward", "ppg": 21.7, "rpg": 7.1, "apg": 4.3, "rings": 1, "honors": "2019 NBA Champion, 2x All-NBA, 2019 Most Improved Player"},
    {"rank": 37, "name": "Scottie Barnes", "country": "United States", "flag": "🇺🇸", "team": "Toronto Raptors", "pos": "Forward", "ppg": 19.9, "rpg": 8.2, "apg": 6.1, "rings": 0, "honors": "Rookie of the Year 2022, All-Star 2024"},
    {"rank": 38, "name": "Derrick White", "country": "United States", "flag": "🇺🇸", "team": "Boston Celtics", "pos": "Guard", "ppg": 15.2, "rpg": 4.2, "apg": 5.2, "rings": 1, "honors": "2024 NBA Champion, Olympic Gold Paris 2024, 2x All-Defensive Team"},
    {"rank": 39, "name": "Jrue Holiday", "country": "United States", "flag": "🇺🇸", "team": "Boston Celtics", "pos": "Guard", "ppg": 12.5, "rpg": 5.4, "apg": 4.8, "rings": 2, "honors": "2x NBA Champion (Bucks 2021, Celtics 2024), 2x Olympic Gold, 6x All-Defense"},
    {"rank": 40, "name": "Mikal Bridges", "country": "United States", "flag": "🇺🇸", "team": "New York Knicks", "pos": "Wing", "ppg": 19.6, "rpg": 4.5, "apg": 3.6, "rings": 0, "honors": "NBA Iron Man (474+ consecutive games played), All-Defensive First Team"},
    {"rank": 41, "name": "Jalen Williams", "country": "United States", "flag": "🇺🇸", "team": "Oklahoma City Thunder", "pos": "Forward / Guard", "ppg": 19.1, "rpg": 4.0, "apg": 4.5, "rings": 0, "honors": "All-Rookie First Team 2023, 54.0% FG efficiency as sophomore"},
    {"rank": 42, "name": "Franz Wagner", "country": "Germany", "flag": "🇩🇪", "team": "Orlando Magic", "pos": "Forward", "ppg": 19.7, "rpg": 5.3, "apg": 3.7, "rings": 0, "honors": "FIBA World Champion 2023 with Germany, Olympic Semi-Finalist 2024"},
    {"rank": 43, "name": "Kristaps Porziņģis", "country": "Latvia", "flag": "🇱🇻", "team": "Boston Celtics", "pos": "Center", "ppg": 20.1, "rpg": 7.2, "apg": 2.0, "rings": 1, "honors": "2024 NBA Champion, 1.9 BPG, 37.5% 3PT"},
    {"rank": 44, "name": "Brandon Ingram", "country": "United States", "flag": "🇺🇸", "team": "New Orleans Pelicans", "pos": "Small Forward", "ppg": 20.8, "rpg": 5.1, "apg": 5.7, "rings": 0, "honors": "All-Star, Most Improved Player 2020"},
    {"rank": 45, "name": "Dejounte Murray", "country": "United States", "flag": "🇺🇸", "team": "New Orleans Pelicans", "pos": "Point Guard", "ppg": 22.5, "rpg": 5.3, "apg": 6.4, "rings": 0, "honors": "All-Star, 2022 NBA Steals Leader, 44-pt game with OT game-winner"},
    {"rank": 46, "name": "Desmond Bane", "country": "United States", "flag": "🇺🇸", "team": "Memphis Grizzlies", "pos": "Shooting Guard", "ppg": 23.7, "rpg": 4.4, "apg": 5.5, "rings": 0, "honors": "41.5% career 3PT shooter on high volume"},
    {"rank": 47, "name": "Jaren Jackson Jr.", "country": "United States", "flag": "🇺🇸", "team": "Memphis Grizzlies", "pos": "Power Forward / Center", "ppg": 22.5, "rpg": 5.5, "apg": 2.3, "rings": 0, "honors": "2023 NBA Defensive Player of the Year, 2x Blocks Leader"},
    {"rank": 48, "name": "Austin Reaves", "country": "United States", "flag": "🇺🇸", "team": "Los Angeles Lakers", "pos": "Guard", "ppg": 15.9, "rpg": 4.3, "apg": 5.5, "rings": 0, "honors": "FIBA World Cup 2023 USA squad, 2023 In-Season Tournament Champion"},
    {"rank": 49, "name": "Dennis Schröder", "country": "Germany", "flag": "🇩🇪", "team": "Brooklyn Nets", "pos": "Point Guard", "ppg": 14.0, "rpg": 3.0, "apg": 6.1, "rings": 0, "honors": "2023 FIBA World Cup MVP, World Champion with Germany, Olympic Semi-Finalist"},
    {"rank": 50, "name": "Bogdan Bogdanović", "country": "Serbia", "flag": "🇷🇸", "team": "Atlanta Hawks", "pos": "Shooting Guard", "ppg": 16.9, "rpg": 3.4, "apg": 3.1, "rings": 0, "honors": "Olympic Bronze Medalist 2024, FIBA All-Tournament Team 2019 & 2023"}
]

basketball_data = {
    "sport": "Basketball",
    "governing_body": "Fédération Internationale de Basketball (FIBA) / National Basketball Association (NBA)",
    "headquarters": "Mies, Switzerland / New York, USA",
    "founded_year": 1891,
    "history": {
        "summary": "Basketball was invented in December 1891 by Canadian physical education instructor Dr. James Naismith in Springfield, Massachusetts, as an indoor game to keep athletes conditioned during harsh New England winters. Naismith nailed two peach baskets to the gymnasium balcony railings at a height of 10 feet (3.05 m), establishing the enduring basket height. FIBA was established in Geneva in 1932, and the BAA (which merged into the NBA) was founded in 1946.",
        "key_eras": [
            {"era": "The Naismith & Early Pro Era (1891–1956)", "description": "Peach baskets replaced by metal hoops and backboards; George Mikan dominating as the game's first dominant giant; introduction of the 24-second shot clock in 1954 saving the league from slow stalling tactics."},
            {"era": "Russell, Wilt & Dynasty Dominance (1957–1979)", "description": "Bill Russell leading the Boston Celtics to 11 championships in 13 seasons; Wilt Chamberlain scoring 100 points in a single game (1962); ABA-NBA merger in 1976 bringing Julius Erving and the 3-point line."},
            {"era": "Magic, Bird & The Jordan Global Boom (1980–1998)", "description": "Lakers Showtime vs Celtics grit revitalizing basketball; Michael Jordan's 6 championships with the Chicago Bulls; the 1992 USA Olympic 'Dream Team' sparking international fascination."},
            {"era": "Kobe, Duncan & The Modern Spacing Revolution (1999–Present)", "description": "Kobe Bryant and Tim Duncan sharing 10 titles; LeBron James reaching 10 NBA Finals and breaking the all-time scoring record; Stephen Curry revolutionizing offensive spacing with the 3-point explosion; European MVPs (Giannis, Jokić, Dončić) taking global center stage."}
        ]
    },
    "major_tournaments": [
        {"name": "NBA Finals", "governing_body": "National Basketball Association", "frequency": "Annual", "first_edition": 1947, "current_holder": "Boston Celtics (2024)", "description": "The best-of-seven championship series of the premier basketball league on Earth. Boston Celtics hold a record 18 championships."},
        {"name": "FIBA Basketball World Cup", "governing_body": "FIBA", "frequency": "Every 4 Years", "first_edition": 1950, "current_holder": "Germany (2023)", "description": "The flagship national team competition. Germany won their historic first world title in 2023 with an undefeated 8-0 run."},
        {"name": "Olympic Men's Basketball Tournament", "governing_body": "IOC / FIBA", "frequency": "Every 4 Years", "first_edition": 1936, "current_holder": "United States (2024)", "description": "The most watched national team tournament. USA has captured 17 of 21 gold medals in history."},
        {"name": "EuroLeague", "governing_body": "Euroleague Basketball", "frequency": "Annual", "first_edition": 1958, "current_holder": "Panathinaikos (2024)", "description": "The top-tier club competition in European basketball culminating in the high-stakes Final Four."},
        {"name": "NBA Cup (In-Season Tournament)", "governing_body": "NBA", "frequency": "Annual", "first_edition": 2023, "current_holder": "Los Angeles Lakers (2023)", "description": "Mid-season cup competition featuring pool play and single-elimination knockouts in Las Vegas."}
    ],
    "matches_2026": [
        {
            "id": "b-match-1",
            "title": "NBA 2026-27 Regular Season / In-Season Cup",
            "date": "14 Nov 2026",
            "venue": "TD Garden, Boston, MA",
            "status": "LIVE",
            "team1": {"name": "Boston Celtics", "flag": "🇺🇸", "score": "98"},
            "team2": {"name": "Golden State Warriors", "flag": "🇺🇸", "score": "94"},
            "note": "LIVE Q4 3:12 • Celtics +4 • Timeouts: BOS 2, GSW 1",
            "key_performers": "Jayson Tatum 31 pts, 8 reb | Stephen Curry 34 pts (7 3PM), 6 ast"
        },
        {
            "id": "b-match-2",
            "title": "NBA 2026-27 Western Conference Clash",
            "date": "17 Nov 2026",
            "venue": "Ball Arena, Denver, CO",
            "status": "SCHEDULED",
            "team1": {"name": "Denver Nuggets", "flag": "🇺🇸", "score": "Upcoming"},
            "team2": {"name": "Dallas Mavericks", "flag": "🇺🇸", "score": "Upcoming"},
            "note": "Nikola Jokić vs Luka Dončić • Western Conference heavyweight match",
            "key_performers": "Nikola Jokić vs Luka Dončić"
        },
        {
            "id": "b-match-3",
            "title": "NBA 2026-27 Regular Season",
            "date": "09 Nov 2026",
            "venue": "Paycom Center, Oklahoma City",
            "status": "COMPLETED",
            "team1": {"name": "Oklahoma City Thunder", "flag": "🇺🇸", "score": "118"},
            "team2": {"name": "LA Clippers", "flag": "🇺🇸", "score": "112"},
            "note": "Final • Shai Gilgeous-Alexander 37 pts, 8 ast",
            "key_performers": "SGA 37 pts, Jalen Williams 24 pts | James Harden 28 pts"
        }
    ],
    "team_fixtures": {
        "germany": {
            "upcoming": [
                {"opp": "vs France (EuroBasket Qualifier)", "date": "21 Nov 2026", "venue": "Berlin Arena", "comp": "FIBA EuroBasket 2025/26"},
                {"opp": "vs Sweden (EuroBasket Qualifier)", "date": "24 Nov 2026", "venue": "Stockholm", "comp": "FIBA EuroBasket 2025/26"},
                {"opp": "vs United States (Exhibition)", "date": "15 Jul 2027", "venue": "Munich", "comp": "International Showcase"}
            ],
            "recent": [
                {"opp": "vs Serbia (FIBA World Cup Final)", "date": "10 Sep 2023", "res": "WON", "score": "83 - 77", "hero": "Dennis Schröder 28 pts (Tournament MVP)"},
                {"opp": "vs USA (FIBA World Cup Semi)", "date": "08 Sep 2023", "res": "WON", "score": "113 - 111", "hero": "Andreas Obst 24 pts, Franz Wagner 22 pts"},
                {"opp": "vs Latvia (FIBA QF)", "date": "06 Sep 2023", "res": "WON", "score": "81 - 79", "hero": "Franz Wagner 16 pts, 8 reb"},
                {"opp": "vs Slovenia (FIBA Round 2)", "date": "03 Sep 2023", "res": "WON", "score": "100 - 71", "hero": "Dennis Schröder 24 pts, 10 ast"},
                {"opp": "vs Australia (FIBA Group E)", "date": "27 Aug 2023", "res": "WON", "score": "85 - 82", "hero": "Dennis Schröder 30 pts, 8 ast"}
            ]
        }
    },
    "top_50_players": basketball_top_50
}

with open(DATASETS_DIR / "basketball.json", "w", encoding="utf-8") as f:
    json.dump(basketball_data, f, indent=2, ensure_ascii=False)
print("Saved data/datasets/basketball.json")
