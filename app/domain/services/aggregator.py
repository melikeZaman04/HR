from app.domain.models import AgentResult, AggregatedDecision, FinalDecision


class DecisionAggregator:
    """
    Ajan kararlarını nihai bir öneri halinde birleştirir.

    Eşit ağırlıklı ortalama ve senaryo tipi sınıflandırmasına dayalı
    ağırlıklı toplama işlemlerini destekler.
    """

    def aggregate(
        self,
        agent_results: list[AgentResult],
        weights: dict[str, float] | None = None,
    ) -> AggregatedDecision:
        """
        Ajan sonuçlarını nihai karara dönüştürür.

        Args:
            agent_results: Ajan analiz sonuçlarının listesi.
            weights: İsteğe bağlı ajan_adı → ağırlık (0-1) sözlüğü.
                     None ise eşit ağırlık kullanılır.
                     Ağırlıkların toplamı 1.0 olmalıdır.

        Returns:
            Nihai skor ve kararı içeren AggregatedDecision.
        """
        if not agent_results:
            raise ValueError("agent_results boş olamaz")

        if weights:
            # Senaryo sınıflandırmasına dayalı ağırlıklı ortalama
            total_weight = 0.0
            weighted_sum = 0.0

            for result in agent_results:
                agent_weight = weights.get(result.agent_name, 1.0 / len(agent_results))
                weighted_sum += result.score * agent_weight
                total_weight += agent_weight

            # Ağırlıklar 1'e toplanmıyorsa normalize et
            average = weighted_sum / total_weight if total_weight > 0 else 0
        else:
            # Eşit ağırlıklı ortalama
            average = sum(result.score for result in agent_results) / len(agent_results)

        if average >= 75:
            decision = FinalDecision.APPROVE
        elif average >= 50:
            decision = FinalDecision.REVISE
        else:
            decision = FinalDecision.REJECT

        return AggregatedDecision(final_score=round(average, 2), decision=decision)
