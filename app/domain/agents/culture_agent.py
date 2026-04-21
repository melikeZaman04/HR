from app.domain.agents.base import Agent
from app.domain.models import AgentMessage, ScenarioInput, Stance, get_agent_metrics, get_agent_stance
from app.infrastructure.llm import call_llm

class CultureAgent(Agent):
    """
    Culture & Loyalty Expert (HR Director Mindset)
    
    Evaluates the candidate's job switching frequency and cultural fit.
    Metrics produced:
        - churn_risk (0-10): Risk of leaving the company early
        - cultural_fit (0-10): Fit with company values based on Glassdoor
    """
    
    def _build_system_prompt(self) -> str:
        return (
            "You are a human-centric HR Director who values company culture and employee retention. "
            "You evaluate candidates strictly based on their job-hopping tendency (avg_months_per_job) "
            "and their previous company's culture score (glassdoor_score). "
            "You MUST respond in English only."
        )

    def _build_reasoning_prompt(self, scenario_inputs: ScenarioInput, stance: str, confidence: float) -> str:
        return (
            f"Candidate: {scenario_inputs.candidate_name}\n"
            f"Average Months Per Job: {scenario_inputs.avg_months_per_job} months\n"
            f"Previous Company Glassdoor: {scenario_inputs.glassdoor_score}/5.0\n\n"
            f"Based on your mathematical rules, your stance is '{stance}' with {confidence*100}% confidence.\n"
            "Explain this decision in 2-3 short, HR-focused sentences about churn risk and cultural alignment. "
            "Do not change the stance, just justify it."
        )

    def _call_llm(self, system_prompt: str, user_prompt: str, scenario_name: str) -> str:
        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            return call_llm(full_prompt, agent_name="Culture", scenario_name=scenario_name)
        except Exception as e:
            return f"[Culture Fallback] Connection to LLM failed. Reason: {str(e)}"

    def analyze(
        self,
        scenario_inputs: ScenarioInput,
        previous_messages: list[AgentMessage] | None = None,
    ) -> AgentMessage:
        
        # 1. Base Metrics Calculation (Katman 1: Matematik)
        # Churn risk: lower months = higher risk
        if scenario_inputs.avg_months_per_job < 6:
            churn_risk = 9.5
        elif scenario_inputs.avg_months_per_job < 12:
            churn_risk = 8.0
        elif scenario_inputs.avg_months_per_job < 24:
            churn_risk = 5.0
        else:
            churn_risk = 2.0
            
        # Cultural fit based on glassdoor (assumes passing a high culture company means good traits)
        cultural_fit = min(10.0, max(0.0, scenario_inputs.glassdoor_score * 2.0))
        
        # 2. Base Stance Logic
        if churn_risk >= 8.0: # Job hopper
            stance = "oppose"
            confidence = 0.85
        elif churn_risk >= 5.0 and cultural_fit < 6.0:
            stance = "oppose"
            confidence = 0.60
        elif churn_risk <= 3.0 and cultural_fit >= 7.0:
            stance = "support"
            confidence = 0.90
        elif churn_risk <= 6.0:
            stance = "support"
            confidence = 0.60
        else:
            stance = "neutral"
            confidence = 0.50
            
        # 3. Round Tracking
        current_round = 1
        if previous_messages:
            current_round = max(m.round_number for m in previous_messages) + 1
            
        reasoning_notes = []
        
        # 4. Cross-Metric Analysis
        if current_round > 1 and previous_messages:
            strategy_stance_info = get_agent_stance(previous_messages, "Strategy")
            salary_stance_info = get_agent_stance(previous_messages, "Salary")
            
            if strategy_stance_info:
                strat_s, _ = strategy_stance_info
                if strat_s == "oppose" and stance == "support":
                    confidence -= 0.15
                    reasoning_notes.append("Strategy found technical issues. HR confidence reduced.")
                    
            if salary_stance_info:
                sal_s, _ = salary_stance_info
                if sal_s == "oppose" and stance == "support":
                    confidence -= 0.10
                    reasoning_notes.append("Salary expectations mismatch. HR confidence reduced.")

            # Stance flip: if both other agents strongly oppose, shift to neutral
            strategy_strongly_opposes = (
                strategy_stance_info is not None
                and strategy_stance_info[0] == "oppose"
                and strategy_stance_info[1] >= 0.70
            )
            salary_strongly_opposes = (
                salary_stance_info is not None
                and salary_stance_info[0] == "oppose"
                and salary_stance_info[1] >= 0.70
            )
            if stance == "support" and strategy_strongly_opposes and salary_strongly_opposes:
                stance = "neutral"
                confidence = max(0.40, confidence - 0.10)
                reasoning_notes.append("Revised to neutral: strong consensus opposition from Strategy and Salary agents.")

        confidence = max(0.3, min(1.0, confidence))
        
        # 5. Reasoning Generation (Katman 2)
        system_p = self._build_system_prompt()
        user_p = self._build_reasoning_prompt(scenario_inputs, stance, confidence)
        
        fallback_reasoning = (
            f"Churn risk {churn_risk}/10 and cultural fit {cultural_fit}/10. "
        )
        if reasoning_notes:
            fallback_reasoning += "Cross analysis: " + " ".join(reasoning_notes) + " "
        fallback_reasoning += f"Result: {stance} ({int(confidence*100)}%)."
        
        llm_reasoning = self._call_llm(system_p, user_p, scenario_inputs.candidate_name)
        
        if "[Culture Fallback]" in llm_reasoning:
            final_reasoning = fallback_reasoning + " | " + llm_reasoning
        else:
            final_reasoning = llm_reasoning

        return AgentMessage(
            agent="Culture",
            stance=stance,
            confidence=round(confidence, 2),
            reasoning=final_reasoning,
            metrics={
                "churn_risk": round(churn_risk, 1),
                "cultural_fit": round(cultural_fit, 1)
            },
            round_number=current_round
        )
