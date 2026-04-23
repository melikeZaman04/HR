from app.domain.agents.base import Agent
from app.domain.models import AgentMessage, ScenarioInput, get_agent_stance
from app.infrastructure.llm import call_llm


class QuestionAgent(Agent):
    """
    Interview Architect — evidence-obsessed assessment specialist.

    Reads every decision agent's analysis and produces 8-10 surgical interview
    questions categorised as [DAVRANIŞSAL], [TEKNİK], [DURUMSAL] or [KÜLTÜREL].
    In round 2+ questions shift toward deeper follow-up probes.
    Always returns neutral stance — does not influence the hiring decision.

    Metrics:
        weak_focus_count  — number of opposing agents whose weaknesses are targeted
        strong_focus_count — number of supporting agents whose strengths are validated
        categories_covered — distinct question categories present in the output (0–4)
    """

    # Question category tags the LLM is expected to use
    _CATEGORIES = ["[DAVRANIŞSAL]", "[TEKNİK]", "[DURUMSAL]", "[KÜLTÜREL]"]

    def _build_system_prompt(self) -> str:
        return (
            "You are a relentless, evidence-obsessed Interview Architect. "
            "You don't ask generic questions — every question is a surgical tool "
            "designed to expose gaps or confirm strengths identified by other evaluators. "
            "Your style: precise, pressure-testing, behavioral-evidence-driven. "
            "You categorize EVERY question with exactly one tag: "
            "[DAVRANIŞSAL], [TEKNİK], [DURUMSAL], or [KÜLTÜREL]. "
            "All questions must be in Turkish. "
            "Questions like 'kendinizi anlatın' or 'güçlü yanlarınız neler' are strictly forbidden. "
            "You never make a hiring recommendation — only ask."
        )

    def _build_reasoning_prompt(
        self, scenario_inputs: ScenarioInput, stance: str, confidence: float
    ) -> str:
        # QuestionAgent does not use stance-based reasoning.
        # Questions are built dynamically from agent analyses in _build_question_prompt.
        return ""

    def _build_question_prompt(
        self,
        scenario_inputs: ScenarioInput,
        analyses_text: str,
        round_number: int,
        weak_agents: list[str],
        strong_agents: list[str],
    ) -> str:
        if round_number > 1:
            depth_note = (
                "Bu ikinci değerlendirme turu. "
                "Yüzeysel soruları geç — doğrudan zayıf noktalara inen, "
                "somut örnek isteyen follow-up sorulara ağırlık ver."
            )
        else:
            depth_note = (
                "Tüm zayıf ve güçlü noktalara dengeli biçimde değinen kapsamlı sorular sor."
            )

        weak_summary = (
            f"Tespit edilen riskler: {', '.join(weak_agents)}" if weak_agents else "Belirgin risk yok."
        )
        strong_summary = (
            f"Güçlü bulunan alanlar: {', '.join(strong_agents)}" if strong_agents else "Belirgin güçlü alan yok."
        )

        return (
            f"Aday: {scenario_inputs.candidate_name}\n"
            f"Pozisyon: {scenario_inputs.applied_role}\n"
            f"Deneyim: {scenario_inputs.experience_years} yıl\n\n"
            f"Risk Özeti — {weak_summary}\n"
            f"Güç Özeti  — {strong_summary}\n\n"
            f"Detaylı Analizler:\n{analyses_text}\n\n"
            f"{depth_note}\n\n"
            "Kurallar:\n"
            "1. Her soruyu şu etiketlerden tam olarak biriyle başlat: "
            "[DAVRANIŞSAL], [TEKNİK], [DURUMSAL] veya [KÜLTÜREL]\n"
            "2. Zayıf noktalara odaklanan sorular çoğunlukta olsun (en az 5 adet)\n"
            "3. Güçlü noktalara 2-3 doğrulama sorusu ekle\n"
            "4. Her soru spesifik, ölçülebilir ve tek bir konuya odaklı olsun\n"
            "5. Adaya saygılı ve profesyonel bir dil kullan\n"
            "Toplam 8-10 soru üret — ne eksik ne fazla."
        )

    def _call_llm(self, system_prompt: str, user_prompt: str, scenario_name: str) -> str:
        try:
            return call_llm(
                f"{system_prompt}\n\n{user_prompt}",
                agent_name="Question",
                scenario_name=scenario_name,
            )
        except Exception:
            return (
                "[Question Fallback] Teknik bir sorun nedeniyle soru üretilemedi. "
                f"Aday profiline ({scenario_name}) göre standart mülakat sorularını kullanın."
            )

    def analyze(
        self,
        scenario_inputs: ScenarioInput,
        previous_messages: list[AgentMessage] | None = None,
        round_number: int = 1,
    ) -> AgentMessage:

        weak_agents: list[str] = []
        strong_agents: list[str] = []
        analyses: list[str] = []

        if previous_messages:
            for msg in previous_messages:
                if msg.agent == "Question":
                    continue
                label = f"[{msg.agent} | {msg.stance.upper()} %{int(msg.confidence * 100)}]"
                analyses.append(f"{label}:\n{msg.reasoning}")
                if msg.stance == "oppose":
                    weak_agents.append(msg.agent)
                elif msg.stance == "support":
                    strong_agents.append(msg.agent)

        analyses_text = "\n\n".join(analyses) if analyses else "Önceki ajan analizi mevcut değil."

        user_p = self._build_question_prompt(
            scenario_inputs, analyses_text, round_number, weak_agents, strong_agents
        )
        llm_output = self._call_llm(self._build_system_prompt(), user_p, scenario_inputs.candidate_name)

        output_upper = llm_output.upper()
        categories_covered = sum(
            1 for tag in self._CATEGORIES if tag in output_upper
        )

        return AgentMessage(
            agent="Question",
            stance="neutral",
            confidence=0.0,
            reasoning=llm_output,
            metrics={
                "weak_focus_count": float(len(weak_agents)),
                "strong_focus_count": float(len(strong_agents)),
                "categories_covered": float(categories_covered),
            },
            round_number=round_number,
        )
