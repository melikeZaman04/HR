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

    # Sınıflandırma için özellik eşikleri
    HIGH_BUDGET_THRESHOLD = 10.0   # Milyon USD
    HIGH_ROI_THRESHOLD = 30.0      # Yüzde
    LOW_ROI_THRESHOLD = 10.0       # Yüzde
    HIGH_RISK_THRESHOLD = 7        # 1-10 ölçeği
    LOW_RISK_THRESHOLD = 3         # 1-10 ölçeği
    HIGH_READINESS_THRESHOLD = 7   # 1-10 ölçeği
    LOW_READINESS_THRESHOLD = 4    # 1-10 ölçeği

    # Senaryo tipine göre varsayılan ajan ağırlıkları
    DEFAULT_WEIGHTS = {
        ScenarioType.HIGH_GROWTH:       {"CEO": 0.40, "CFO": 0.35, "HR": 0.25},
        ScenarioType.COST_OPTIMIZATION: {"CEO": 0.25, "CFO": 0.50, "HR": 0.25},
        ScenarioType.TEAM_EXPANSION:    {"CEO": 0.25, "CFO": 0.25, "HR": 0.50},
        ScenarioType.STRATEGIC_PIVOT:   {"CEO": 0.45, "CFO": 0.30, "HR": 0.25},
        ScenarioType.MAINTENANCE:       {"CEO": 0.33, "CFO": 0.34, "HR": 0.33},
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
        Sınıflandırma için senaryodan normalize edilmiş özellikler çıkarır.

        Tutarlı puanlama için tüm özellikler 0-1 aralığına normalize edilir.
        """
        # Bütçeyi normalize et (0-1, maksimum 50M)
        budget_norm = min(scenario.budget_million_usd / 50.0, 1.0)

        # ROI'yi normalize et (0-1, maksimum %100)
        roi_norm = max(0, min(scenario.expected_roi_percent / 100.0, 1.0))

        # Riski normalize et (1-10 → 0-1)
        risk_norm = (scenario.risk_level - 1) / 9.0

        # Ekip hazırlığını normalize et (1-10 → 0-1)
        readiness_norm = (scenario.team_readiness - 1) / 9.0

        # Türetilmiş özellikler
        roi_risk_ratio = roi_norm / (risk_norm + 0.1)          # Riske göre ROI
        investment_intensity = budget_norm * (1 - risk_norm)   # Güvenli yatırım kapasitesi
        hr_criticality = (1 - readiness_norm) * budget_norm    # İK açığının önemi

        return {
            "budget_norm": budget_norm,
            "roi_norm": roi_norm,
            "risk_norm": risk_norm,
            "readiness_norm": readiness_norm,
            "roi_risk_ratio": min(roi_risk_ratio, 2.0) / 2.0,  # 0-1'e normalize et
            "investment_intensity": investment_intensity,
            "hr_criticality": hr_criticality,
        }

    def _calculate_type_scores(self, features: dict[str, float]) -> dict[str, float]:
        """
        Her senaryo tipi için sınıflandırma puanı hesaplar.

        Her tipe özgü ağırlıklı özellik kombinasyonları kullanır.
        """
        scores = {}

        # HIGH_GROWTH: Yüksek ROI, yüksek bütçe, risk iştahı var
        scores[ScenarioType.HIGH_GROWTH.value] = (
            0.40 * features["roi_norm"] +
            0.30 * features["budget_norm"] +
            0.15 * features["roi_risk_ratio"] +
            0.10 * features["readiness_norm"] +
            0.05 * features["investment_intensity"]
        )

        # COST_OPTIMIZATION: Düşük bütçe, riskten kaçınan, sabit operasyonlar
        cost_opt_score = (
            0.35 * (1 - features["budget_norm"]) +
            0.30 * (1 - features["risk_norm"]) +
            0.15 * (1 - features["roi_norm"]) +
            0.10 * features["readiness_norm"] +
            0.10 * (1 - features["hr_criticality"])
        )
        # Bütçe veya ROI orta/yüksekse ceza uygula
        if features["budget_norm"] > 0.3 or features["roi_norm"] > 0.25:
            cost_opt_score *= 0.6
        scores[ScenarioType.COST_OPTIMIZATION.value] = cost_opt_score

        # TEAM_EXPANSION: İK odaklı, düşük ekip hazırlığı tetikleyici
        team_score = (
            0.45 * (1 - features["readiness_norm"]) +  # Düşük hazırlık = genişleme ihtiyacı
            0.25 * features["hr_criticality"] +
            0.15 * features["budget_norm"] +
            0.10 * (1 - features["risk_norm"]) +
            0.05 * features["roi_norm"]
        )
        # Hazırlık kritik derecede düşükse artır
        if features["readiness_norm"] < 0.35:
            team_score *= 1.4
        scores[ScenarioType.TEAM_EXPANSION.value] = team_score

        # STRATEGIC_PIVOT: Yüksek risk birincil göstergedir
        pivot_score = (
            0.45 * features["risk_norm"] +
            0.25 * features["roi_norm"] +
            0.15 * features["budget_norm"] +
            0.10 * (1 - features["readiness_norm"]) +
            0.05 * features["roi_risk_ratio"]
        )
        # Risk yüksekse artır
        if features["risk_norm"] > 0.7:
            pivot_score *= 1.3
        scores[ScenarioType.STRATEGIC_PIVOT.value] = pivot_score

        # MAINTENANCE: Düşük risk, her şey orta, sabit durum
        maintenance_score = (
            0.35 * (1 - features["risk_norm"]) +
            0.20 * (1 - abs(features["roi_norm"] - 0.15) * 2) +  # Düşük-orta ROI
            0.20 * (1 - features["budget_norm"]) +
            0.15 * features["readiness_norm"] +
            0.10 * (1 - features["hr_criticality"])
        )
        # ROI veya bütçe yüksekse ceza uygula
        if features["roi_norm"] > 0.3 or features["budget_norm"] > 0.4:
            maintenance_score *= 0.5
        scores[ScenarioType.MAINTENANCE.value] = max(0, maintenance_score)

        # Softmax benzeri normalizasyon uygula
        total = sum(scores.values()) + 0.001
        return {k: round(v / total, 3) for k, v in scores.items()}

    def _generate_reasoning(
        self,
        scenario: ScenarioInput,
        features: dict[str, float],
        primary_type: ScenarioType,
    ) -> str:
        """Okunabilir sınıflandırma gerekçesi üretir."""
        reasons = []

        if primary_type == ScenarioType.HIGH_GROWTH:
            reasons.append(f"High expected ROI of {scenario.expected_roi_percent}%")
            if scenario.budget_million_usd >= self.HIGH_BUDGET_THRESHOLD:
                reasons.append(f"Significant investment of ${scenario.budget_million_usd}M")
            reasons.append("Focus on growth and market opportunity")

        elif primary_type == ScenarioType.COST_OPTIMIZATION:
            reasons.append("Conservative investment approach")
            if scenario.risk_level <= self.LOW_RISK_THRESHOLD:
                reasons.append(f"Low risk tolerance (level {scenario.risk_level})")
            reasons.append("Focus on efficiency and cost control")

        elif primary_type == ScenarioType.TEAM_EXPANSION:
            if scenario.team_readiness <= self.LOW_READINESS_THRESHOLD:
                reasons.append(f"Team readiness gap (level {scenario.team_readiness}/10)")
            reasons.append("HR-centric decision with talent implications")
            reasons.append("Focus on team capability building")

        elif primary_type == ScenarioType.STRATEGIC_PIVOT:
            if scenario.risk_level >= self.HIGH_RISK_THRESHOLD:
                reasons.append(f"High risk level ({scenario.risk_level}/10)")
            reasons.append("Major strategic direction change")
            reasons.append("Requires balanced multi-perspective analysis")

        else:  # MAINTENANCE
            reasons.append("Steady-state operational improvement")
            reasons.append("Low disruption to current operations")
            reasons.append("Incremental enhancement focus")

        return " | ".join(reasons)

    def get_agent_weights(self, scenario_type: ScenarioType) -> dict[str, float]:
        """Senaryo tipine göre önerilen ajan ağırlıklarını döndürür."""
        return self.DEFAULT_WEIGHTS.get(scenario_type, self.DEFAULT_WEIGHTS[ScenarioType.MAINTENANCE])
