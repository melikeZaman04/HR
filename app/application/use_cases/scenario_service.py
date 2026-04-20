import logging
from dataclasses import dataclass

from app.application.exceptions import ScenarioNotFoundError
from app.application.models import RoundBasedSimulationResult, RoundResult, SimulationRunResult
from app.domain.agents.base import Agent
from app.domain.agents.factory import AgentFactory
from app.domain.models import AgentMessage, ScenarioInput
from app.domain.repositories import AgentOutputRepository, FinalDecisionRepository, ScenarioRepository
from app.domain.services.aggregator import DecisionAggregator
from app.domain.services.classifier import ClassificationResult, ScenarioClassifier


logger = logging.getLogger(__name__)


@dataclass
class _RoundChangeTracker:
    """Tracks changes between rounds for early termination detection."""
    agent: str
    old_stance: str
    new_stance: str
    old_confidence: float
    new_confidence: float

    @property
    def stance_changed(self) -> bool:
        return self.old_stance != self.new_stance

    @property
    def confidence_changed(self) -> bool:
        return abs(self.old_confidence - self.new_confidence) > 0.01


class ScenarioSimulationService:
    """
    Service for creating and running scenario simulations.

    Orchestrates the agent discussion and aggregation process.
    Supports multi-round discussions where agents can update their
    positions based on other agents' messages.

    Optional ML classification enables:
    - Automatic scenario type detection
    - Dynamic agent weighting based on scenario type
    - Enhanced decision aggregation
    """

    CONFIDENCE_BOOST_ON_CONSENSUS = 0.1
    CONFIDENCE_PENALTY_ON_MINORITY = 0.1

    def __init__(
        self,
        scenario_repository: ScenarioRepository,
        agent_output_repository: AgentOutputRepository,
        final_decision_repository: FinalDecisionRepository,
        aggregator: DecisionAggregator | None = None,
        classifier: ScenarioClassifier | None = None,
    ) -> None:
        self.scenario_repository = scenario_repository
        self.agent_output_repository = agent_output_repository
        self.final_decision_repository = final_decision_repository
        self.aggregator = aggregator or DecisionAggregator()
        self.classifier = classifier or ScenarioClassifier()

    async def create_scenario(self, scenario: ScenarioInput) -> int:
        """Create a new scenario and return its ID."""
        return await self.scenario_repository.create(scenario)

    async def run_simulation(
        self,
        scenario_id: int,
        n_rounds: int = 2,
        use_classification: bool = True,
    ) -> RoundBasedSimulationResult:
        """
        Run a round-based multi-agent discussion simulation.

        Each round, agents analyze sequentially (CEO → CFO → HR).
        Each agent sees all messages from current and previous rounds.
        Discussion terminates early if consensus or stability is reached.

        Args:
            scenario_id: ID of the scenario to simulate
            n_rounds: Maximum number of discussion rounds (default: 2)
            use_classification: If True, use ML classification for weighted
                               aggregation (default: True)

        Returns:
            RoundBasedSimulationResult with all rounds, consensus info, and decision

        Raises:
            ScenarioNotFoundError: If scenario doesn't exist
        """
        scenario = await self.scenario_repository.get_by_id(scenario_id)
        if scenario is None:
            raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")

        scenario_inputs = ScenarioInput(
            candidate_name=scenario.candidate_name,
            applied_role=scenario.applied_role,
            experience_years=scenario.experience_years,
            tech_test_score=scenario.tech_test_score,
            avg_months_per_job=scenario.avg_months_per_job,
            glassdoor_score=scenario.glassdoor_score,
            expected_salary=scenario.expected_salary,
        )

        classification: ClassificationResult | None = None
        agent_weights: dict[str, float] | None = None

        if use_classification:
            classification = self.classifier.classify(scenario_inputs)
            agent_weights = classification.recommended_weights
            logger.info(
                f"Scenario classified as {classification.primary_type.value} "
                f"(confidence: {classification.confidence:.2f})"
            )

        agents = AgentFactory.create_default_agents()

        rounds: list[RoundResult] = []
        all_messages: list[AgentMessage] = []
        consensus_reached = False
        stability_reached = False

        for round_num in range(1, n_rounds + 1):
            logger.info(f"Starting round {round_num}/{n_rounds}")

            round_messages = self._run_single_round(
                agents=agents,
                scenario_inputs=scenario_inputs,
                previous_messages=all_messages if all_messages else None,
                round_number=round_num,
            )

            round_result = RoundResult(round_number=round_num, messages=round_messages)
            rounds.append(round_result)

            self._log_round_results(round_num, round_messages)

            consensus_reached = self._check_consensus(round_messages)
            if consensus_reached:
                logger.info(
                    f"Consensus reached in round {round_num} - "
                    f"all agents agree on '{round_messages[0].stance}'"
                )
                break

            if round_num > 1:
                previous_round_messages = rounds[-2].messages
                stability_reached = self._check_stability(previous_round_messages, round_messages)
                if stability_reached:
                    logger.info(f"Stability reached in round {round_num} - no agent changed position")
                    break

            all_messages.extend(round_messages)

        final_messages = rounds[-1].messages
        agent_results = [msg.to_legacy_result() for msg in final_messages]
        aggregated = self.aggregator.aggregate(agent_results, weights=agent_weights)

        await self.agent_output_repository.create_many(scenario_id, agent_results)
        await self.final_decision_repository.create(scenario_id, aggregated)

        classification_str = f", type={classification.primary_type.value}" if classification else ""
        logger.info(
            f"Simulation complete: {len(rounds)} rounds, "
            f"consensus={consensus_reached}, stability={stability_reached}, "
            f"decision={aggregated.decision.value}{classification_str}"
        )

        return RoundBasedSimulationResult(
            scenario_id=scenario_id,
            rounds=rounds,
            total_rounds=len(rounds),
            consensus_reached=consensus_reached,
            stability_reached=stability_reached,
            final_messages=final_messages,
            agent_outputs=agent_results,
            aggregated_decision=aggregated,
            classification=classification,
            agent_weights=agent_weights,
        )

    def _run_single_round(
        self,
        agents: list[Agent],
        scenario_inputs: ScenarioInput,
        previous_messages: list[AgentMessage] | None,
        round_number: int,
    ) -> list[AgentMessage]:
        """
        Run a single discussion round with all agents (sync — no I/O).

        Agents run sequentially, each seeing all previous messages
        plus messages from earlier agents in the current round.
        """
        round_messages: list[AgentMessage] = []

        for agent in agents:
            all_prior = []
            if previous_messages:
                all_prior.extend(previous_messages)
            if round_messages:
                all_prior.extend(round_messages)

            message = agent.analyze(
                scenario_inputs,
                previous_messages=all_prior if all_prior else None,
            )

            message_with_round = AgentMessage(
                agent=message.agent,
                stance=message.stance,
                confidence=message.confidence,
                reasoning=message.reasoning,
                metrics=message.metrics,
                round_number=round_number,
            )
            round_messages.append(message_with_round)

        return round_messages

    def _check_consensus(self, messages: list[AgentMessage]) -> bool:
        """Check if all agents have the same stance."""
        if not messages:
            return False
        first_stance = messages[0].stance
        return all(msg.stance == first_stance for msg in messages)

    def _check_stability(
        self,
        previous_messages: list[AgentMessage],
        current_messages: list[AgentMessage],
    ) -> bool:
        """
        Check if no agent changed stance or confidence significantly.

        Returns True if all agents maintained same stance and confidence
        (within 0.01 tolerance).
        """
        if len(previous_messages) != len(current_messages):
            return False

        prev_by_agent = {msg.agent: msg for msg in previous_messages}
        curr_by_agent = {msg.agent: msg for msg in current_messages}

        for agent_name in prev_by_agent:
            if agent_name not in curr_by_agent:
                return False
            prev = prev_by_agent[agent_name]
            curr = curr_by_agent[agent_name]
            if prev.stance != curr.stance:
                return False
            if abs(prev.confidence - curr.confidence) > 0.01:
                return False

        return True

    def _log_round_results(self, round_num: int, messages: list[AgentMessage]) -> None:
        """Log the results of a discussion round."""
        for msg in messages:
            logger.info(
                f"  Round {round_num} - {msg.agent}: "
                f"stance={msg.stance}, confidence={msg.confidence:.2f}"
            )

    async def run_simulation_legacy(self, scenario_id: int) -> SimulationRunResult:
        """Run a single-round simulation (legacy backward compatibility)."""
        result = await self.run_simulation(scenario_id, n_rounds=1)
        return SimulationRunResult(
            scenario_id=result.scenario_id,
            agent_messages=result.final_messages,
            agent_outputs=result.agent_outputs,
            aggregated_decision=result.aggregated_decision,
        )
