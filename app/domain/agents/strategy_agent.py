from app.domain.agents.base import Agent
from app.domain.models import AgentMessage, ScenarioInput, Stance, get_agent_metrics, get_agent_stance

def _to_strategic_inputs(scenario: ScenarioInput) -> dict:
    """
    Convert ScenarioInput to standardized strategic inputs format.
    
    Args:
        scenario: Input scenario data
        
    Returns:
        Dict with strategic_fit (0-1), market_risk (0-1), growth_priority
    """
    # strategic_fit: ROI normalized to 0-1 range (0% = 0, 100%+ = 1)
    strategic_fit = min(1.0, max(0.0, scenario.expected_roi_percent / 100.0))
    
    # market_risk: risk_level (1-10 scale) normalized to 0-1
    market_risk = scenario.risk_level / 10.0
    
    # Dynamic growth priority based on budget size
    # Small projects (<1M) get lower priority (0.3), large projects (>10M) get full priority (1.0)
    growth_priority = min(1.0, max(0.3, scenario.budget_million_usd / 10.0))
    
    return {
        "strategic_fit": strategic_fit,
        "market_risk": market_risk,
        "growth_priority": growth_priority,
    }

class CEOAgent(Agent):
    """
    CEO Agent: Strategic evaluation focusing on growth, market, and vision.
    
    Metrics produced:
        - growth_potential (0-10): Estimated growth opportunity
        - market_alignment (0-10): Alignment with market trends and strategy
    """
    
    def _build_reasoning_prompt(self, scenario_inputs: ScenarioInput) -> str:
        """
        CEO ajanı için role özgü formatlanmış analiz cümlesi oluşturur.
        Bu şimdilik reasoning alanında loglanır, ileride bir LLM promptunda kullanılacak.
        """
        return f"[CEO Metni]: Stratejik büyüme ve pazar uyumu odaklı analiz. (Senaryo: {scenario_inputs.name})"

    def analyze(
        self,
        scenario_inputs: ScenarioInput,
        previous_messages: list[AgentMessage] | None = None,
    ) -> AgentMessage:
        """
        Perform strategic analysis of the scenario.
        
        Args:
            scenario_inputs: Scenario data to analyze
            previous_messages: Optional messages from previous rounds
            
        Returns:
            AgentMessage with CEO's strategic assessment
        """
        strategic_inputs = _to_strategic_inputs(scenario_inputs)
        
        strategic_fit = strategic_inputs["strategic_fit"]
        market_risk = strategic_inputs["market_risk"]
        growth_priority = strategic_inputs["growth_priority"]

        # 1. Base Metrics Calculation
        growth_potential = (strategic_fit * 0.7 + growth_priority * 0.3) * 10
        market_alignment = (1.0 - market_risk) * 10
        
        # 2. Base Stance Logic
        raw_score = (growth_potential * 0.6 + market_alignment * 0.4) / 10.0
        
        if raw_score >= 0.6:
            stance = "support"
            confidence = min(0.9, 0.5 + (raw_score - 0.6))
        elif raw_score >= 0.3:
            stance = "neutral"
            confidence = 0.6
        else:
            stance = "oppose"
            confidence = min(0.9, 0.5 + (0.3 - raw_score))
            
        # 3. Round Tracking
        current_round = 1
        if previous_messages:
            current_round = max(m.round_number for m in previous_messages) + 1
            
        reasoning_notes = []
        
        # 4. Cross-Metric Analysis (Only after Round 1)
        if current_round > 1 and previous_messages:
            # Analyze CFO
            cfo_metrics = get_agent_metrics(previous_messages, "CFO")
            if cfo_metrics:
                cfo_risk = cfo_metrics.get("risk_score", 0)
                cfo_roi = cfo_metrics.get("roi_estimate", 0)
                
                if cfo_risk > 7:
                    penalty = min(0.15, (cfo_risk - 7) * 0.05)
                    confidence -= penalty
                    reasoning_notes.append(f"CFO'nun yüksek risk uyarısı ({cfo_risk}/10) güveni düşürdü (-{penalty:.2f}).")
                
                if cfo_roi < 10.0 and stance == "support":
                    confidence -= 0.1
                    reasoning_notes.append("CFO'nun düşük ROI tahmini nedeniyle güven azaldı.")

            # Analyze HR
            hr_metrics = get_agent_metrics(previous_messages, "HR")
            if hr_metrics:
                team_impact = hr_metrics.get("team_impact", 5)
                talent_availability = hr_metrics.get("talent_availability", 5)
                
                if team_impact < 3:
                    confidence -= 0.1
                    reasoning_notes.append("HR'ın olumsuz ekip etkisi raporu endişe verici.")
                
                if talent_availability < 3 and scenario_inputs.budget_million_usd > 5:
                    confidence -= 0.08
                    reasoning_notes.append("Büyük bütçeli projede yetenek eksikliği riski var.")
            
            # Stance Shift Logic
            cfo_stance_info = get_agent_stance(previous_messages, "CFO")
            hr_stance_info = get_agent_stance(previous_messages, "HR")
            
            if cfo_stance_info and hr_stance_info:
                cfo_s, _ = cfo_stance_info
                hr_s, _ = hr_stance_info
                
                if cfo_s == "oppose" and hr_s == "oppose" and stance == "support":
                    stance = "neutral"
                    confidence = 0.5
                    reasoning_notes.append("Diğer tüm birimler karşı çıktığı için görüş NÖTR olarak revize edildi.")
                elif cfo_s == "support" and hr_s == "support" and stance == "oppose":
                    stance = "neutral"
                    confidence = 0.5
                    reasoning_notes.append("Ekip konsensüsü nedeniyle karşıt görüş yumuşatıldı.")
                elif cfo_s != hr_s:
                    confidence -= 0.05
                    reasoning_notes.append("Yönetim ekibindeki fikir, güveni hafif sarstı.")

        # Ensure confidence bounds
        confidence = max(0.3, min(1.0, confidence))
        
        # JIRA-02: Build reasoning prompt content
        llm_persona_text = self._build_reasoning_prompt(scenario_inputs)
        
        # 5. Reasoning Generation
        base_reasoning = (
            f"{llm_persona_text} | "
            f"Stratejik uyum %{int(strategic_fit*100)} ve pazar riski {int(market_risk*10)}/10. "
            f"Potansiyel: {growth_potential:.1f}/10."
        )
        
        if reasoning_notes:
            final_reasoning = f"{base_reasoning} Çapraz analiz: {' '.join(reasoning_notes)} Sonuç: {stance} (%{int(confidence*100)})."
        else:
            final_reasoning = f"{base_reasoning} Sonuç: {stance} (%{int(confidence*100)})."

        return AgentMessage(
            agent="CEO",
            stance=stance,
            confidence=round(confidence, 2),
            reasoning=final_reasoning,
            metrics={
                "growth_potential": round(growth_potential, 1),
                "market_alignment": round(market_alignment, 1)
            },
            round_number=current_round
        )