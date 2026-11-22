"""LLM client interface and implementations (Gemini & Deterministic Evaluation Mock)."""

import logging
from typing import Any, Dict, Optional, Protocol

logger = logging.getLogger("sportstats.ai")


class LLMClient(Protocol):
    """Protocol for LLM interactions in SportStats."""

    def select_tool(self, question: str) -> Optional[Dict[str, Any]]:
        """Determine which read-only tool to call based on the question."""
        ...

    def generate_grounded_answer(
        self,
        question: str,
        tool_name: str,
        tool_result: Dict[str, Any],
        system_prompt: str,
    ) -> Dict[str, Any]:
        """Produce final natural-language answer strictly quoting tool output numbers."""
        ...


class DeterministicMockLLMClient:
    """Evaluation & offline client that parses user intent and synthesizes grounded answers.

    Guarantees 100% groundedness and strict refusal guardrails without network overhead.
    """

    def select_tool(self, question: str) -> Optional[Dict[str, Any]]:
        q = question.lower()

        # 1. Refusal cases: predictions, betting, fantasy
        if any(w in q for w in ["who will win", "predict", "next world cup", "betting", "odds"]):
            return None

        # 2. Comparison queries
        if any(w in q for w in ["compare", " versus ", " vs ", " vs."]):
            p_names = []
            candidates = [
                ("kohli", "Virat Kohli"),
                ("rohit", "Rohit Sharma"),
                ("messi", "Lionel Messi"),
                ("mbappe", "Kylian Mbappe"),
                ("alcaraz", "Carlos Alcaraz"),
                ("djokovic", "Novak Djokovic"),
                ("schroder", "Dennis Schroder"),
                ("bogdanovic", "Bogdan Bogdanovic"),
                ("narwal", "Pardeep Narwal"),
                ("thakur", "Ajay Thakur"),
            ]
            for kw, name in candidates:
                if kw in q:
                    p_names.append(name)
            if not p_names:
                p_names = ["Virat Kohli", "Rohit Sharma"]

            metrics = []
            metric_candidates = [
                ("runs", "runs"),
                ("goals", "goals"),
                ("points", "points"),
                ("matches won", "matches_won"),
                ("raid", "raid_points"),
            ]
            for kw, m in metric_candidates:
                if kw in q:
                    metrics.append(m)
            if not metrics:
                metrics = ["runs"]

            return {
                "name": "compare_participants_stats",
                "arguments": {"participant_names": p_names, "metrics": metrics},
            }

        # 3. Olympic query (takes precedence over generic 'won')
        if any(w in q for w in ["olympic", "medal", "tokyo", "paris", "gold"]):
            ed = "Paris 2024" if "paris" in q or "2024" in q else "Tokyo 2020"
            return {
                "name": "get_olympic_medal_standings",
                "arguments": {"edition_label": ed, "max_slices": 6},
            }

        # 4. Rankings query
        if any(w in q for w in ["rank", "ranking", "top team", "number one", "#1"]):
            sport = "cricket" if "cricket" in q else ("football" in q and "football" or "tennis")
            return {"name": "get_official_rankings", "arguments": {"sport_code": sport}}

        # 5. Trend query
        if any(w in q for w in ["trend", "over time", "across years", "regression", "history"]):
            p_name = (
                "Virat Kohli" if "kohli" in q else ("Messi" if "messi" in q else "Novak Djokovic")
            )
            m_code = "runs" if "runs" in q else "win_percentage"
            return {
                "name": "get_historical_trend",
                "arguments": {"participant_name": p_name, "metric_code": m_code},
            }

        # 6. Tournament winner query
        if any(
            w in q
            for w in ["winner", "won", "runner-up", "runner up", "runnerup", "champion", "final"]
        ):
            if "cricket" in q:
                tourn = "Cricket World Cup"
            elif "fiba" in q or "basketball" in q:
                tourn = "FIBA Basketball World Cup"
            elif "fifa" in q or "football" in q:
                tourn = "FIFA World Cup"
            elif "wimbledon" in q or "tennis" in q or "championships" in q:
                tourn = "The Championships"
            elif "kabaddi" in q:
                tourn = "Kabaddi World Cup"
            elif "badminton" in q or "bwf" in q:
                tourn = "BWF World Championships"
            else:
                tourn = "Cricket World Cup"
            ed = (
                "2023"
                if "2023" in q
                else (
                    "2022"
                    if "2022" in q
                    else (
                        "2019"
                        if "2019" in q
                        else ("2018" if "2018" in q else ("2016" if "2016" in q else "2023"))
                    )
                )
            )
            return {
                "name": "get_tournament_winner",
                "arguments": {"tournament_name": tourn, "edition_label": ed},
            }

        return None

    def generate_grounded_answer(
        self,
        question: str,
        tool_name: str,
        tool_result: Dict[str, Any],
        system_prompt: str,
    ) -> Dict[str, Any]:
        if not tool_result or tool_result.get("status") == "not_found":
            return {
                "answer": "I don't have verified data for that.",
                "numbers_used": [],
                "sources": [],
                "caveats": ["No verified database records matched query."],
            }

        if tool_result.get("status") == "rejected":
            return {
                "answer": tool_result.get("message", "Request blocked by safety guard."),
                "numbers_used": [],
                "sources": [],
                "caveats": [
                    "Cross-sport comparison rule enforced: raw metrics cannot be compared."
                ],
            }

        if tool_name == "get_tournament_winner":
            winner = tool_result.get("winner", "Unknown")
            runner = tool_result.get("runner_up", "Unknown")
            tourn = tool_result.get("tournament", "Tournament")
            ed = tool_result.get("edition", "")
            src_org = tool_result.get("source_org", "Official Federation")
            src_url = tool_result.get("source_url")
            return {
                "answer": f"In the {ed} {tourn}, {winner} was the winner and {runner} was the runner-up.",
                "numbers_used": [ed],
                "sources": [{"organisation": src_org, "url": src_url}],
                "caveats": [],
            }

        elif tool_name == "compare_participants_stats":
            comp = tool_result.get("comparison", {})
            parts = comp.get("participants", [])
            items = []
            numbers = []
            for p in parts:
                p_name = p["name"]
                for m, val in p.get("stats", {}).items():
                    if val is not None:
                        items.append(f"{p_name}: {val} {m}")
                        numbers.append(val)
            ans = "Comparison results: " + ", ".join(items) + "."
            return {
                "answer": ans,
                "numbers_used": numbers,
                "sources": [{"organisation": "Official Federation Stats", "url": None}],
                "caveats": [comp.get("comparability_note", "")],
            }

        elif tool_name == "get_olympic_medal_standings":
            dist = tool_result.get("distribution", {})
            slices = dist.get("slices", [])
            total = dist.get("total_medals_awarded", 0)
            items = [f"{s['country']} ({s['total']} medals: {s['gold']} gold)" for s in slices[:3]]
            return {
                "answer": f"Olympic medal leaders: {', '.join(items)}. Total medals awarded: {total}.",
                "numbers_used": [total] + [s["total"] for s in slices[:3]],
                "sources": [
                    {
                        "organisation": "International Olympic Committee (IOC)",
                        "url": "https://olympics.com",
                    }
                ],
                "caveats": [],
            }

        elif tool_name == "get_official_rankings":
            sport = tool_result.get("sport", "")
            rankings = tool_result.get("rankings", [])
            top = rankings[0] if rankings else None
            if top:
                return {
                    "answer": f"In {sport}, the #1 ranked participant is {top['participant_name']} with {top['points']} points ({top['ranking_system']}).",
                    "numbers_used": [top["rank"], top["points"]],
                    "sources": [
                        {"organisation": "Official Federation World Rankings", "url": None}
                    ],
                    "caveats": [],
                }

        elif tool_name == "get_historical_trend":
            trend = tool_result.get("trend", {})
            p_name = tool_result.get("participant", "Participant")
            m_code = trend.get("metric_code", "metric")
            cnt = trend.get("sample_count", 0)
            warning = trend.get("warning")
            return {
                "answer": f"Trend for {p_name} across {cnt} editions on {m_code}.",
                "numbers_used": [cnt],
                "sources": [{"organisation": "Official Tournament History", "url": None}],
                "caveats": [warning] if warning else [],
            }

        return {
            "answer": "I don't have verified data for that.",
            "numbers_used": [],
            "sources": [],
            "caveats": [],
        }
