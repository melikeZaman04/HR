from app.domain.agents.base import Agent
from app.domain.models import AgentMessage, ScenarioInput, Stance, get_agent_metrics, get_agent_stance

def _to_hr_inputs(scenario: ScenarioInput) -> dict:
    """
    Convert ScenarioInput to standardized HR inputs format.
    
    Args:
        scenario: Input scenario data
        
    Returns:
        Dict with hiring_needed, time_to_hire_months, training_months, team_readiness
    """
    # Hiring needed based on budget and risk (proxy for complexity)
    budget_factor = scenario.budget_million_usd / 5.0
    risk_factor = scenario.risk_level / 5.0
    hiring_needed = int(budget_factor + risk_factor)
    
    # Dynamic time estimates based on hiring volume
    if hiring_needed <= 2:
        time_to_hire = 1.5
        training = 1.0
    elif hiring_needed <= 5:
        time_to_hire = 2.5
        training = 1.5
    else:
        time_to_hire = 3.5
        training = 2.0
        
    # High readiness reduces training time
    if scenario.team_readiness >= 8:
        training = max(0.5, training - 0.5)
        
    return {
        "hiring_needed": max(0, hiring_needed),
        "time_to_hire_months": time_to_hire,
        "training_months": training,
        "team_readiness": scenario.team_readiness,
    }

