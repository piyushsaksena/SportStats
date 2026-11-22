"""Data Dictionary Generator for SportStats.

Inspects SQLAlchemy Base.metadata and views to generate a complete markdown
data dictionary in docs/DATA_DICTIONARY.md.
"""

from pathlib import Path

from sportstats.db.models import Base
from sportstats.metrics.catalog import (
    METRICS_CATALOGUE,
    get_catalogue_counts_by_sport,
)

# Root docs directory
OUTPUT_FILE = Path(__file__).resolve().parents[4] / "docs" / "DATA_DICTIONARY.md"

TABLE_DESCRIPTIONS = {
    "sport": "Reference catalog of tracked sports disciplines.",
    "discipline": "Sub-disciplines (e.g. Athletics, Swimming under Olympic Sports).",
    "country": "ISO3 country reference registry.",
    "venue": "Host stadiums and arenas.",
    "source": "Official and secondary data sources documenting complete data provenance.",
    "tournament": "High-level recurring tournaments and championships.",
    "tournament_edition": "Specific editions of tournaments with dates, host venues, and winners (Table 2).",
    "participant": "Universal participant entity representing teams, players, and athletes.",
    "player_profile": "Individual player profile details (birth date, position, gender).",
    "team_profile": "Team profile details (national, franchise, club).",
    "team_membership": "Player-to-team rosters per edition or season.",
    "edition_participant": "Participants enrolled in a tournament edition with seeds and final positions.",
    "stage": "Tournament round or stage (group, knockout, heats, final).",
    "match_event": "Individual match, fixture, or event contest.",
    "match_side": "Contestant performance and score details per match.",
    "olympic_result": "Olympic event placements, medal awards, times, and records.",
    "metric_definition": "Statistical metric definitions catalogue across sports.",
    "performance_stat": "Atomic performance statistics linked to participants and editions.",
    "ranking_snapshot": "Official ranking snapshots published at specific dates.",
    "ranking_entry": "Rank positions of participants within snapshots.",
    "record_entry": "All-time milestones and historical records.",
    "ingestion_run": "Audit log for batch data collection and validation runs.",
    "data_quality_issue": "Itemized row validation errors and anomaly flags.",
}

VIEW_DESCRIPTIONS = {
    "v_tournament_tracking": "Tracking view of upcoming, ongoing, and completed tournament editions with winners.",
    "v_edition_summary": "One-row summary per edition with participant count, match counts, and champion.",
    "v_participant_edition_totals": "Aggregated metric totals and averages per participant per tournament edition.",
    "v_win_loss_record": "Matches played, wins, losses, draws, win percentage, and loss percentage.",
    "v_previous_winners": "Historical tournament champions and runners-up across completed editions.",
}


def generate_markdown() -> str:
    lines = [
        "# SportStats — Data Dictionary",
        "",
        "> Automatically generated from SQLAlchemy ORM metadata and database schema specifications.",
        "",
        "## 1. Schema Overview",
        "",
        f"The SportStats relational model consists of **{len(Base.metadata.tables)} tables** and **{len(VIEW_DESCRIPTIONS)} analytical views** structured into 4 logical groups (Figure 2 in research report):",
        "- **Tournament Information & Tracking**: `sport`, `discipline`, `country`, `venue`, `tournament`, `tournament_edition`, `stage`, `match_event`, `match_side`, `olympic_result`",
        "- **Participant Information**: `participant`, `player_profile`, `team_profile`, `team_membership`, `edition_participant`",
        "- **Performance Statistics**: `metric_definition`, `performance_stat`",
        "- **Rankings, Records & Provenance**: `ranking_snapshot`, `ranking_entry`, `record_entry`, `source`, `ingestion_run`, `data_quality_issue`",
        "",
        "---",
        "",
        "## 2. Metric Catalogue Summary (Figure 3 Depth of Statistics)",
        "",
        "| Sport Code | Sport Name | Total Metrics Tracked | Report Figure 3 Target | Status |",
        "|---|---|---|---|---|",
    ]

    counts = get_catalogue_counts_by_sport()
    targets = {
        "cricket": 10,
        "football": 10,
        "badminton": 9,
        "basketball": 10,
        "tennis": 10,
        "kabaddi": 10,
        "olympic": 10,
    }
    for code, count in counts.items():
        target = targets.get(code, 0)
        status = "✅ Exact Match" if count == target else "⚠️ Discrepancy"
        lines.append(f"| `{code}` | {code.capitalize()} | **{count}** | {target} | {status} |")

    lines.extend(
        [
            "",
            f"**Total Metrics across all sports**: **{len(METRICS_CATALOGUE)}**",
            "",
            "---",
            "",
            "## 3. Relational Tables",
            "",
        ]
    )

    for table_name, table in sorted(Base.metadata.tables.items()):
        desc = TABLE_DESCRIPTIONS.get(table_name, "Relational table.")
        lines.append(f"### Table: `{table_name}`")
        lines.append(f"*{desc}*")
        lines.append("")
        lines.append("| Column Name | Type | PK | Nullable | FK / Constraints | Description |")
        lines.append("|---|---|---|---|---|---|")

        for col in table.columns:
            pk = "✅" if col.primary_key else ""
            nullable = "NULL" if col.nullable else "**NOT NULL**"
            col_type = str(col.type)

            fk_info = []
            for fk in col.foreign_keys:
                fk_info.append(f"FK -> `{fk.target_fullname}`")

            constraints_str = ", ".join(fk_info) if fk_info else "-"

            lines.append(
                f"| `{col.name}` | `{col_type}` | {pk} | {nullable} | {constraints_str} | - |"
            )

        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## 4. Analytical Views (Section 6.8)",
            "",
        ]
    )

    for view_name, desc in VIEW_DESCRIPTIONS.items():
        lines.append(f"### View: `{view_name}`")
        lines.append(f"*{desc}*")
        lines.append("")

    return "\n".join(lines)


def main():
    content = generate_markdown()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Data dictionary generated successfully at {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
