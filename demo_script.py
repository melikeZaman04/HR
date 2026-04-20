import json
from app.domain.agents.ceo_agent import CEOAgent
from app.domain.agents.cfo_agent import CFOAgent
from app.domain.agents.hr_agent import HRAgent
from app.domain.models import ScenarioInput, AgentMessage
from app.domain.services.aggregator import DecisionAggregator

def print_agent_update(agent_name: str, msg: AgentMessage, round_num: int):
    status = "🟢" if msg.stance == "support" else "🔴" if msg.stance == "oppose" else "⚪"
    print(f"\n[{agent_name}] Round {round_num} {status}")
    print(f"  Stance: {msg.stance.upper()} ({int(msg.confidence * 100)}% confidence)")
    print(f"  Reasoning: {msg.reasoning}")
    if round_num > 1 and "Çapraz analiz" in msg.reasoning:
        print("  ⚡ CROSS-ANALYSIS DETECTED!")

def run_simulation(scenario: ScenarioInput):
    print(f"\n{'='*60}")
    print(f"🚜 FERRARI TEST DRIVE: {scenario.name}")
    print(f"💰 Budget: ${scenario.budget_million_usd}M | 📈 ROI: {scenario.expected_roi_percent}% | ⚠️ Risk: {scenario.risk_level}/10 | 👥 Team: {scenario.team_readiness}/10")
    print(f"{'='*60}")

    # Initialize Agents
    ceo = CEOAgent()
    cfo = CFOAgent()
    hr = HRAgent()
    aggregator = DecisionAggregator()

    # --- ROUND 1: Independent Analysis ---
    print("\n🏁 ROUND 1: INITIAL POSITIONS (Blind Analysis)")
    ceo_msg1 = ceo.analyze(scenario)
    cfo_msg1 = cfo.analyze(scenario)
    hr_msg1 = hr.analyze(scenario)

    print_agent_update("CEO", ceo_msg1, 1)
    print_agent_update("CFO", cfo_msg1, 1)
    print_agent_update("HR", hr_msg1, 1)

    previous_messages = [ceo_msg1, cfo_msg1, hr_msg1]

    # --- ROUND 2: Debate & Cross-Examination ---
    print("\n🏁 ROUND 2: THE DEBATE (Cross-Examination)")
    ceo_msg2 = ceo.analyze(scenario, previous_messages)
    cfo_msg2 = cfo.analyze(scenario, previous_messages)
    hr_msg2 = hr.analyze(scenario, previous_messages)

    print_agent_update("CEO", ceo_msg2, 2)
    print_agent_update("CFO", cfo_msg2, 2)
    print_agent_update("HR", hr_msg2, 2)

    # --- FINAL DECISION ---
    print("\n🏁 FINAL BOARD DECISION")
    results = [
        ceo_msg2.to_legacy_result(),
        cfo_msg2.to_legacy_result(),
        hr_msg2.to_legacy_result()
    ]
    
    final = aggregator.aggregate(results)
    print(f"\n🏆 VERDICT: {final.decision.value} (Score: {final.final_score}/100)")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    # Scenario 1: High Risk, High Reward (The "Moonshot")
    moonshot = ScenarioInput(
        name="Project Moonshot",
        description="Massive AI overhaul",
        budget_million_usd=15.0,  # Large Tier
        expected_roi_percent=45.0, # High ROI
        risk_level=8,             # Very High Risk
        team_readiness=5          # Mediocre Team
    )

    # Scenario 2: Safe Bet (The "Low Hanging Fruit")
    safe_bet = ScenarioInput(
        name="Optimization Update",
        description="Server cost reduction",
        budget_million_usd=0.8,   # Small Tier
        expected_roi_percent=25.0,
        risk_level=2,
        team_readiness=9
    )

    run_simulation(moonshot)
    run_simulation(safe_bet)
