# SportStats Methodology & Statistical Specifications

This document formally defines the mathematical formulas, zero-division behaviors, comparison guardrails, provenance hierarchies, and analytical limitations governing **SportStats**, based on *Tables 4, 5, and 6* of the research report.

---

## 1. Table 4 Statistical Formulas

Every metric in SportStats is implemented deterministically in `backend/src/sportstats/metrics/formulas.py` and validated with hypothesis property-based tests.

### 1.1 Cricket Formulas

#### Batting Average
Measures a batsman's scoring efficiency per dismissal:
$$\text{Batting Average} = \frac{\text{Total Runs}}{\text{Innings} - \text{Not Outs}}$$

- **Zero-Division Handling:** If dismissals $(\text{Innings} - \text{Not Outs}) = 0$, returns $\text{Total Runs}$ if $\text{Total Runs} > 0$, else returns $0.0$.

#### Batting Strike Rate
Measures runs scored per 100 balls faced:
$$\text{Batting Strike Rate} = \left(\frac{\text{Runs}}{\text{Balls Faced}}\right) \times 100$$

- **Zero-Division Handling:** If $\text{Balls Faced} = 0$, returns $0.0$.

#### Bowling Average
Measures runs conceded per wicket taken:
$$\text{Bowling Average} = \frac{\text{Runs Conceded}}{\text{Wickets Taken}}$$

- **Zero-Division Handling:** If $\text{Wickets Taken} = 0$, returns `None` (uncomputable average; infinite runs per wicket).

#### Bowling Economy Rate
Measures runs conceded per 6-ball over bowled:
$$\text{Economy Rate} = \frac{\text{Runs Conceded}}{\frac{\text{Legal Balls Bowled}}{6}}$$

- **Zero-Division Handling:** If $\text{Legal Balls Bowled} = 0$, returns $0.0$.

#### Net Run Rate (NRR)
Measures the difference between a team's scoring rate and conceding rate across an edition:
$$\text{NRR} = \left(\frac{\sum \text{Runs Scored}}{\sum \text{Overs Faced}}\right) - \left(\frac{\sum \text{Runs Conceded}}{\sum \text{Overs Bowled}}\right)$$

- **All-Out Quota Rule:** If a team is dismissed (all out) before completing its scheduled overs (e.g. 50 overs in ODI, 20 overs in T20), the overs divisor is set to the full scheduled allocation (e.g. 50.0).

---

### 1.2 Football Formulas

#### Goal Ratio
$$\text{Goal Ratio} = \frac{\text{Goals Scored}}{\text{Matches Played}}$$

#### Expected Goals (xG) Difference
$$\text{xG Difference} = \text{Actual Goals} - \text{Expected Goals (xG)}$$

#### Save Percentage
$$\text{Save \%} = \left(\frac{\text{Saves}}{\text{Saves} + \text{Goals Conceded}}\right) \times 100$$

---

### 1.3 Basketball Formulas

#### True Shooting Percentage (TS%)
Measures total shooting efficiency incorporating 2-point, 3-point, and free-throw attempts:
$$\text{TS\%} = \frac{\text{Points}}{2 \times (\text{FGA} + 0.44 \times \text{FTA})} \times 100$$

- **Zero-Division Handling:** If $(\text{FGA} + 0.44 \times \text{FTA}) = 0$, returns $0.0$.

#### Effective Field Goal Percentage (eFG%)
$$\text{eFG\%} = \left(\frac{\text{FGM} + 0.5 \times \text{3PM}}{\text{FGA}}\right) \times 100$$

#### Assist-to-Turnover Ratio
$$\text{AST/TO} = \frac{\text{Assists}}{\text{Turnovers}}$$
- If $\text{Turnovers} = 0$, returns $\text{Assists}$ if $\text{Assists} > 0$, else $0.0$.

---

### 1.4 Tennis Formulas

#### Hold Percentage
$$\text{Hold \%} = \left(\frac{\text{Service Games Won}}{\text{Total Service Games}}\right) \times 100$$

#### Break Point Conversion
$$\text{BP Conversion \%} = \left(\frac{\text{Break Points Won}}{\text{Break Point Opportunities}}\right) \times 100$$

---

### 1.5 Badminton Formulas

#### Smash Efficiency
$$\text{Smash Efficiency \%} = \left(\frac{\text{Smash Winners}}{\text{Total Smashes}}\right) \times 100$$

#### Net Point Conversion
$$\text{Net Point \%} = \left(\frac{\text{Net Points Won}}{\text{Net Approaches}}\right) \times 100$$

---

### 1.6 Kabaddi Formulas

#### Tackle Success Rate
$$\text{Tackle Success \%} = \left(\frac{\text{Successful Tackles}}{\text{Total Tackle Attempts}}\right) \times 100$$

#### Raid Point Average
$$\text{Raid Point Avg} = \frac{\text{Total Raid Points}}{\text{Matches Played}}$$

---

## 2. Table 5 Cross-Sport Comparison Guard

A fundamental design requirement of SportStats is the **Cross-Sport Comparison Guard**:

> **Rule:** The analytical engine and REST API strictly reject direct comparison of raw sport-specific metrics (e.g. comparing cricket runs to football goals, or tennis aces to kabaddi tackle points). Any such request responds with HTTP 400 Bad Request and suggestions for valid normalized dimensions.

### Allowed Normalized Dimensions

1. **Match Win Percentage:**
   $$\text{Win \%} = \left(\frac{\text{Wins} + 0.5 \times \text{Ties}}{\text{Matches Played}}\right) \times 100$$
2. **Standardized Performance Z-Score:**
   $$z = \frac{x - \mu}{\sigma}$$
   Where $x$ is the athlete's output, $\mu$ is the tournament population mean, and $\sigma$ is the standard deviation.
3. **Within-Discipline Percentile Rank:**
   $$P = \left(\frac{\text{Rank} - 0.5}{N}\right) \times 100$$

---

## 3. Table 6 Limitations & Guardrails

| Limitation | Impact | Architectural Guardrail |
| :--- | :--- | :--- |
| **Historical Data Sparsity** | Pre-1990 tournaments lack granular match stats | Strict audit logging; missing data recorded as null; zero extrapolation |
| **Small-Sample Variance** | Small tournament samples ($N < 5$ matches) produce volatile metrics | Mandatory visual warning badge in UI and API `meta.warnings` |
| **Rule & Format Shifts** | Format changes (e.g., cricket powerplays, football VAR) alter baseline rates | Format change annotations overlaid on regression trendlines |
| **Cross-Sport Incomparability** | Different physical domains lack shared dimensional units | Hard refusal on raw metric comparisons |

---

## 4. Provenance Hierarchy & Quarantine Invariants

1. **Tier 1 Federation Authority:** All official records originate from primary governing bodies (ICC, FIFA, BWF, FIBA, ITF, IOC).
2. **Mandatory Auditing:** Every row in `performance_stat`, `match`, and `tournament_edition` must have an audited `source_id`.
3. **Quarantine Invariant:** Synthetic or benchmark data is marked `is_sample = true` and quarantined from production analytics.

