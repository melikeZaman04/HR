from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.domain.models import AgentMessage, AgentResult, AggregatedDecision, ScenarioRecord

if TYPE_CHECKING:
    from app.domain.services.classifier import ClassificationResult


@dataclass(frozen=True)
class RoundResult:
    """Result of a single discussion round."""
    round_number: int
    messages: list[AgentMessage]


@dataclass(frozen=True)
class RoundBasedSimulationResult:
    """
    Result of a round-based multi-agent discussion simulation.
    
    Attributes:
        scenario_id: ID of the scenario being simulated
        rounds: List of round results with agent messages per round
        total_rounds: Number of rounds actually executed
        consensus_reached: True if all agents reached the same stance
        stability_reached: True if no agent changed stance/confidence in last round
        final_messages: The messages from the final round
        agent_outputs: Legacy format for aggregator compatibility
        aggregated_decision: Final decision from aggregator
        classification: Optional ML classification of the scenario
        agent_weights: Weights used for aggregation (if classification was used)
    """
    scenario_id: int
    rounds: list[RoundResult]
    total_rounds: int
    consensus_reached: bool
    stability_reached: bool
    final_messages: list[AgentMessage]
    agent_outputs: list[AgentResult]
    aggregated_decision: AggregatedDecision
    classification: "ClassificationResult | None" = None
    agent_weights: dict[str, float] | None = None


@dataclass(frozen=True)
class SimulationRunResult:
    """Result of running a simulation with all agent outputs (legacy single-round)."""
    scenario_id: int
    agent_messages: list[AgentMessage]  # New protocol messages
    agent_outputs: list[AgentResult]  # Legacy format for aggregator
    aggregated_decision: AggregatedDecision


@dataclass(frozen=True)
class SimulationReadResult:
    """Result of reading a saved simulation."""
    scenario: ScenarioRecord
    agent_outputs: list[AgentResult]
    aggregated_decision: AggregatedDecision
