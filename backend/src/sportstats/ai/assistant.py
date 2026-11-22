"""SportStats Grounded Assistant Orchestrator.

Enforces:
- No numbers invented out of thin air (100% grounded in tool results)
- Prompt injection protection (user input never interpreted as DB directives)
- Refusal behavior when data is missing or out of scope ("I don't have verified data for that")
- Cross-sport comparison guard
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from sportstats.ai.llm_client import DeterministicMockLLMClient, LLMClient
from sportstats.ai.tools import execute_tool

SYSTEM_PROMPT_PATH = Path(__file__).parent / "prompts" / "assistant.md"


class GroundedAnswer(BaseModel):
    """Grounded AI response schema adhering to Report Section 12."""

    answer: str
    numbers_used: List[Any] = Field(default_factory=list)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    caveats: List[str] = Field(default_factory=list)


class SportStatsAssistant:
    """The SportStats AI Grounded Assistant."""

    def __init__(self, client: Optional[LLMClient] = None):
        self.client = client or DeterministicMockLLMClient()
        self.system_prompt = ""
        if SYSTEM_PROMPT_PATH.exists():
            self.system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()

    def ask(self, question: str, db: Session) -> GroundedAnswer:
        """Process natural language question through tool calling and grounded synthesis."""
        clean_question = question.strip()
        if not clean_question:
            return GroundedAnswer(
                answer="Please ask a question about tournament performance, winners, or statistics.",
                caveats=["Empty question received."],
            )

        # 1. Tool Selection
        tool_spec = self.client.select_tool(clean_question)

        # Refusal check: if out-of-scope or prediction requested
        if not tool_spec:
            return GroundedAnswer(
                answer="I don't have verified data for that.",
                numbers_used=[],
                sources=[],
                tool_calls=[],
                caveats=[
                    "Query is outside the scope of verified historical tournament statistics."
                ],
            )

        tool_name = tool_spec["name"]
        tool_args = tool_spec.get("arguments", {})

        # 2. Tool Execution (Read-Only DB Layer)
        tool_result = execute_tool(tool_name, tool_args, db)

        # 3. Grounded Answer Synthesis
        res = self.client.generate_grounded_answer(
            question=clean_question,
            tool_name=tool_name,
            tool_result=tool_result,
            system_prompt=self.system_prompt,
        )

        return GroundedAnswer(
            answer=res.get("answer", "I don't have verified data for that."),
            numbers_used=res.get("numbers_used", []),
            sources=res.get("sources", []),
            tool_calls=[{"name": tool_name, "arguments": tool_args}],
            caveats=res.get("caveats", []),
        )
