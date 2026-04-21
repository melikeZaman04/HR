"""
Senaryo Sınıflandırma Servisi

Senaryoları stratejik kategorilere ayıran kural tabanlı ML sınıflandırıcısı.
Ajanların daha bağlamsal analiz yapmasını ve senaryo tipine göre dinamik
ağırlıklandırma uygulanmasını sağlar.
"""
from dataclasses import dataclass
from enum import Enum

from app.domain.models import ScenarioInput


class ScenarioType(str, Enum):
    """
    İş senaryolarının stratejik niteliğe göre sınıflandırılması.

    Her tip farklı analiz önceliklerini ifade eder:
    - HIGH_GROWTH: ROI potansiyeli ve pazar fırsatına odak
    - COST_OPTIMIZATION: Risk azaltma ve verimlilik odağı
    - TEAM_EXPANSION: İK hazırlığı ve yetenek erişilebilirliğine odak
    - STRATEGIC_PIVOT: Tüm faktörlerin dengesi, yüksek belirsizlik
    - MAINTENANCE: Düşük riskli, sabit durum operasyonları
    """
    HIGH_GROWTH = "high_growth"
    COST_OPTIMIZATION = "cost_optimization"
    TEAM_EXPANSION = "team_expansion"
    STRATEGIC_PIVOT = "strategic_pivot"
    MAINTENANCE = "maintenance"


@dataclass(frozen=True)
class ClassificationResult:
    """
    Güven skorlarıyla birlikte senaryo sınıflandırma sonucu.

    Attributes:
        primary_type: En yüksek olasılıklı senaryo sınıfı
        confidence: Birincil sınıflandırmaya olan güven (0.0-1.0)
        secondary_type: İkinci en yüksek olasılıklı sınıf
        type_scores: Tüm senaryo tipleri için güven skorları
        recommended_weights: Tipe göre önerilen ajan ağırlıkları
        classification_reasoning: Sınıflandırma gerekçesi
    """
    primary_type: ScenarioType
    confidence: float
    secondary_type: ScenarioType | None
    type_scores: dict[str, float]
    recommended_weights: dict[str, float]
    classification_reasoning: str


