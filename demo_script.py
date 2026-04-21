import json
from app.domain.agents.strategy_agent import StrategyAgent
from app.domain.agents.salary_agent import SalaryAgent
from app.domain.agents.culture_agent import CultureAgent
from app.domain.models import ScenarioInput, AgentMessage
from app.domain.services.aggregator import DecisionAggregator

def print_agent_update(agent_name: str, msg: AgentMessage, round_num: int):
    status = "??" if msg.stance == "support" else "??" if msg.stance == "oppose" else "?"
    print(f"\n[{agent_name}] Round {round_num} {status}")
    print(f"  Stance: {msg.stance.upper()} ({int(msg.confidence * 100)}% confidence)")
    print(f"  Reasoning: {msg.reasoning}")

def run_simulation(scenario: ScenarioInput):
    print(f"\n{'='*60}")
    print(f"?? HIRESYNC CANDIDATE: {scenario.candidate_name} ({scenario.applied_role})")
    print(f"? Exp: {scenario.experience_years}y | ?? Test: {scenario.tech_test_score}/100 | ?? Salary: {scenario.expected_salary}TL | ?? Loyalty: {scenario.avg_months_per_job}m/job")
    print(f"{'='*60}")

    strategy = StrategyAgent()
    salary = SalaryAgent()
    culture = CultureAgent()
    aggregator = DecisionAggregator()

    print("\n?? ROUND 1: INITIAL POSITIONS (Blind Analysis)")
    strat_msg1 = strategy.analyze(scenario)
    sal_msg1 = salary.analyze(scenario)
    cult_msg1 = culture.analyze(scenario)

    print_agent_update("Strategy", strat_msg1, 1)
    print_agent_update("Salary", sal_msg1, 1)
    print_agent_update("Culture", cult_msg1, 1)

    previous_messages = [strat_msg1, sal_msg1, cult_msg1]

    print("\n?? ROUND 2: THE DEBATE (Cross-Examination)")
    strat_msg2 = strategy.analyze(scenario, previous_messages)
    sal_msg2 = salary.analyze(scenario, previous_messages)
    cult_msg2 = culture.analyze(scenario, previous_messages)

    print_agent_update("Strategy", strat_msg2, 2)
    print_agent_update("Salary", sal_msg2, 2)
    print_agent_update("Culture", cult_msg2, 2)

    print("\n?? FINAL HR DECISION")
    results = [
        strat_msg2.to_legacy_result(),
        sal_msg2.to_legacy_result(),
        cult_msg2.to_legacy_result()
    ]
    
    final = aggregator.aggregate(results)
    print(f"\n?? VERDICT: {final.decision.value} (Score: {final.final_score}/100)")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    candidate1 = ScenarioInput(
        candidate_name="Ali Veli",
        applied_role="Backend Developer",
        experience_years=5,
        tech_test_score=92,
        expected_salary=75000,
        avg_months_per_job=24,
        glassdoor_score=4.5
    )

    candidate2 = ScenarioInput(
        candidate_name="Ayse Yilmaz",
        applied_role="Frontend Developer",
        experience_years=2,
        tech_test_score=60,
        expected_salary=90000,
        avg_months_per_job=4,
        glassdoor_score=3.2
    )

    run_simulation(candidate1)
    run_simulation(candidate2)
