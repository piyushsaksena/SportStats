# SportStats — Official Data Sources Registry

> Provenance record and terms of service documentation for official international sports data sources (Research Report Table 3 and Master Prompt Part 8).

---

## 1. Principles of Source Governance
1. **Zero Fabricated Data**: Every record ingested into SportStats traces to an immutable `source_id` provenance envelope containing the issuing organisation, official URL, retrieved-at timestamp, and licensing terms.
2. **Official Federations First**: Data is collected directly from international governing bodies (ICC, FIFA, BWF, FIBA, ITF/Grand Slam, IKF, IOC).
3. **Immutability of Raw Ingestion**: Original raw files are stored with sha256 checksums and JSON sidecars in `data/raw/`.

---

## 2. Primary Official Sources by Sport

| Sport | Governing Body / Organisation | Official Base URL | Access Method | Update Cadence | Tier | Verification Status | Notes |
|---|---|---|---|---|---|---|---|
| **Cricket** | International Cricket Council (ICC) | `https://www.icc-cricket.com` | Curated CSV / Official Portal | Post-Tournament | `official` | Verified | Men's and Women's World Cups, T20 World Cups, Champions Trophy, official team & player rankings. |
| **Football** | Fédération Internationale de Football Association (FIFA) | `https://www.fifa.com` | Curated CSV / Match Center | Post-Tournament | `official` | Verified | FIFA World Cup, FIFA Women's World Cup, official FIFA/Coca-Cola World Rankings. |
| **Badminton** | Badminton World Federation (BWF) | `https://bwfbadminton.com` | Official Results Center / CSV | Post-Tournament | `official` | Verified | BWF World Championships, Thomas & Uber Cup, BWF World Rankings. |
| **Basketball** | International Basketball Federation (FIBA) | `https://www.fiba.basketball` | Official Tournament Center / CSV | Post-Tournament | `official` | Verified | FIBA Basketball World Cup, FIBA World Rankings presented by Nike. |
| **Tennis** | All England Lawn Tennis Club (AELTC) / Grand Slam | `https://www.wimbledon.com` | Official Tournament Portal / Draws | Post-Tournament | `official` | Verified | The Championships Wimbledon tournament draws, match events, and historical championship records. |
| **Tennis** | Association of Tennis Professionals (ATP) | `https://www.atptour.com` | Official Rankings Portal | Weekly | `official` | Verified | Official ATP Singles and Doubles Rankings snapshots. |
| **Kabaddi** | International Kabaddi Federation (IKF) | `https://www.worldkabaddi.org` | Official Tournament Archives / CSV | Post-Tournament | `official` | Verified | Standard-style Kabaddi World Cup editions (2004, 2007, 2016). |
| **Olympic Sports** | International Olympic Committee (IOC) | `https://olympics.com` | Official Olympic Results API & Portal | Quadrennial | `official` | Verified | Summer Olympic Games medal tables, discipline results, World & Olympic records. |

---

## 3. Wave 1 Ingestion Audit & Coverage Report

Wave 1 provides the vertical slice across all 7 sports, covering 2 completed editions per sport:

| Sport | Competition | Editions Loaded | Matches Loaded | Top Performers / Stats | Rankings Snapshots | Olympic Events | Provenance Status |
|---|---|---|---|---|---|---|---|
| **Cricket** | Cricket World Cup | 2019, 2023 | 4 | Runs, Wickets (Kohli, Rohit, Shami, Zampa) | ICC Men's ODI Team Rankings (Top 3) | N/A | ✅ 100% Sourced |
| **Football** | FIFA World Cup | 2018, 2022 | 3 | Goals, Assists (Mbappe, Messi) | FIFA Men's World Ranking (Top 3) | N/A | ✅ 100% Sourced |
| **Tennis** | The Championships, Wimbledon | 2022, 2023 | 2 | Matches Won (Alcaraz, Djokovic) | ATP Singles Rankings (Top 2) | N/A | ✅ 100% Sourced |
| **Badminton** | BWF World Championships | 2022, 2023 | 2 | Matches Won, Titles (Axelsen, Vitidsarn) | BWF Tournament Snapshots | N/A | ✅ 100% Sourced |
| **Basketball** | FIBA Basketball World Cup | 2019, 2023 | 2 | Points (Schroder, Bogdanovic) | FIBA Tournament Snapshots | N/A | ✅ 100% Sourced |
| **Kabaddi** | Kabaddi World Cup | 2007, 2016 | 1 | Raid Points (Narwal, Thakur) | IKF Tournament Snapshots | N/A | ✅ 100% Sourced |
| **Olympic** | Summer Olympic Games | Tokyo 2020, Paris 2024 | N/A | Event Results (Jacobs, Chopra, Lyles, Pan) | Official Medal Table Leaders | 9 Medal Events | ✅ 100% Sourced |

- **Total Tournament Editions**: 14
- **Total Matches Recorded**: 14
- **Total Performance Statistics**: 13
- **Total Ranking Snapshots & Entries**: 3 snapshots, 8 entries
- **Total Olympic Medal Results**: 9 events
- **Rejection Rate**: **0.00%** (all rows strictly conform to validation rules and carry official source URLs)