class ScenarioClassifier:
    """
    Senaryoları kural tabanlı ML ile stratejik kategorilere sınıflandırır.

    Normalize edilmiş özellik çıkarımı ve ağırlıklı puanlama ile
    en uygun senaryo kategorisini belirler.

    Sınıflandırma şunları etkiler:
    - Ajan analiz odağı
    - Dinamik ajan ağırlıklandırması
    - Benzer geçmiş senaryoların önerilmesi
    """

    # HireSync sınıflandırma eşikleri
    HIGH_TECH_THRESHOLD = 80        # tech_test_score (0-100)
    HIGH_EXP_THRESHOLD = 7          # experience_years
    LOW_STABILITY_THRESHOLD = 12    # avg_months_per_job
    HIGH_SALARY_THRESHOLD = 120000  # expected_salary (TL)

    # Senaryo tipine göre varsayılan ajan ağırlıkları
    DEFAULT_WEIGHTS = {
        ScenarioType.HIGH_GROWTH:       {"Strategy": 0.40, "Salary": 0.35, "Culture": 0.25},
        ScenarioType.COST_OPTIMIZATION: {"Strategy": 0.25, "Salary": 0.50, "Culture": 0.25},
        ScenarioType.TEAM_EXPANSION:    {"Strategy": 0.25, "Salary": 0.25, "Culture": 0.50},
        ScenarioType.STRATEGIC_PIVOT:   {"Strategy": 0.45, "Salary": 0.30, "Culture": 0.25},
        ScenarioType.MAINTENANCE:       {"Strategy": 0.33, "Salary": 0.34, "Culture": 0.33},
    }

    def classify(self, scenario: ScenarioInput) -> ClassificationResult:
        """
        Senaryoyu stratejik bir kategoriye sınıflandırır.

        Çok özellikli analiz kullanarak en uygun senaryo tipini
        ve güven skorlarını belirler.

        Args:
            scenario: Sınıflandırılacak senaryo girdisi.

        Returns:
            Tip, güven ve ağırlıkları içeren ClassificationResult.
        """
        features = self._extract_features(scenario)
        type_scores = self._calculate_type_scores(features)

        sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)

        primary_type = ScenarioType(sorted_types[0][0])
        primary_score = sorted_types[0][1]

        secondary_type = None
        if len(sorted_types) > 1 and sorted_types[1][1] > 0.2:
            secondary_type = ScenarioType(sorted_types[1][0])

        reasoning = self._generate_reasoning(scenario, features, primary_type)

        return ClassificationResult(
            primary_type=primary_type,
            confidence=min(primary_score, 1.0),
            secondary_type=secondary_type,
            type_scores=type_scores,
            recommended_weights=self.DEFAULT_WEIGHTS[primary_type],
            classification_reasoning=reasoning,
        )

    def _extract_features(self, scenario: ScenarioInput) -> dict[str, float]:
        """
        HireSync aday verilerinden normalize edilmiş özellikler çıkarır.
        Tüm özellikler 0-1 aralığına normalize edilir.
        """
        tech_norm = scenario.tech_test_score / 100.0
        exp_norm = min(scenario.experience_years / 15.0, 1.0)
        stability_norm = min(scenario.avg_months_per_job / 48.0, 1.0)
        culture_norm = (scenario.glassdoor_score - 1.0) / 4.0
        salary_norm = min(scenario.expected_salary / 150000.0, 1.0)

        return {
            "tech_norm": tech_norm,
            "exp_norm": exp_norm,
            "stability_norm": stability_norm,
            "culture_norm": culture_norm,
            "salary_norm": salary_norm,
            "seniority": tech_norm * exp_norm,
            "churn_risk": 1.0 - stability_norm,
            "budget_efficiency": 1.0 - salary_norm,
        }

    def _calculate_type_scores(self, features: dict[str, float]) -> dict[str, float]:
        """
        Her senaryo tipi için sınıflandırma puanı hesaplar.
        HireSync aday metriklerine dayalı ağırlıklı özellik kombinasyonları kullanır.
        """
        scores = {}

        # HIGH_GROWTH: Güçlü teknik profil + derin deneyim → kıdemli işe alım
        high_growth = (
            0.35 * features["tech_norm"] +
            0.35 * features["exp_norm"] +
            0.20 * features["seniority"] +
            0.10 * features["stability_norm"]
        )
        if features["tech_norm"] > 0.7 and features["exp_norm"] > 0.4:
            high_growth *= 1.4
        scores[ScenarioType.HIGH_GROWTH.value] = high_growth

        # COST_OPTIMIZATION: Bütçe dostu aday → maaş odaklı değerlendirme
        cost_opt = (
            0.55 * features["budget_efficiency"] +
            0.20 * features["tech_norm"] +
            0.15 * features["stability_norm"] +
            0.10 * features["culture_norm"]
        )
        if features["salary_norm"] < 0.4:
            cost_opt *= 1.3
        scores[ScenarioType.COST_OPTIMIZATION.value] = cost_opt

        # TEAM_EXPANSION: Junior/kültür uyumu odaklı → ekip büyümesi
        team_exp = (
            0.45 * (1.0 - features["exp_norm"]) +
            0.30 * features["culture_norm"] +
            0.15 * features["stability_norm"] +
            0.10 * features["tech_norm"]
        )
        if features["exp_norm"] < 0.2:
            team_exp *= 1.4
        scores[ScenarioType.TEAM_EXPANSION.value] = team_exp

        # STRATEGIC_PIVOT: Teknik olarak güçlü ama yüksek churn riski
        pivot = (
            0.40 * features["tech_norm"] +
            0.40 * features["churn_risk"] +
            0.10 * features["exp_norm"] +
            0.10 * (1.0 - features["culture_norm"])
        )
        if features["churn_risk"] > 0.5 and features["tech_norm"] > 0.6:
            pivot *= 1.3
        scores[ScenarioType.STRATEGIC_PIVOT.value] = pivot

        # MAINTENANCE: Dengeli, orta profil → standart işe alım
        maintenance = (
            0.35 * features["stability_norm"] +
            0.30 * features["culture_norm"] +
            0.20 * (features["tech_norm"] * (1.0 - features["tech_norm"]) * 4.0) +
            0.15 * features["budget_efficiency"]
        )
        scores[ScenarioType.MAINTENANCE.value] = max(0.0, maintenance)

        total = sum(scores.values()) + 0.001
        return {k: round(v / total, 3) for k, v in scores.items()}

    def _generate_reasoning(
        self,
        scenario: ScenarioInput,
        features: dict[str, float],
        primary_type: ScenarioType,
    ) -> str:
        """HireSync aday değerlendirmesi için okunabilir sınıflandırma gerekçesi üretir."""
        reasons = []

        if primary_type == ScenarioType.HIGH_GROWTH:
            reasons.append(f"High-growth senior profile: {scenario.tech_test_score}/100 tech score")
            reasons.append(f"{scenario.experience_years} years of experience depth")
            reasons.append("Strategy-heavy senior talent evaluation")

        elif primary_type == ScenarioType.COST_OPTIMIZATION:
            reasons.append(f"Budget-efficient: {scenario.expected_salary:,} TL salary expectation")
            reasons.append("Salary fit is the primary decision axis")

        elif primary_type == ScenarioType.TEAM_EXPANSION:
            reasons.append(f"Junior-mid profile: {scenario.experience_years} years experience")
            reasons.append("Culture fit and retention are critical for growth hire")
            reasons.append("Team capacity building opportunity")

        elif primary_type == ScenarioType.STRATEGIC_PIVOT:
            reasons.append(f"High churn risk: {scenario.avg_months_per_job} avg months/job")
            reasons.append(f"Strong technical signal: {scenario.tech_test_score}/100")
            reasons.append("Multi-perspective risk-balanced evaluation required")

        else:  # MAINTENANCE
            reasons.append("Balanced candidate profile across all metrics")
            reasons.append("Standard hire with moderate seniority and stability")
            reasons.append("Equal-weight balanced evaluation recommended")

        return " | ".join(reasons)

    def get_agent_weights(self, scenario_type: ScenarioType) -> dict[str, float]:
        """Senaryo tipine göre önerilen ajan ağırlıklarını döndürür."""
        return self.DEFAULT_WEIGHTS.get(scenario_type, self.DEFAULT_WEIGHTS[ScenarioType.MAINTENANCE])
