from app.domain.agents.base import Agent
from app.domain.models import AgentMessage, ScenarioInput
from app.infrastructure.llm import call_llm


class QuestionAgent(Agent):
    """
    Interview Architect — evidence-obsessed assessment specialist.

    Reads every decision agent's analysis and produces 8-10 surgical interview
    questions categorised as [DAVRANISSAL], [TEKNIK], [DURUMSAL] or [KULTUREL].
    ASCII category tags are used throughout to avoid Turkish Unicode upper-case
    mismatches (e.g. 'i'.upper() == 'I', not 'İ').

    In round 2+ questions shift toward deeper follow-up probes.
    Always returns neutral stance — does not influence the hiring decision.

    Metrics:
        weak_focus_count   — number of opposing agents whose weaknesses are targeted
        strong_focus_count — number of supporting agents whose strengths are validated
        categories_covered — distinct question categories present in the output (0–4)
    """

    # ASCII tags — no Turkish Unicode casing issues
    _CATEGORIES = ["[DAVRANISSAL]", "[TEKNIK]", "[DURUMSAL]", "[KULTUREL]"]

    def _build_system_prompt(self) -> str:
        return (
            "Sen kıdemli, titiz bir Türk işe alım uzmanısın. "
            "Görevin: sana verilen ajan analizlerindeki SPESIFIK zayıf ve güçlü noktalara göre "
            "hedef odaklı mülakat soruları üretmek.\n\n"
            "Kesin kurallar:\n"
            "1. Her soruyu şu etiketlerden biriyle başlat: "
            "[DAVRANISSAL], [TEKNIK], [DURUMSAL] veya [KULTUREL]\n"
            "2. Her soru adayın profilindeki somut bir tespite dayansın — "
            "genel sorular kesinlikle yasak ('kendinizi anlatın', 'güçlü yanlarınız' gibi)\n"
            "3. Doğal, akıcı Türkçe kullan — çeviri hissi veren ifadeler yasak\n"
            "4. Zayıf noktalara odaklanan sorular çoğunlukta olsun (en az 5-6 adet)\n"
            "5. Güçlü noktalara 2-3 doğrulama sorusu ekle\n"
            "6. Karar verme — sadece soru üret"
        )

    def _build_reasoning_prompt(
        self, scenario_inputs: ScenarioInput, stance: str, confidence: float
    ) -> str:
        # QuestionAgent does not use stance-based reasoning.
        # All questioning logic lives in _build_question_prompt.
        return ""

    def _build_risk_signals(self, scenario_inputs: ScenarioInput) -> list[str]:
        """Extract concrete risk signals from candidate data for targeted questioning."""
        signals = []
        if scenario_inputs.tech_test_score < 75:
            signals.append(
                f"TEKNİK RİSK: Teknik skor {scenario_inputs.tech_test_score}/100 — "
                "eşik değerin hemen üstünde. Sistem tasarımı, mimari kararlar ve "
                "kod kalitesi derinlemesine sorgulanmalı."
            )
        if scenario_inputs.tech_test_score >= 85:
            signals.append(
                f"TEKNİK GÜÇLÜ: Teknik skor {scenario_inputs.tech_test_score}/100 — "
                "bu iddiayı gerçek projelerle doğrulayan sorular sor."
            )
        if scenario_inputs.glassdoor_score < 4.0:
            signals.append(
                f"KÜLTÜR SORU İŞARETİ: Eski şirket Glassdoor skoru {scenario_inputs.glassdoor_score}/5 — "
                "neden ayrıldığı, yöneticiyle ilişkisi ve çalışma ortamı hakkında soru sor."
            )
        if scenario_inputs.avg_months_per_job < 18:
            signals.append(
                f"CHURN RİSKİ: Ortalama {scenario_inputs.avg_months_per_job} ay/şirket — "
                "her ayrılışın arkasındaki somut nedeni ve uzun vadeli bağlılık niyetini sorgula."
            )
        if scenario_inputs.avg_months_per_job >= 30:
            signals.append(
                f"SADAKAT GÜÇLÜ: Ortalama {scenario_inputs.avg_months_per_job} ay/şirket — "
                "bu bağlılığı besleyen motivasyonu ve büyüme hedeflerini doğrula."
            )
        if scenario_inputs.experience_years < 3:
            signals.append(
                f"DENEYİM EKSİKLİĞİ: {scenario_inputs.experience_years} yıl deneyim — "
                "öğrenme hızını ve bağımsız problem çözme kapasitesini ölç."
            )
        return signals

    def _build_question_prompt(
        self,
        scenario_inputs: ScenarioInput,
        analyses_text: str,
        round_number: int,
        weak_agents: list[str],
        strong_agents: list[str],
    ) -> str:
        risk_signals = self._build_risk_signals(scenario_inputs)

        signals_block = (
            "\n".join(f"• {s}" for s in risk_signals)
            if risk_signals
            else "• Belirgin metrik riski yok — genel profil değerlendirmesine odaklan."
        )

        weak_summary = (
            f"Karşı çıkan ajanlar: {', '.join(weak_agents)}" if weak_agents else "Belirgin ajan riski yok."
        )
        strong_summary = (
            f"Destekleyen ajanlar: {', '.join(strong_agents)}" if strong_agents else "Belirgin ajan desteği yok."
        )

        depth_note = (
            "İkinci tur — yüzeysel soruları atla. "
            "Birinci turda ortaya çıkan zayıf noktalara daha derin, "
            "somut örnek isteyen follow-up sorular sor."
            if round_number > 1
            else "İlk tur — tüm risk sinyallerini kapsamlı şekilde ele al."
        )

        return (
            f"ADAY PROFİLİ:\n"
            f"Ad: {scenario_inputs.candidate_name}\n"
            f"Pozisyon: {scenario_inputs.applied_role}\n"
            f"Deneyim: {scenario_inputs.experience_years} yıl\n"
            f"Teknik Skor: {scenario_inputs.tech_test_score}/100\n"
            f"Ort. Çalışma: {scenario_inputs.avg_months_per_job} ay/şirket\n"
            f"Glassdoor: {scenario_inputs.glassdoor_score}/5\n"
            f"Maaş Beklentisi: {scenario_inputs.expected_salary:,} {scenario_inputs.salary_currency}\n\n"
            f"AJAN KARARLARI:\n{weak_summary}\n{strong_summary}\n\n"
            f"SPESİFİK RİSK SİNYALLERİ (bu noktalara odaklan):\n{signals_block}\n\n"
            f"AJAN ANALİZLERİ (detay için):\n{analyses_text}\n\n"
            f"GÖREV: {depth_note}\n\n"
            "Her soruyu şu etiketlerden biriyle başlat: "
            "[DAVRANISSAL], [TEKNIK], [DURUMSAL] veya [KULTUREL]\n"
            "Toplam 8-10 soru üret."
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
                f"{scenario_name} adayı için standart mülakat sorularını kullanın."
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
                label = (
                    f"[{msg.agent} | "
                    f"{'KARŞI' if msg.stance == 'oppose' else 'DESTEKLİYOR' if msg.stance == 'support' else 'TARAFSIZ'} "
                    f"%{int(msg.confidence * 100)}]"
                )
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

        # ASCII upper() — no Turkish İ/I mismatch
        output_upper = llm_output.upper()
        categories_covered = sum(1 for tag in self._CATEGORIES if tag in output_upper)

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