class HRAgent(Agent):
    """
    HR Agent: Human resources impact evaluation.
    
    Focuses on personnel, competency, and workload considerations.
    
    Metrics produced:
        - talent_availability (0-10): Available talent/hiring feasibility
        - team_impact (0-10): Impact on existing team
        - workload_score (0-10): Workload sustainability assessment
    """
    
    def _build_reasoning_prompt(self, scenario_inputs: ScenarioInput) -> str:
        """
        HR ajanı için ekip kapasitesi ve iş yükü odaklı analiz cümlesi oluşturur.
        Bu şimdilik reasoning alanında loglanır, ileride bir LLM promptunda kullanılacak.
        """
        return f"[HR Metni]: Ekip kapasitesi ve iş yükü odaklı analiz. (Hazır Bulunuşluk: {scenario_inputs.team_readiness}/10)"

    def analyze(
        self,
        scenario_inputs: ScenarioInput,
        previous_messages: list[AgentMessage] | None = None,
    ) -> AgentMessage:
        """
        Perform HR impact analysis of the scenario.
        
        Args:
            scenario_inputs: Scenario data to analyze
            previous_messages: Optional messages from previous rounds
            
        Returns:
            AgentMessage with HR's assessment
        """
        hr_inputs = _to_hr_inputs(scenario_inputs)
        
        team_readiness = hr_inputs["team_readiness"]
        hiring_needed = hr_inputs["hiring_needed"]
        time_to_hire_months = hr_inputs["time_to_hire_months"]
        training_months = hr_inputs["training_months"]
        
        # 1. Base Metrics Calculation
        total_readiness_months = time_to_hire_months + training_months
        
        # Talent availability: scales with hiring volume (inverse)
        talent_availability = max(0, 10 - hiring_needed * 0.8)
        
        # Team impact: readiness mitigated by disruption of hiring
        team_impact = team_readiness * (1 - hiring_needed / 15.0)
        
        # Workload score: inverse of time to productivity
        workload_score = max(0, 10 - total_readiness_months * 1.5)
        
        # 2. Round Tracking
        current_round = 1
        if previous_messages:
            current_round = max(m.round_number for m in previous_messages) + 1
            
        reasoning_notes = []
        
        # 3. Cross-Metric Analysis
        if current_round > 1 and previous_messages:
            # Analyze CFO
            cfo_metrics = get_agent_metrics(previous_messages, "CFO")
            if cfo_metrics:
                cfo_risk = cfo_metrics.get("risk_score", 0)
                cfo_roi = cfo_metrics.get("roi_estimate", 0)
                
                if cfo_risk > 7:
                    talent_availability -= 1.5
                    confidence_penalty = 0.08
                    # Initialize confidence later, tracking penalty here
                    reasoning_notes.append("Yüksek finansal risk nedeniyle yetenek çekme zorlaşabilir.")
                
                if cfo_roi > 30 and cfo_risk < 5:
                    talent_availability += 1.0
                    reasoning_notes.append("Yüksek ROI potansiyeli yetenek havuzunu genişletebilir.")

            # Analyze CEO
            ceo_metrics = get_agent_metrics(previous_messages, "CEO")
            if ceo_metrics:
                market_alignment = ceo_metrics.get("market_alignment", 0)
                growth_potential = ceo_metrics.get("growth_potential", 0)
                
                if market_alignment < 4:
                    team_impact -= 1.0
                    reasoning_notes.append("Pazar belirsizliği ekip motivasyonunu düşürebilir.")
                
                if growth_potential >= 8:
                    workload_score += 0.8
                    reasoning_notes.append("Büyüme vizyonu iş yükü toleransını artırıyor.")

        # Ensure metrics stay in bounds after adjustments
        talent_availability = round(max(0, min(10, talent_availability)), 1)
        team_impact = round(max(0, min(10, team_impact)), 1)
        workload_score = round(max(0, min(10, workload_score)), 1)

        # 4. Base Stance Logic
        # Composite score calculation
        composite = (talent_availability + team_impact + workload_score) / 30.0
        
        if composite >= 0.6:
            stance = "support"
            confidence = min(1.0, 0.5 + composite * 0.5)
        elif composite >= 0.35:
            stance = "neutral"
            confidence = 0.5 + abs(composite - 0.475) * 0.8
        else:
            stance = "oppose"
            confidence = min(1.0, 0.5 + (0.35 - composite) * 1.5)
            
        # Apply confidence penalties/boosts from cross-analysis
        # (Re-applying reasoning notes impact on confidence)
        if current_round > 1:
             # Basic confidence mods from cross-metrics logic were tracking in notes but not applied to 'confidence' variable yet
             # Let's apply them based on the logic described in inputs
             if previous_messages: 
                cfo_metrics = get_agent_metrics(previous_messages, "CFO")
                if cfo_metrics:
                    if cfo_metrics.get("risk_score", 0) > 7:
                        confidence -= 0.08
                    if cfo_metrics.get("roi_estimate", 0) > 30 and cfo_metrics.get("risk_score", 0) < 5:
                        confidence += 0.05
                
                # CEO metrics logic didn't change confidence directly in the prompt requirement, only metrics
                # logic: "market_alignment < 4 → team_impact -= 1.0" -> affects composite -> affects stance/confidence indirectly
                
                # Stance Shift Logic
                ceo_stance = get_agent_stance(previous_messages, "CEO")
                cfo_stance = get_agent_stance(previous_messages, "CFO")
                
                if ceo_stance and cfo_stance:
                    ceo_s, _ = ceo_stance
                    cfo_s, _ = cfo_stance
                    
                    if stance == "oppose" and ceo_s == "support" and cfo_s == "support":
                        if composite > 0.25:
                            stance = "neutral"
                            confidence = 0.45
                            reasoning_notes.append("CEO ve CFO'nun tam desteği nedeniyle itiraz askıya alındı.")
                    elif stance == "support" and ceo_s == "oppose" and cfo_s == "oppose":
                        stance = "neutral"
                        confidence = 0.5
                        reasoning_notes.append("Yönetim ekibinin itirazı nedeniyle destek geri çekildi.")
                    elif ceo_s == "support" and cfo_s == "oppose":
                        confidence -= 0.05
                        reasoning_notes.append("Liderlikteki fikir ayrılığı (CEO vs CFO) riski artırıyor.")

        # Ensure confidence bounds
        confidence = max(0.3, min(1.0, confidence))
        
        # JIRA-02: Build reasoning prompt content
        llm_persona_text = self._build_reasoning_prompt(scenario_inputs)
        
        # 5. Reasoning Generation
        base_reasoning = (
            f"{llm_persona_text} | "
            f"Ekip hazırlığı {team_readiness}/10, {hiring_needed} kişi alınması gerekiyor "
            f"({total_readiness_months} ay adaptasyon). "
            f"Yetenek: {talent_availability}/10, Etki: {team_impact}/10."
        )
        
        if reasoning_notes:
            final_reasoning = f"{base_reasoning} Çapraz analiz: {' '.join(reasoning_notes)} Sonuç: {stance} (%{int(confidence*100)})."
        else:
            final_reasoning = f"{base_reasoning} Sonuç: {stance} (%{int(confidence*100)})."

        return AgentMessage(
            agent="HR",
            stance=stance,
            confidence=round(confidence, 2),
            reasoning=final_reasoning,
            metrics={
                "talent_availability": talent_availability,
                "team_impact": team_impact,
                "workload_score": workload_score,
            },
            round_number=current_round
        )

        
        return AgentMessage(
            agent="HR",
            stance=stance,
            confidence=round(confidence, 2),
            reasoning=reasoning,
            metrics={
                "talent_availability": talent_availability,
                "team_impact": team_impact,
                "workload_score": workload_score,
            },
        )
