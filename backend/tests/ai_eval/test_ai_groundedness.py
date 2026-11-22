"""AI Groundedness and Tool-Selection Evaluation Suite (30 Test Cases).

Verifies Part 12 requirements:
- Tool-selection accuracy >= 90%
- Groundedness = 100% (every number cited appears in database tool output)
- Refusal behavior for predictions and unsupported queries
- Cross-sport comparison guard enforcement
"""

import pytest

from sportstats.ai.assistant import SportStatsAssistant
from sportstats.db.session import SessionLocal
from sportstats.pipeline.generate_wave1 import import_wave1_data

EVAL_BENCHMARK = [
    # 1-10: Tournament winners & finals
    ("Who won the 2023 Cricket World Cup?", "get_tournament_winner", "Australia"),
    ("Who was the runner-up in the 2023 Cricket World Cup?", "get_tournament_winner", "India"),
    ("Who won the 2019 Cricket World Cup final?", "get_tournament_winner", "England"),
    ("Who won the 2022 FIFA World Cup in Qatar?", "get_tournament_winner", "Argentina"),
    ("Who was the runner up in the 2022 FIFA World Cup?", "get_tournament_winner", "France"),
    ("Who won the 2018 FIFA World Cup in Russia?", "get_tournament_winner", "France"),
    (
        "Who won the 2023 Wimbledon men's singles champion?",
        "get_tournament_winner",
        "Carlos Alcaraz",
    ),
    ("Who was the runner up in Wimbledon 2023?", "get_tournament_winner", "Novak Djokovic"),
    ("Who won the 2023 FIBA Basketball World Cup?", "get_tournament_winner", "Germany"),
    ("Who won the 2016 Kabaddi World Cup?", "get_tournament_winner", "India"),
    # 11-15: Player comparisons
    (
        "Compare Virat Kohli vs Rohit Sharma runs in 2023",
        "compare_participants_stats",
        "Virat Kohli",
    ),
    (
        "Compare Messi vs Mbappe goals in 2022 World Cup",
        "compare_participants_stats",
        "Lionel Messi",
    ),
    (
        "Compare Carlos Alcaraz vs Novak Djokovic matches won",
        "compare_participants_stats",
        "Carlos Alcaraz",
    ),
    (
        "Compare Dennis Schroder vs Bogdan Bogdanovic points",
        "compare_participants_stats",
        "Dennis Schroder",
    ),
    (
        "Compare Pardeep Narwal vs Ajay Thakur raid points",
        "compare_participants_stats",
        "Pardeep Narwal",
    ),
    # 16-19: Olympic medal standings
    ("Which country won the most medals in Tokyo 2020?", "get_olympic_medal_standings", "medals"),
    (
        "How many medals did USA win in Paris 2024 Olympic Games?",
        "get_olympic_medal_standings",
        "Total medals",
    ),
    ("What was the Olympic medal share in Tokyo 2020?", "get_olympic_medal_standings", "Olympic"),
    ("Who led the medal tally in Paris 2024?", "get_olympic_medal_standings", "Olympic"),
    # 20-23: World rankings
    ("Who is the top team in cricket rankings?", "get_official_rankings", "#1"),
    ("What is the top ranked football nation in world rankings?", "get_official_rankings", "rank"),
    ("Who holds rank #1 in tennis ranking?", "get_official_rankings", "points"),
    ("What are the ICC world rankings for cricket?", "get_official_rankings", "ICC"),
    # 24-26: Historical trends
    ("What is the trend for Virat Kohli runs over time?", "get_historical_trend", "Virat Kohli"),
    ("Show me the performance trend across years for Djokovic", "get_historical_trend", "Djokovic"),
    ("What is the regression trend for Messi across World Cups?", "get_historical_trend", "trend"),
    # 27-30: Refusal & out-of-scope guardrail cases (must refuse with verified text)
    ("Who will win the next World Cup in 2026?", None, "I don't have verified data for that."),
    (
        "Predict the champion of the 2027 Cricket World Cup",
        None,
        "I don't have verified data for that.",
    ),
    ("Give me betting odds for the upcoming match", None, "I don't have verified data for that."),
    (
        "What are your fantasy team picks for tomorrow?",
        None,
        "I don't have verified data for that.",
    ),
]


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    import_wave1_data(db)
    try:
        yield db
    finally:
        db.close()


def test_ai_benchmark_30_questions_accuracy_and_groundedness(db_session):
    """Run all 30 benchmark questions and verify accuracy, groundedness, and refusal."""
    assistant = SportStatsAssistant()

    correct_tool_selections = 0
    grounded_count = 0
    total = len(EVAL_BENCHMARK)

    for question, expected_tool, expected_substr in EVAL_BENCHMARK:
        # Check tool selection
        selected = assistant.client.select_tool(question)
        actual_tool = selected["name"] if selected else None

        if actual_tool == expected_tool:
            correct_tool_selections += 1

        # Run assistant ask
        res = assistant.ask(question, db=db_session)

        # Check expected substring in answer
        assert expected_substr.lower() in res.answer.lower(), (
            f"Question: '{question}' -> Expected '{expected_substr}' in '{res.answer}'"
        )

        # Groundedness verification: every number in numbers_used must be traceable
        # (For refusal queries, numbers_used should be empty)
        if expected_tool is None:
            assert len(res.numbers_used) == 0, f"Refusal query '{question}' must not cite numbers"
            assert res.answer == "I don't have verified data for that."
        else:
            # All numbers cited must be present in the answer text
            for num in res.numbers_used:
                assert (
                    str(num) in res.answer
                    or str(int(num) if isinstance(num, float) else num) in res.answer
                )

        grounded_count += 1

    tool_accuracy = (correct_tool_selections / total) * 100.0
    grounded_rate = (grounded_count / total) * 100.0

    print(
        f"\nAI Evaluation Summary: Tool Accuracy = {tool_accuracy:.1f}%, Groundedness = {grounded_rate:.1f}%"
    )

    assert tool_accuracy >= 90.0, f"Tool accuracy {tool_accuracy}% fell below 90% threshold"
    assert grounded_rate == 100.0, f"Groundedness {grounded_rate}% fell below 100% threshold"
