"""Read-only deterministic analysis tools exposed to the AI Analyst Layer.

Strictly disallows raw SQL and write actions. Routes tool calls to tested
analysis modules in `sportstats.analysis` and returns structured JSON-serializable data.
"""

from typing import Any, Dict

from sqlalchemy.orm import Session

from sportstats.analysis.compare import (
    CrossSportComparisonError,
    compare_players,
    compare_teams,
)
from sportstats.analysis.rankings import country_medal_distribution
from sportstats.analysis.trends import year_to_year_trend
from sportstats.db.models import Participant, Sport, Tournament, TournamentEdition

# Tool declarations for LLM function calling
ANALYSIS_TOOLS = [
    {
        "name": "get_tournament_winner",
        "description": "Get winner, runner-up, and format for a specific tournament edition.",
        "parameters": {
            "type": "object",
            "properties": {
                "tournament_name": {
                    "type": "string",
                    "description": "e.g. Cricket World Cup, FIFA World Cup",
                },
                "edition_label": {"type": "string", "description": "e.g. 2023, 2022, Tokyo 2020"},
            },
            "required": ["tournament_name", "edition_label"],
        },
    },
    {
        "name": "compare_participants_stats",
        "description": "Compare 2 or more players or teams on specified metrics. Cross-sport raw comparisons are blocked.",
        "parameters": {
            "type": "object",
            "properties": {
                "participant_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of player or team names",
                },
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of metric codes (e.g. runs, goals, points, win_percentage)",
                },
                "participant_type": {
                    "type": "string",
                    "enum": ["player", "team"],
                    "description": "Type of participant",
                },
            },
            "required": ["participant_names", "metrics"],
        },
    },
    {
        "name": "get_historical_trend",
        "description": "Get year-to-year performance trend and regression for a participant.",
        "parameters": {
            "type": "object",
            "properties": {
                "participant_name": {"type": "string", "description": "Name of player or team"},
                "metric_code": {
                    "type": "string",
                    "description": "Metric code (e.g. runs, win_percentage)",
                },
            },
            "required": ["participant_name", "metric_code"],
        },
    },
    {
        "name": "get_olympic_medal_standings",
        "description": "Get country medal standings and medal share percentages for Olympic Games.",
        "parameters": {
            "type": "object",
            "properties": {
                "edition_label": {"type": "string", "description": "e.g. Tokyo 2020, Paris 2024"},
                "max_slices": {"type": "integer", "description": "Top N countries", "default": 6},
            },
        },
    },
    {
        "name": "get_official_rankings",
        "description": "Get official world ranking snapshot for a sport.",
        "parameters": {
            "type": "object",
            "properties": {
                "sport_code": {"type": "string", "description": "e.g. cricket, football, tennis"},
            },
            "required": ["sport_code"],
        },
    },
]


def execute_tool(name: str, args: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Dispatch tool call to deterministic analysis layer."""
    if name == "get_tournament_winner":
        tourn_name = args.get("tournament_name", "").strip()
        edition_label = args.get("edition_label", "").strip()

        ed = (
            db.query(TournamentEdition)
            .join(Tournament, TournamentEdition.tournament_id == Tournament.id)
            .filter(
                Tournament.name.ilike(f"%{tourn_name}%"),
                TournamentEdition.edition_label.ilike(f"%{edition_label}%"),
            )
            .first()
        )
        if not ed:
            return {
                "status": "not_found",
                "message": f"No verified edition found for '{tourn_name}' ({edition_label})",
            }

        winner = (
            db.query(Participant).filter(Participant.id == ed.winner_participant_id).first()
            if ed.winner_participant_id
            else None
        )
        runner = (
            db.query(Participant).filter(Participant.id == ed.runner_up_participant_id).first()
            if ed.runner_up_participant_id
            else None
        )

        return {
            "status": "success",
            "tournament": tourn_name,
            "edition": ed.edition_label,
            "year": ed.year,
            "winner": winner.name if winner else "Not available",
            "runner_up": runner.name if runner else "Not available",
            "host_city": ed.host_city,
            "matches_played": ed.matches_or_events_count,
            "source_org": ed.source.organisation if ed.source else "Official Federation",
            "source_url": ed.source.url if ed.source else None,
        }

    elif name == "compare_participants_stats":
        names = args.get("participant_names", [])
        metrics = args.get("metrics", [])
        p_type = args.get("participant_type", "player")

        participants = db.query(Participant).filter(Participant.name.in_(names)).all()
        if not participants:
            return {
                "status": "not_found",
                "message": f"No verified participants found matching: {names}",
            }

        p_ids = [p.id for p in participants]
        try:
            if p_type == "team":
                res = compare_teams(db, p_ids, metrics)
            else:
                res = compare_players(db, p_ids, metrics)
            return {"status": "success", "comparison": res}
        except CrossSportComparisonError as e:
            return {
                "status": "rejected",
                "error": str(e),
                "message": "Cross-sport comparison blocked: raw values not comparable.",
            }

    elif name == "get_historical_trend":
        p_name = args.get("participant_name", "").strip()
        metric_code = args.get("metric_code", "").strip()

        p = db.query(Participant).filter(Participant.name.ilike(f"%{p_name}%")).first()
        if not p:
            return {
                "status": "not_found",
                "message": f"No verified participant found for '{p_name}'",
            }

        trend = year_to_year_trend(db, participant_id=p.id, metric_code=metric_code)
        return {"status": "success", "participant": p.name, "trend": trend}

    elif name == "get_olympic_medal_standings":
        ed_label = args.get("edition_label")
        max_slices = args.get("max_slices", 6)

        edition_id = None
        if ed_label:
            ed = (
                db.query(TournamentEdition)
                .filter(TournamentEdition.edition_label.ilike(f"%{ed_label}%"))
                .first()
            )
            if ed:
                edition_id = ed.id

        dist = country_medal_distribution(db, edition_id=edition_id, max_slices=max_slices)
        return {"status": "success", "distribution": dist}

    elif name == "get_official_rankings":
        sport_code = args.get("sport_code", "").lower().strip()
        sport = db.query(Sport).filter(Sport.code == sport_code).first()
        if not sport:
            return {"status": "not_found", "message": f"Sport '{sport_code}' not found"}

        from sportstats.api.routers.analytics import get_rankings_endpoint

        resp = get_rankings_endpoint(sport=sport_code, db=db)
        return {
            "status": "success",
            "sport": sport_code,
            "rankings": [r.model_dump() for r in resp.data],
        }

    return {"status": "error", "message": f"Unknown tool: {name}"}
