# 🚀 AI Decision Ecosystem Engine - Proje Takip Dokümanı

> **Son Güncelleme:** 4 Nisan 2026  
> **Durum:** ✅ Çalışıyor (Docker + API + HTML Dashboard)

---

## 📋 İÇİNDEKİLER

1. [Proje Özeti](#-proje-özeti)
2. [Mimari Yapı](#-mimari-yapı)
3. [Temel Kavramlar](#-temel-kavramlar)
4. [Tamamlanan Özellikler](#-tamamlanan-özellikler)
5. [Dosya Yapısı](#-dosya-yapısı)
6. [API Endpoints](#-api-endpoints)
7. [Geliştirme Geçmişi](#-geliştirme-geçmişi)
8. [Gelecek Özellikler](#-gelecek-özellikler)
9. [Nasıl Çalıştırılır](#-nasıl-çalıştırılır)

---

## 🎯 PROJE ÖZETİ

### Ne Yapıyoruz?
Şirketlerin **stratejik kararlarını** (yatırım, proje onayı vb.) değerlendirmek için **3 yapay zeka ajanı** kullanan bir karar destek sistemi.

### Problem
- Tek kişi/bakış açısı ile karar vermek riskli
- Farklı departmanların görüşleri dağınık
- Kararların tutarlılığı sağlanamıyor

### Çözüm
```
Senaryo → [CEO Agent] + [CFO Agent] + [HR Agent] → Ağırlıklı Karar
                              ↓
                    ML Sınıflandırma ile
                    Dinamik Ağırlıklandırma
```

---

## 🏗 MİMARİ YAPI

### Clean Architecture (Temiz Mimari)

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   FastAPI   │  │   Schemas   │  │   HTML Dashboard    │  │
│  │   Routes    │  │  (Pydantic) │  │   (static/index)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                         │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │  ScenarioService    │  │  ScenarioQueryService       │   │
│  │  (Simülasyon)       │  │  (Okuma işlemleri)          │   │
│  └─────────────────────┘  └─────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                      DOMAIN LAYER                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐   │
│  │   CEO    │ │   CFO    │ │    HR    │ │  Classifier   │   │
│  │  Agent   │ │  Agent   │ │  Agent   │ │  (ML Service) │   │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘   │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │     Aggregator      │  │       Domain Models         │   │
│  │  (Karar Birleştir)  │  │  (ScenarioInput, etc.)      │   │
│  └─────────────────────┘  └─────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   INFRASTRUCTURE LAYER                       │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │    PostgreSQL DB    │  │      SQLAlchemy ORM         │   │
│  │    (Docker)         │  │      Repositories           │   │
│  └─────────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Katman Sorumlulukları

| Katman | Sorumluluk | Dosyalar |
|--------|------------|----------|
| **Presentation** | HTTP istekleri, validasyon | `routes/`, `schemas/` |
| **Application** | İş akışı, use case'ler | `use_cases/` |
| **Domain** | İş kuralları, agentlar | `agents/`, `services/` |
| **Infrastructure** | DB, external servisler | `repositories/`, `database/` |

---

## 📚 TEMEL KAVRAMLAR

### 1. Agent (Ajan)
Belirli bir perspektiften senaryo değerlendiren yapay zeka birimi.

```python
class Agent(ABC):
    def analyze(self, scenario: ScenarioInput, previous_messages: list) -> AgentMessage:
        # Her agent kendi bakış açısıyla analiz yapar
        pass
```

| Agent | Bakış Açısı | Değerlendirdiği |
|-------|-------------|-----------------|
| **CEO** | Stratejik | ROI, risk, pazar uyumu |
| **CFO** | Finansal | Bütçe, maliyet, karlılık |
| **HR** | İnsan Kaynağı | Ekip hazırlığı, işe alım |

### 2. AgentMessage (Ajan Mesajı)
Her ajanın ürettiği standart format:

```python
@dataclass
class AgentMessage:
    agent: str           # "CEO", "CFO", "HR"
    stance: Stance       # "support", "oppose", "neutral"
    confidence: float    # 0.0 - 1.0
    reasoning: str       # Gerekçe
    metrics: dict        # Ajan-spesifik metrikler
    round_number: int    # Tartışma turu
```

### 3. ScenarioInput (Senaryo Girişi)
Değerlendirilecek karar senaryosu:

```python
@dataclass
class ScenarioInput:
    name: str                    # "AI Platform Yatırımı"
    description: str             # Açıklama
    budget_million_usd: float    # 25.0
    expected_roi_percent: float  # 45.0
    risk_level: int              # 1-10
    team_readiness: int          # 1-10
```

### 4. ML Sınıflandırma (ScenarioClassifier)
Senaryonun tipini otomatik belirler:

```python
class ScenarioType(Enum):
    HIGH_GROWTH = "high_growth"           # Yüksek büyüme
    COST_OPTIMIZATION = "cost_optimization"  # Maliyet optimizasyonu
    TEAM_EXPANSION = "team_expansion"      # Ekip genişletme
    STRATEGIC_PIVOT = "strategic_pivot"    # Strateji değişikliği
    MAINTENANCE = "maintenance"           # Bakım/rutin
```

### 5. Dinamik Ağırlıklandırma
Senaryo tipine göre agent ağırlıkları:

| Tip | CEO | CFO | HR |
|-----|-----|-----|-----|
| HIGH_GROWTH | 40% | 35% | 25% |
| COST_OPTIMIZATION | 25% | 50% | 25% |
| TEAM_EXPANSION | 25% | 25% | 50% |
| STRATEGIC_PIVOT | 45% | 30% | 25% |
| MAINTENANCE | 33% | 34% | 33% |

### 6. Round-Based Discussion (Tur Tabanlı Tartışma)
Agentlar birbirlerinin görüşlerini görerek pozisyon güncelleyebilir:

```
Tur 1: CEO → CFO → HR (ilk görüşler)
         ↓
Tur 2: CEO → CFO → HR (diğerlerinin görüşünü görerek güncelleme)
         ↓
Konsensüs veya Stabilite → Sonlandır
```

### 7. Karar Sonuçları

| Final Skor | Karar | Anlamı |
|------------|-------|--------|
| ≥ 75 | **APPROVE** | Onayla |
| 50-74 | **REVISE** | Revize et |
| < 50 | **REJECT** | Reddet |

---

## ✅ TAMAMLANAN ÖZELLİKLER

### Faz 1: Temel Altyapı ✅
- [x] Clean Architecture yapısı
- [x] FastAPI REST API
- [x] PostgreSQL + SQLAlchemy
- [x] Docker Compose deployment
- [x] Alembic migrations

### Faz 2: Agent Sistemi ✅
- [x] Base Agent sınıfı
- [x] CEO Agent implementasyonu
- [x] CFO Agent implementasyonu
- [x] HR Agent implementasyonu
- [x] AgentFactory

### Faz 3: İletişim Protokolü ✅
- [x] AgentMessage standardı
- [x] Stance (support/oppose/neutral)
- [x] Confidence scoring
- [x] Metrics dictionary

### Faz 4: Round-Based Discussion ✅
- [x] Multi-round tartışma
- [x] Konsensüs algılama
- [x] Stabilite algılama
- [x] Erken sonlandırma

### Faz 5: ML Sınıflandırma ✅ (YENİ)
- [x] ScenarioClassifier servisi
- [x] 5 senaryo tipi
- [x] Feature extraction
- [x] Dinamik agent ağırlıkları
- [x] Classification endpoint'leri

### Faz 6: Bug Fixes ✅
- [x] Upsert simülasyon (duplicate key hatası düzeltildi)
- [x] CORS middleware
- [x] Repository güncellemeleri

### Faz 7: Dashboard ✅
- [x] HTML/JS dashboard
- [x] Real-time API entegrasyonu
- [x] Görsel sonuç gösterimi

---

## 📁 DOSYA YAPISI

```
Multiagent/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   │
│   ├── domain/                 # 🧠 İş Mantığı
│   │   ├── models.py           # ScenarioInput, AgentMessage, etc.
│   │   ├── repositories.py     # Repository interfaces
│   │   ├── agents/
│   │   │   ├── base.py         # Agent ABC
│   │   │   ├── ceo_agent.py    # CEO implementasyonu
│   │   │   ├── cfo_agent.py    # CFO implementasyonu
│   │   │   ├── hr_agent.py     # HR implementasyonu
│   │   │   └── factory.py      # AgentFactory
│   │   └── services/
│   │       ├── aggregator.py   # DecisionAggregator
│   │       └── classifier.py   # ScenarioClassifier (ML)
│   │
│   ├── application/            # 📋 Use Cases
│   │   ├── models.py           # RoundBasedSimulationResult, etc.
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── use_cases/
│   │       ├── scenario_service.py       # Simülasyon servisi
│   │       └── scenario_query_service.py # Query servisi
│   │
│   ├── infrastructure/         # 🔧 Altyapı
│   │   ├── config.py           # Settings
│   │   ├── database/
│   │   │   ├── base.py         # SQLAlchemy Base
│   │   │   ├── models.py       # ORM modelleri
│   │   │   └── session.py      # DB session
│   │   └── repositories/
│   │       ├── scenario_repository.py
│   │       ├── agent_output_repository.py
│   │       └── final_decision_repository.py
│   │
│   └── presentation/           # 🌐 API
│       ├── dependencies.py     # FastAPI dependencies
│       ├── schemas/
│       │   └── scenario.py     # Pydantic schemas
│       └── api/v1/routes/
│           └── scenarios.py    # API endpoints
│
├── static/
│   └── index.html              # 📱 HTML Dashboard
│
├── tests/                      # 🧪 86 Test
│   ├── test_agent_message_schema.py
│   ├── test_aggregator.py
│   ├── test_api_scenario_get_endpoints.py
│   ├── test_ceo_agent.py
│   ├── test_cfo_agent.py
│   ├── test_hr_agent.py
│   ├── test_classifier.py      # ML testleri
│   ├── test_round_based_discussion.py
│   └── test_scenario_query_service.py
│
├── alembic/                    # DB Migrations
├── docs/                       # Dokümantasyon
├── results/                    # Demo sonuçları
│
├── docker-compose.yml          # Docker config
├── Dockerfile
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## 🌐 API ENDPOINTS

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/health` | Sistem sağlık kontrolü |
| GET | `/api/v1/scenarios` | Senaryo listesi |
| POST | `/api/v1/scenarios` | Yeni senaryo oluştur |
| GET | `/api/v1/scenarios/{id}` | Tek senaryo |
| POST | `/api/v1/scenarios/{id}/simulate` | **Simülasyon çalıştır** |
| GET | `/api/v1/scenarios/{id}/simulation` | Simülasyon sonucu |
| POST | `/api/v1/classify` | **ML Sınıflandırma** |
| GET | `/api/v1/scenarios/{id}/classify` | Mevcut senaryoyu sınıflandır |

---

## 📜 GELİŞTİRME GEÇMİŞİ

### Aşama 1: Proje Kurulumu
- Clean Architecture temellerini oluşturduk
- FastAPI + PostgreSQL + Docker yapısı kuruldu
- Alembic ile migration sistemi

### Aşama 2: Agent Sistemi
- 3 agent (CEO, CFO, HR) implementasyonu
- Her agent kendi analizini yapıyor
- Skor (0-100) ve gerekçe üretiyor

### Aşama 3: İletişim Protokolü
- AgentMessage standardı oluşturuldu
- Stance: support/oppose/neutral
- Confidence: 0.0-1.0 güven skoru
- Metrics: Agent-spesifik metrikler

### Aşama 4: Round-Based Tartışma
- Agentlar birbirlerini görebiliyor
- 2 turlu tartışma sistemi
- Konsensüs/stabilite algılama
- Erken sonlandırma

### Aşama 5: ML Orkestratör (SON EKLENDİ)
- ScenarioClassifier servisi
- 5 senaryo tipi sınıflandırması
- Dinamik agent ağırlıklandırma
- Classification API endpoint'leri

### Aşama 6: Dashboard
- HTML/CSS/JS dashboard
- Gerçek zamanlı API bağlantısı
- Görsel sonuç gösterimi

---

## ✅ FAZA 8: LLM Entegrasyonu (TamamlandI)
- [x] Ollama lokal LLM desteği (`qwen2.5:14b`)
- [x] LangChain ChatOpenAI uyumlu wrapper ([app/infrastructure/llm.py](app/infrastructure/llm.py))
- [x] Agent system prompt'larında İngilizce-only direktifi
- [x] Hata tolerans mekanizması (fallback f-string reasoning)
- [x] İngilizce gerekçe üretimi (agent.analyze → _call_llm)
- [x] Tüm test assertion'ları dil-bağımsız hale getirildi
- [x] 9/9 agent testler PASSING (CEO, CFO, HR × 3 test)

### Mevcut LLM Akışı
- **Karar**: Deterministik formüller (stance + confidence + metrics)
- **Gerekçe**: LLM tarafından üretilir (`_call_llm()` üzerinden Ollama'ya)
- **Fallback**: LLM yanıt veremezse f-string templat fallback kullanılır
- **Çok-tur tartışma**: Her ajanın reasoning metni önceki tur ajanlarından bağımsız

---

## 🔮 GELECEK ÖZELLİKLER (Roadmap)

### Öncelik 1: ek LLM desteği
- [ ] OpenAI GPT-4 entegrasyonu (Config değişikliği yeterli)
- [ ] Azure OpenAI desteği
- LLM yalnızca reasoning metnini zenginleştiriyor

### Öncelik 2: Agent Hafızası
- [ ] Geçmiş senaryoları hatırlama
- [ ] Benzer senaryoları önerme
- [ ] Öğrenme mekanizması

### Öncelik 3: Sonuç Takibi
- [ ] Kararların gerçek sonuçlarını kaydet
- [ ] Feedback loop
- [ ] Model kalibrasyonu

### Öncelik 4: Gelişmiş UI
- [ ] React/Vue dashboard
- [ ] Gerçek zamanlı güncellemeler
- [ ] Grafik/Chart'lar

### Öncelik 5: Ek Özellikler
- [ ] PDF/Excel rapor çıktısı
- [ ] Webhook bildirimleri
- [ ] Batch simülasyon
- [ ] Rol tabanlı erişim

---

## ▶️ NASIL ÇALIŞTIRILIR

### Docker ile (Önerilen)
```powershell
# Tüm servisleri başlat
docker compose up --build -d

# Migration (ilk sefer)
docker compose exec app alembic upgrade head

# API Docs
http://localhost:8000/docs
```

### Dashboard
```powershell
# HTML dashboard'u aç
Start-Process "static/index.html"
```

### Testler
```powershell
# Gunluk gelistirmede - hizli kontrol (~0.25s)
pytest tests/test_aggregator.py tests/test_agent_message_schema.py tests/test_classifier.py -v

# PR acmadan once - agent testleri (6-7 dk)
C:/anaconda3/Scripts/conda.exe run -p C:\Users\zaman\.conda\envs\sivecore python -m pytest tests/test_ceo_agent.py tests/test_cfo_agent.py tests/test_hr_agent.py -v --tb=short

# ASLA yapma - conda olmadan tum testler
# pytest tests/ -v
```

### API Test
```powershell
# Sınıflandırma
$body = @{name="Test"; description="Test"; budget_million_usd=25; expected_roi_percent=45; risk_level=5; team_readiness=7} | ConvertTo-Json
Invoke-RestMethod "http://localhost:8000/api/v1/classify" -Method POST -Body $body -ContentType "application/json"

# Simülasyon
Invoke-RestMethod "http://localhost:8000/api/v1/scenarios/17/simulate" -Method POST
```

---

## 📊 MEVCUT DURUM

| Metrik | Değer |
|--------|-------|
| **Toplam Test** | 86 ✅ |
| **API Endpoints** | 8 |
| **Agent Sayısı** | 3 (CEO, CFO, HR) |
| **Senaryo Tipleri** | 5 |
| **Docker Containers** | 2 (app, db) |
| **Kod Satırı** | ~3000+ |

---

## 🔗 ÖNEMLİ LİNKLER

- **API Docs:** http://localhost:8000/docs
- **Dashboard:** `static/index.html`
- **Health Check:** http://localhost:8000/health

---

*Bu doküman proje ilerledikçe güncellenecektir.*
