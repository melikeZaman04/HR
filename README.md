# HireSync AI — Multi-Agent İşe Alım Karar Sistemi

Üç uzman yapay zeka ajanının bir aday hakkında tartışarak konsensüs kararı verdiği, **FastAPI + PostgreSQL + Clean Architecture** tabanlı çok-ajanlı karar destek sistemi.

![Tests](https://img.shields.io/badge/tests-88%20passed-brightgreen)
![Python](https://img.shields.io/badge/python-3.10-blue)
![Architecture](https://img.shields.io/badge/architecture-Clean-orange)
![DB](https://img.shields.io/badge/database-PostgreSQL%2016-336791)

---

## Sistem Durumu (22 Nisan 2026)

| Bileşen | Durum | Detay |
|---------|-------|-------|
| Docker App Container | Çalışıyor | `localhost:8000` |
| Docker DB Container | Çalışıyor (healthy) | `localhost:5432` |
| FastAPI / Swagger UI | Erişilebilir | `http://localhost:8000/docs` |
| PostgreSQL Şeması | HireSync şeması aktif | Migration `0002` head'de |
| Test Suite | 88/88 geçti | `pytest tests/ -v` |
| Aktif Branch | `feature/agent-identities` | PR #1 açık |

---

## Nasıl Çalışır?

Bir aday sisteme girildiğinde üç ajan sırasıyla analiz yapar ve birbirlerinin kararlarını okuyarak güven puanlarını güncellerler:

```
Aday Verisi → [Strategy Agent] → [Salary Agent] → [Culture Agent]
                    ↑                   ↑                 ↑
               Teknik analiz      Bütçe analizi     Kültür analizi
                    └───────────────────┴─────────────────┘
                              DecisionAggregator
                                     ↓
                         MÜLAKATA AL / BEKLET / REDDET
```

---

## Ajan Kimlikleri

### Strategy Agent (CTO Zihniyeti)
- **Sorumluluk:** Teknik yetkinlik ve deneyim derinliği
- **Katman 1 (Matematik):** `tech_test_score` ve `experience_years` üzerinden `tech_alignment` ve `experience_depth` metriklerini üretir
- **Katman 2 (LLM):** Ollama (`qwen2.5:7b`) ile teknik gerekçe yazar
- **Stance Kuralları:**
  - `tech_test_score < 50` → **oppose** (0.85 güven)
  - `tech_test_score < 70` ve `experience_years > 5` → **oppose** (0.75 güven)
  - `tech_test_score >= 80` ve `experience_years >= 3` → **support** (0.90 güven)

### Salary Agent (CFO Zihniyeti)
- **Sorumluluk:** Maaş beklentisini bütçe bandıyla karşılaştırır
- **Katman 1 (Matematik):** Rol bazlı bütçe bandı ile `diff_ratio` hesaplar; `budget_fit` ve `market_alignment` üretir
- **Bütçe Bandı:** Backend/Data: 80.000 TL baz + yıl başına 5.000 TL
- **Stance Kuralları:**
  - `diff_ratio > 1.2` (bütçeyi %20+ aşıyor) → **oppose** (0.90)
  - `diff_ratio > 1.05` → **oppose** (0.60)
  - Bunların dışı → **support** (0.80)

### Culture Agent (HR Direktörü Zihniyeti)
- **Sorumluluk:** İş değiştirme sıklığı ve kültürel uyum
- **Katman 1 (Matematik):** `avg_months_per_job` → `churn_risk`, `glassdoor_score` → `cultural_fit`
- **Stance Kuralları:**
  - `churn_risk >= 8.0` (job hopper) → **oppose** (0.85)
  - `churn_risk <= 3.0` ve `cultural_fit >= 7.0` → **support** (0.90)

### Çapraz Ajan Etkileşimi (Tur 2+)
Her ajan, diğer ajanların kararını okuyarak kendi güven puanını güncelleyebilir:
- Karşı ajan **oppose** verirse destekçi ajanın güveni düşer
- Salary Agent, Strategy çok güçlü support verirse bütçe toleransını artırır

---

## Veritabanı Şeması

### `scenarios` tablosu
```sql
id              SERIAL PRIMARY KEY
candidate_name  VARCHAR(120) NOT NULL
applied_role    VARCHAR(120) NOT NULL
experience_years INTEGER NOT NULL
tech_test_score INTEGER NOT NULL        -- 0-100
avg_months_per_job INTEGER NOT NULL     -- ay cinsinden
glassdoor_score DOUBLE PRECISION NOT NULL -- 1.0-5.0
expected_salary INTEGER NOT NULL        -- TL
created_at      TIMESTAMP NOT NULL
```

### `agent_outputs` tablosu
```sql
id          SERIAL PRIMARY KEY
scenario_id INTEGER REFERENCES scenarios(id) ON DELETE CASCADE
agent_name  VARCHAR(30)  -- "Strategy" | "Salary" | "Culture"
score       INTEGER      -- 0-100 (legacy aggregation skoru)
rationale   TEXT
```

### `final_decisions` tablosu
```sql
id          SERIAL PRIMARY KEY
scenario_id INTEGER REFERENCES scenarios(id) ON DELETE CASCADE UNIQUE
final_score DOUBLE PRECISION
decision    VARCHAR(20)  -- "APPROVE" | "REVISE" | "REJECT"
```

### Migration Geçmişi
| Revizyon | Açıklama |
|----------|----------|
| `0001_initial_tables` | Eski CEO/CFO/HR finansal şema |
| `0002_hireSync_candidate_schema` | HireSync aday şeması (aktif, head) |

---

## API Uç Noktaları

Tümü `http://localhost:8000/api/v1` altında:

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `POST` | `/scenarios` | Yeni aday oluştur |
| `POST` | `/scenarios/{id}/simulate` | 3 ajan simülasyonu çalıştır |
| `GET` | `/scenarios` | Aday listesi (sayfalı) |
| `GET` | `/scenarios/{id}` | Aday detayı |
| `GET` | `/scenarios/{id}/simulation` | Ajan çıktıları + nihai karar |
| `POST` | `/classify` | Aday profilini sınıflandır (ML) |
| `GET` | `/scenarios/{id}/classify` | Kayıtlı adayı sınıflandır |

### Aday Oluşturma

```bash
curl -X POST http://localhost:8000/api/v1/scenarios \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_name": "Ahmet Yılmaz",
    "applied_role": "Backend Developer",
    "experience_years": 5,
    "tech_test_score": 85,
    "avg_months_per_job": 18,
    "glassdoor_score": 4.2,
    "expected_salary": 90000
  }'
```

### Simülasyon Çalıştırma

```bash
curl -X POST http://localhost:8000/api/v1/scenarios/1/simulate
```

Örnek çıktı:
```json
{
  "scenario_id": 1,
  "agent_outputs": [
    {"agent_name": "Strategy", "score": 85, "rationale": "Strong technical profile..."},
    {"agent_name": "Salary",   "score": 72, "rationale": "Salary within budget band..."},
    {"agent_name": "Culture",  "score": 60, "rationale": "Moderate churn risk..."}
  ],
  "final_score": 72.33,
  "final_decision": "REVISE"
}
```

### Karar Eşikleri
| Skor | Karar |
|------|-------|
| ≥ 75 | **APPROVE** — Mülakata Al |
| 50–74 | **REVISE** — Beklet |
| < 50 | **REJECT** — Reddet |

---

## ML Sınıflandırıcı

Her aday simülasyon öncesinde otomatik olarak 5 profile sınıflandırılır ve ajan ağırlıkları dinamik olarak ayarlanır:

| Profil Tipi | Tetikleyici | Strategy | Salary | Culture |
|-------------|-------------|----------|--------|---------|
| `high_growth` | Yüksek teknik + derin deneyim | **%40** | %35 | %25 |
| `cost_optimization` | Bütçe dostu maaş beklentisi | %25 | **%50** | %25 |
| `team_expansion` | Junior profil, iyi kültür uyumu | %25 | %25 | **%50** |
| `strategic_pivot` | Güçlü teknik ama job hopper | **%45** | %30 | %25 |
| `maintenance` | Dengeli, orta profil | %33 | %34 | %33 |

---

## Proje Mimarisi (Clean Architecture)

```
app/
├── domain/                    # İş kuralları — dış bağımlılık yok
│   ├── agents/
│   │   ├── base.py            # Agent soyut sınıfı
│   │   ├── strategy_agent.py  # CTO ajanı
│   │   ├── salary_agent.py    # CFO ajanı
│   │   ├── culture_agent.py   # HR ajanı
│   │   └── factory.py         # Agent listesi üretici
│   ├── models.py              # ScenarioInput, AgentMessage, FinalDecision
│   ├── repositories.py        # Repository interface'leri
│   └── services/
│       ├── aggregator.py      # Ajan kararlarını birleştirir
│       └── classifier.py      # ML profil sınıflandırıcısı
│
├── application/               # Orkestrasyon katmanı
│   └── use_cases/
│       ├── scenario_service.py      # Simülasyon çalıştırır
│       └── scenario_query_service.py # Sorgular
│
├── infrastructure/            # DB, ORM, LLM bağlantıları
│   ├── database/
│   │   ├── models.py          # SQLAlchemy ORM modelleri
│   │   └── session.py         # asyncpg oturumu
│   ├── repositories/          # Repository implementasyonları
│   ├── llm.py                 # Ollama çağrısı
│   └── config.py              # .env ayarları
│
└── presentation/              # FastAPI katmanı
    ├── api/v1/routes/
    │   └── scenarios.py       # Tüm HTTP endpoint'leri
    └── schemas/
        └── scenario.py        # Pydantic request/response şemaları
```

---

## Kurulum ve Çalıştırma

### Gereksinimler
- Docker Desktop
- Python 3.10+ (test için)
- Conda ortamı: `sivecore`

### Docker ile Başlatma

```bash
# Tüm servisleri başlat
docker compose up -d

# Migration'ı uygula (yeni kurulumda)
docker compose exec app python -m alembic upgrade head

# API erişimi
http://localhost:8000/docs
```

### Mevcut Container'lar Duruyorsa

```bash
docker start ai_decision_db ai_decision_app
```

### Test Çalıştırma

```bash
conda activate sivecore
pytest tests/ -v
# Beklenen çıktı: 88 passed
```

---

## Git Akışı

```
main  ←  feature/agent-identities (PR #1 — açık)
         feature/question-agent   (sonraki hedef)
         feature/api-integration  (frontend bağlantısı)
```

### Tamamlanan PR'lar
| PR | Branch | Konu |
|----|--------|------|
| #1 | `feature/agent-identities` | Agent kimlikleri + 8 kritik bug düzeltmesi |

### Sonraki Adımlar
| Branch | Hedef |
|--------|-------|
| `feature/question-agent` | 3 ajanın çıktısını okuyup 8-10 Türkçe mülakat sorusu üreten `question_agent.py` |
| `feature/api-integration` | Next.js frontend dashboard bağlantısı |

---

## Çevre Değişkenleri (`.env`)

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ai_decision_engine
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=30
DEBUG=false
LOG_LEVEL=INFO
```

> **Not:** Uygulama runtime'da `asyncpg` driver'ı kullanır (`postgresql+asyncpg://...`). Alembic migration'ları için `psycopg2` kullanılır. Config otomatik dönüştürür.

---

## Teknik Notlar

- **LLM Fallback:** Ollama erişilemezse ajan deterministik metrik özeti döner, sistem çalışmaya devam eder.
- **Tur Limiti:** Simülasyon varsayılan 2 tur çalışır; konsensüs veya stabilite durumunda erken durur.
- **Agent Sırası:** Strategy → Salary → Culture (her ajan öncekinin çıktısını görür).
- **asyncio_mode:** `pytest.ini` içinde `auto` olarak ayarlanmış, `pytest-asyncio` gerektirir.
