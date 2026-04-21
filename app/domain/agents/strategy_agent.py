from app.domain.agents.base import Agent
from app.domain.models import AgentMessage, ScenarioInput, Stance, get_agent_metrics, get_agent_stance
from app.infrastructure.llm import call_llm

class StrategyAgent(Agent):
    """
    Strategy & Talent Expert (CTO Mindset)
    
    Evaluates the candidate's technical capability and experience depth.
    Metrics produced:
        - tech_alignment (0-10): Raw technical test score scaled
        - experience_depth (0-10): Experience mapped to a 0-10 scale
    """
    
    def _build_system_prompt(self) -> str:
        return (
            "You are a ruthless, tech-focused CTO Strategy Expert in a tech company. "
            "You evaluate candidates strictly based on their technical test score and experience years. "
            "You MUST respond in English only."
        )

    def _build_reasoning_prompt(self, scenario_inputs: ScenarioInput, stance: str, confidence: float) -> str:
        return (
            f"Candidate: {scenario_inputs.candidate_name}\n"
            f"Role: {scenario_inputs.applied_role}\n"
            f"Experience: {scenario_inputs.experience_years} years\n"
            f"Tech Test Score: {scenario_inputs.tech_test_score}/100\n\n"
            f"Based on your mathematical rules, your stance is '{stance}' with {confidence*100}% confidence.\n"
            "Explain this decision in 2-3 short, highly technical sentences. "
            "Do not change the stance, just justify it."
        )

    def _call_llm(self, system_prompt: str, user_prompt: str, scenario_name: str) -> str:
        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            return call_llm(full_prompt, agent_name="Strategy", scenario_name=scenario_name)
        except Exception as e:
            return f"[Strategy Fallback] Connection to LLM failed. Reason: {str(e)}"

    def analyze(
        self,
        scenario_inputs: ScenarioInput,
        previous_messages: list[AgentMessage] | None = None,
    ) -> AgentMessage:
        
        # 1. Base Metrics Calculation (Katman 1: Deterministik formüller)
        tech_alignment = min(10.0, max(0.0, scenario_inputs.tech_test_score / 10.0))
        experience_depth = min(10.0, max(0.0, scenario_inputs.experience_years * 1.5))
        
        # 2. Base Stance Logic
        if scenario_inputs.tech_test_score < 50:
            stance = "oppose"
            confidence = 0.85
        elif scenario_inputs.tech_test_score < 70 and scenario_inputs.experience_years > 5:
            stance = "oppose"
            confidence = 0.75  # High experience but poor test score -> bad
        elif scenario_inputs.tech_test_score >= 80 and scenario_inputs.experience_years >= 3:
            stance = "support"
            confidence = 0.90
        elif scenario_inputs.tech_test_score >= 70:
            stance = "support"
            confidence = 0.65
        else:
            stance = "neutral"
            confidence = 0.50
            
        # 3. Round Tracking
        current_round = 1
        if previous_messages:
            current_round = max(m.round_number for m in previous_messages) + 1
            
        reasoning_notes = []
        
        # 4. Cross-Metric Analysis (Only after Round 1)
        if current_round > 1 and previous_messages:
            # HR (Culture) info check
            culture_metrics = get_agent_metrics(previous_messages, "Culture")
            culture_stance_info = get_agent_stance(previous_messages, "Culture")
            
            if culture_stance_info:
                cult_s, _ = culture_stance_info
                if cult_s == "oppose" and stance == "support":
                    confidence -= 0.15
                    reasoning_notes.append("Culture Agent flagged high risk. Strategy confidence reduced.")
                    
            # CFO (Salary) info check
            salary_metrics = get_agent_metrics(previous_messages, "Salary")
            salary_stance_info = get_agent_stance(previous_messages, "Salary")
            
            if salary_stance_info:
                sal_s, _ = salary_stance_info
                if sal_s == "oppose" and stance == "support":
                    confidence -= 0.10
                    reasoning_notes.append("Salary expectation is too high. Strategy confidence reduced.")

            # Stance flip: if both other agents strongly oppose, shift to neutral
            culture_strongly_opposes = (
                culture_stance_info is not None
                and culture_stance_info[0] == "oppose"
                and culture_stance_info[1] >= 0.70
            )
            salary_strongly_opposes = (
                salary_stance_info is not None
                and salary_stance_info[0] == "oppose"
                and salary_stance_info[1] >= 0.70
            )
            if stance == "support" and culture_strongly_opposes and salary_strongly_opposes:
                stance = "neutral"
                confidence = max(0.40, confidence - 0.10)
                reasoning_notes.append("Revised to neutral: strong consensus opposition from Culture and Salary agents.")

        confidence = max(0.3, min(1.0, confidence))
        
        # 5. Reasoning Generation (Katman 2: LLM reasoning)
        system_p = self._build_system_prompt()
        user_p = self._build_reasoning_prompt(scenario_inputs, stance, confidence)
        
        fallback_reasoning = (
            f"Tech alignment {tech_alignment}/10 and experience depth {experience_depth}/10. "
        )
        if reasoning_notes:
            fallback_reasoning += "Cross analysis: " + " ".join(reasoning_notes) + " "
        fallback_reasoning += f"Result: {stance} ({int(confidence*100)}%)."
        
        llm_reasoning = self._call_llm(system_p, user_p, scenario_inputs.candidate_name)
        
        if "[Strategy Fallback]" in llm_reasoning:
            final_reasoning = fallback_reasoning + " | " + llm_reasoning
        else:
            final_reasoning = llm_reasoning

        return AgentMessage(
            agent="Strategy",
            stance=stance,
            confidence=round(confidence, 2),
            reasoning=final_reasoning,
            metrics={
                "tech_alignment": round(tech_alignment, 1),
                "experience_depth": round(experience_depth, 1)
            },
            round_number=current_round
        )