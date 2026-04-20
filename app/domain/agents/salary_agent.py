from app.domain.agents.base import Agent
from app.domain.models import AgentMessage, ScenarioInput, Stance, get_agent_metrics, get_agent_stance

def _to_financial_inputs(scenario: ScenarioInput) -> dict:
    """
    Convert ScenarioInput to standardized financial inputs format.
    
    Args:
        scenario: Input scenario data
        
    Returns:
        Dict with investment_cost, expected_profit, risk_factor, budget_tier
    """
    budget = scenario.budget_million_usd
    
    if budget < 2:
        budget_tier = "small"
    elif budget <= 10:
        budget_tier = "medium"
    else:
        budget_tier = "large"
        
    return {
        "investment_cost": budget,
        "expected_profit": budget * (1 + scenario.expected_roi_percent / 100),
        "risk_factor": scenario.risk_level / 10.0,
        "budget_tier": budget_tier
    }

class CFOAgent(Agent):
    """
    CFO Agent: Financial analysis focusing on cost, risk, and budget.
    
    Metrics produced:
        - risk_score (0-10): Financial risk assessment
        - cost_impact (float): Investment cost in millions USD
        - roi_estimate (float): Expected return on investment percentage
    """
    
    def _build_reasoning_prompt(self, scenario_inputs: ScenarioInput) -> str:
        """
        CFO ajanı için finansal sürdürülebilirlik ve risk odaklı analiz cümlesi oluşturur.
        Bu şimdilik reasoning alanında loglanır, ileride bir LLM promptunda kullanılacak.
        """
        return f"[CFO Metni]: Finansal sürdürülebilirlik ve risk odaklı analiz. (Bütçe: ${scenario_inputs.budget_million_usd}M)"

    def analyze(
        self,
        scenario_inputs: ScenarioInput,
        previous_messages: list[AgentMessage] | None = None,
    ) -> AgentMessage:
        """
        Perform financial analysis of the scenario.
        
        Args:
            scenario_inputs: Scenario data to analyze
            previous_messages: Optional messages from previous rounds
            
        Returns:
            AgentMessage with CFO's financial assessment
        """
        financial_inputs = _to_financial_inputs(scenario_inputs)
        
        investment_cost = financial_inputs["investment_cost"]
        expected_profit = financial_inputs["expected_profit"]
        risk_factor = financial_inputs["risk_factor"]
        budget_tier = financial_inputs["budget_tier"]
        
        # Calculate ROI
        if investment_cost <= 0:
            roi = 0.0
        else:
            roi = (expected_profit - investment_cost) / investment_cost
            
        risk_penalty = 1.0 - risk_factor
        adjusted_roi = roi * risk_penalty
        
        # 1. Dynamic Thresholds by Budget Tier
        if budget_tier == "large":
            support_threshold = 0.35
            neutral_threshold = 0.15
            risk_ceiling = 0.7
        elif budget_tier == "medium":
            support_threshold = 0.30
            neutral_threshold = 0.10
            risk_ceiling = 0.8
        else: # small
            support_threshold = 0.20
            neutral_threshold = 0.05
            risk_ceiling = 0.9
            
        # 2. Base Stance Logic
        if adjusted_roi >= support_threshold:
            stance = "support"
            confidence = min(1.0, 0.5 + adjusted_roi * 0.5)
        elif adjusted_roi >= neutral_threshold:
            stance = "neutral"
            confidence = 0.5 + abs(adjusted_roi - neutral_threshold * 2) * 0.5
        else:
            stance = "oppose"
            confidence = min(1.0, 0.5 + (neutral_threshold - adjusted_roi) * 2)
            
        # High risk checks
        if risk_factor >= risk_ceiling and stance == "support":
            stance = "neutral"
            confidence = 0.6
            
        # 3. Round Tracking
        current_round = 1
        if previous_messages:
            current_round = max(m.round_number for m in previous_messages) + 1
            
        reasoning_notes = []
        
        # 4. Cross-Metric Analysis
        if current_round > 1 and previous_messages:
            # Analyze HR
            hr_metrics = get_agent_metrics(previous_messages, "HR")
            if hr_metrics:
                talent_availability = hr_metrics.get("talent_availability", 5)
                team_impact = hr_metrics.get("team_impact", 5)
                workload_score = hr_metrics.get("workload_score", 5)
                
                if talent_availability < 4:
                    penalty = (4 - talent_availability) * 0.03
                    confidence -= penalty
                    reasoning_notes.append(f"İK yetenek sıkıntısı raporladı, maliyet riski arttı (-{penalty:.2f}).")
                
                if team_impact < 3:
                     confidence -= 0.08
                     reasoning_notes.append("İK'nın olumsuz ekip etkisi öngörüsü verimliliği düşürebilir.")
                     
                if workload_score < 4:
                    confidence -= 0.06
                    reasoning_notes.append("Yüksek iş yükü (turnover riski) maliyet projeksiyonunu bozabilir.")

            # Analyze CEO
            ceo_metrics = get_agent_metrics(previous_messages, "CEO")
            if ceo_metrics:
                growth_potential = ceo_metrics.get("growth_potential", 0)
                market_alignment = ceo_metrics.get("market_alignment", 0)
                
                if growth_potential >= 8 and market_alignment >= 7:
                    confidence += 0.05
                    reasoning_notes.append("CEO'nun güçlü büyüme öngörüsü finansal risk toleransını artırdı.")
                
                if market_alignment < 4:
                    confidence -= 0.07
                    reasoning_notes.append("CEO'nun pazar uyumsuzluğu tespiti gelir tahminlerini şüpheli kılıyor.")
            
            # Stance Shift Logic
            ceo_stance_info = get_agent_stance(previous_messages, "CEO")
            hr_stance_info = get_agent_stance(previous_messages, "HR")
            
            if ceo_stance_info and hr_stance_info:
                ceo_s, ceo_conf = ceo_stance_info
                hr_s, _ = hr_stance_info
                
                if stance == "oppose" and ceo_s == "support" and hr_s == "support":
                    if adjusted_roi > 0:
                        stance = "neutral"
                        confidence = 0.45
                        reasoning_notes.append("Diğer birimlerin tam desteği ve pozitif ROI nedeniyle itiraz NÖTR'e çekildi.")
                elif stance == "support" and ceo_s == "oppose" and hr_s == "oppose":
                    stance = "neutral"
                    confidence = 0.5
                    reasoning_notes.append("Diğer birimlerin ortak itirazı finansal desteği askıya aldırdı.")
                elif stance == "neutral" and ceo_s == "support" and ceo_conf >= 0.8:
                    confidence = min(0.65, confidence + 0.1)
                    reasoning_notes.append("CEO'nun çok güçlü desteği belirsizliği azalttı.")

        # Ensure confidence bounds
        confidence = max(0.3, min(1.0, confidence))
        
        # JIRA-02: Build reasoning prompt content
        llm_persona_text = self._build_reasoning_prompt(scenario_inputs)
        
        # 5. Reasoning Generation
        risk_score = round(risk_factor * 10, 1)
        roi_estimate = round(roi * 100, 2)
        
        base_reasoning = (
            f"{llm_persona_text} | "
            f"Bütçe {budget_tier} (${investment_cost}M), beklenen ROI %{roi_estimate}. "
            f"Risk skoru: {risk_score}/10. Risk ayarlı ROI: {adjusted_roi:.2f}."
        )
        
        if reasoning_notes:
            final_reasoning = f"{base_reasoning} Çapraz analiz: {' '.join(reasoning_notes)} Sonuç: {stance} (%{int(confidence*100)})."
        else:
            final_reasoning = f"{base_reasoning} Sonuç: {stance} (%{int(confidence*100)})."

        return AgentMessage(
            agent="CFO",
            stance=stance,
            confidence=round(confidence, 2),
            reasoning=final_reasoning,
            metrics={
                "risk_score": risk_score,
                "cost_impact": round(investment_cost, 2),
                "roi_estimate": roi_estimate,
            },
            round_number=current_round
        )

