from app.domain.agents.base import Agent
from app.domain.models import AgentMessage, ScenarioInput, Stance, get_agent_metrics, get_agent_stance
from app.infrastructure.llm import call_llm

class SalaryAgent(Agent):
    """
    Salary & Budget Calibration Expert (CFO Mindset)
    
    Evaluates the candidate's salary expectations against typical market budget bands.
    Metrics produced:
        - budget_fit (0-10): How well the expectation fits the company budget
        - market_alignment (0-10): How realistic the expectation is for their experience
    """
    
    def _build_system_prompt(self) -> str:
        return (
            "You are a highly rational, budget-conscious CFO or Finance Director. "
            "You evaluate candidates solely on their financial expectations (expected_salary) "
            "comparative to their experience_years and applied_role. "
            "You MUST respond in English only."
        )

    def _build_reasoning_prompt(self, scenario_inputs: ScenarioInput, stance: str, confidence: float) -> str:
        return (
            f"Candidate: {scenario_inputs.candidate_name}\n"
            f"Role: {scenario_inputs.applied_role}\n"
            f"Experience: {scenario_inputs.experience_years} years\n"
            f"Expected Salary: {scenario_inputs.expected_salary} TL\n\n"
            f"Based on your mathematical rules, your stance is '{stance}' with {confidence*100}% confidence.\n"
            "Explain this decision in 2-3 short, finance-focused sentences about budget sustainability and ROI. "
            "Do not change the stance, just justify it."
        )

    def _call_llm(self, system_prompt: str, user_prompt: str, scenario_name: str) -> str:
        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            return call_llm(full_prompt, agent_name="Salary", scenario_name=scenario_name)
        except Exception as e:
            return f"[Salary Fallback] Connection to LLM failed. Reason: {str(e)}"

    def analyze(
        self,
        scenario_inputs: ScenarioInput,
        previous_messages: list[AgentMessage] | None = None,
    ) -> AgentMessage:
        
        # 1. Base Metrics Calculation (Katman 1: Matematik)
        # Basit bir piyasa verisi simülasyonu
        base_budget = 50000
        if "backend" in scenario_inputs.applied_role.lower() or "data" in scenario_inputs.applied_role.lower():
            base_budget = 80000
        elif "frontend" in scenario_inputs.applied_role.lower() or "mobile" in scenario_inputs.applied_role.lower():
            base_budget = 70000
            
        allowed_max = base_budget + (scenario_inputs.experience_years * 5000)
        
        # Calculate how much expected salary deviates from allowed max
        diff_ratio = scenario_inputs.expected_salary / allowed_max
        
        budget_fit = min(10.0, max(0.0, 10.0 - ((diff_ratio - 1.0) * 20.0)))
        market_alignment = min(10.0, max(0.0, 10.0 - abs(1.0 - diff_ratio) * 10.0))

        # 2. Base Stance Logic
        if diff_ratio > 1.2:  # Expected is >20% over budget limits
            stance = "oppose"
            confidence = 0.90
        elif diff_ratio > 1.05:  # Expected is slightly over
            stance = "oppose"
            confidence = 0.60
        elif diff_ratio < 0.8:  # Suspiciously low
            stance = "neutral"
            confidence = 0.60
        else: # Within reasonable budget (0.8 - 1.05)
            stance = "support"
            confidence = 0.80

        # 3. Round Tracking
        current_round = 1
        if previous_messages:
            current_round = max(m.round_number for m in previous_messages) + 1
            
        reasoning_notes = []
        
        # 4. Cross-Metric Analysis
        if current_round > 1 and previous_messages:
            strategy_stance_info = get_agent_stance(previous_messages, "Strategy")
            culture_stance_info = get_agent_stance(previous_messages, "Culture")
            
            if strategy_stance_info:
                strat_s, strat_conf = strategy_stance_info
                # Eğer aday bütçeyi aşıyorsa ama teknik olarak MÜKEMMEL ise tölere et
                if strat_s == "support" and strat_conf > 0.8 and stance == "oppose" and diff_ratio <= 1.2:
                    stance = "neutral"
                    confidence = 0.60
                    reasoning_notes.append("Strategy Agent strongly supports the candidate; willing to flex the budget to neutral.")
                    
            if culture_stance_info:
                cult_s, _ = culture_stance_info
                # Eğer adayın bütçesi uygun olsa bile erken kaçma ihtimali varsa yatırımı (maaşı) riskli bul
                if cult_s == "oppose" and stance == "support":
                    confidence -= 0.20
                    reasoning_notes.append("Culture Agent highlighted churn risk; reducing financial commitment confidence.")

        confidence = max(0.3, min(1.0, confidence))
        
        # 5. Reasoning Generation (Katman 2)
        system_p = self._build_system_prompt()
        user_p = self._build_reasoning_prompt(scenario_inputs, stance, confidence)
        
        fallback_reasoning = (
            f"Budget fit {budget_fit:.1f}/10 and market alignment {market_alignment:.1f}/10. "
            f"Expected {scenario_inputs.expected_salary} vs Max Limit {allowed_max}. "
        )
        if reasoning_notes:
            fallback_reasoning += "Cross analysis: " + " ".join(reasoning_notes) + " "
        fallback_reasoning += f"Result: {stance} ({int(confidence*100)}%)."
        
        llm_reasoning = self._call_llm(system_p, user_p, scenario_inputs.candidate_name)
        
        if "[Salary Fallback]" in llm_reasoning:
            final_reasoning = fallback_reasoning + " | " + llm_reasoning
        else:
            final_reasoning = llm_reasoning

        return AgentMessage(
            agent="Salary",
            stance=stance,
            confidence=round(confidence, 2),
            reasoning=final_reasoning,
            metrics={
                "budget_fit": round(budget_fit, 1),
                "market_alignment": round(market_alignment, 1)
            },
            round_number=current_round
        )

