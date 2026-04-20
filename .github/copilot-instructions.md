# GitHub Copilot - Proje Baglam Dosyasi
# Bu dosyayi .github/copilot-instructions.md olarak kaydet

---

## PROJE: BMU326 Multi-Agent Karar Destek Sistemi

Firat Universitesi yazilim muhendisligi projesi.
3 kisilik takim, Agile/Scrum, sprint bazli ilerleme.

---

## TEKNIK STACK

- Python 3.10+, FastAPI, SQLAlchemy (sync - asyncpg gecisi Sprint 3'te)
- LangChain + Ollama (qwen2.5:14b) - localhost:11434
- PostgreSQL, Docker Compose
- pytest, Conda env adi: `sivecore`
- Windows gelistirme ortami

---

## MIMARI - 4 KATMAN

```
Presentation  -> app/presentation/api/v1/routes/scenarios.py
                app/presentation/schemas/scenario.py
Application   -> app/use_cases/scenario_service.py       <- simulasyon orkestrasyonu
                app/use_cases/scenario_query_service.py
Domain        -> app/domain/models.py                    <- veri modelleri
                app/domain/agents/base.py               <- Agent ABC
                app/domain/agents/ceo_agent.py
                app/domain/agents/cfo_agent.py
                app/domain/agents/hr_agent.py
                app/domain/agents/factory.py
                app/domain/services/aggregator.py
                app/domain/services/classifier.py
Infrastructure-> app/infrastructure/config.py            <- TEK konfigurasyon kaynagi
                app/infrastructure/llm.py               <- get_llm() -> ChatOllama
                app/infrastructure/database/session.py
                app/infrastructure/repositories/
```

---

## AGENT MIMARISI - EN ONEMLI KURAL

Her agent TAM OLARAK su sekilde calisir - bu degistirilemez:

```
analyze(scenario, previous_messages) cagrisi
|
|- KATMAN 1: Deterministik formuller (DOKUNULMAZ)
|  |- stance     -> "support" | "oppose" | "neutral"
|  |- confidence -> 0.0 ile 1.0 arasinda float
|  \- metrics    -> agent'a ozgu dict
|
\- KATMAN 2: LLM reasoning (sadece metin uretir, karara mudahale etmez)
   |- _call_llm() cagrilir
   |- Basarili  -> LLM'in Ingilizce metni reasoning alanina yazilir
   \- Basarisiz -> f-string fallback devreye girer, sistem cokmez
```

**stance ve confidence HER ZAMAN formule belirlenir. LLM ASLA karar vermez.**

---

## HAFIZA SISTEMI - DOGRU ANLAMA

Copilot'a not: Sistemde "hafiza eksik" deme. Iki tur hafiza var:

### Kisa sureli hafiza - MEVCUT VE CALISIYOR
`previous_messages` parametresi ile her agent onceki turun
ciktilarini gorur. 2 tur boyunca agent'lar birbirini okur ve
pozisyonlarini guncelleyebilir.

```python
# scenario_service.py - zaten calisiyor
for round_num in range(1, n_rounds + 1):
    for agent in agents:
        message = agent.analyze(
            scenario_inputs=scenario,
            previous_messages=previous_messages if round_num > 1 else None,
        )
    previous_messages = round_messages  # bir sonraki tura aktarilir
```

### Uzun sureli hafiza - SPRINT 4 (BACKLOG, HENUZ YAPILMAYACAK)
Farkli simulasyonlar arasinda ogrenme. Neo4j graph DB ile
planlanmis. Su an kapsam disi.

---

## TAMAMLANAN ISLER (Sprint 1 + Sprint 2)

### Sprint 1 - Tamamlandi
- [x] CEO, CFO, HR agent'lari - rule-based deterministik karar
- [x] AgentMessage protokolu (stance, confidence, reasoning, metrics)
- [x] PostgreSQL + Docker Compose kurulumu
- [x] Alembic migration'lari
- [x] FastAPI endpoint'leri

### Sprint 2 - Tamamlandi
- [x] JIRA-01: .env.example + config.py SSOT (tek konfigurasyon kaynagi)
- [x] JIRA-02: base.py'e LLM altyapisi (_build_system_prompt, _build_reasoning_prompt, _call_llm)
- [x] CEO/CFO/HR - Ingilizce system prompt + LLM reasoning entegrasyonu
- [x] scenario_service.py - 2 turlu tartisma dongusu dogrulandi (degisiklik gerekmedi)
- [x] config.py SSOT - LLMSettings kaldirildi, tek kaynak
- [x] main.py CORS - allow_origins=["*"] -> settings.ALLOWED_ORIGINS
- [x] Test suite - 58 test, tamami geciyor

### Test durumu (son calistirma)
```
test_aggregator.py          5/5  PASSED  (0.25s)
test_agent_message_schema.py 32/32 PASSED (0.25s)
test_classifier.py          12/12 PASSED (0.25s)
test_ceo_agent.py           3/3  PASSED  (LLM cagrisi - ~130s)
test_cfo_agent.py           3/3  PASSED  (LLM cagrisi - ~130s)
test_hr_agent.py            3/3  PASSED  (LLM cagrisi - ~130s)
```

---

## YANLIS BILINENLER - DUZELTMELI

| Copilot'un Dedigi | Gercek Durum |
|-------------------|--------------|
| "Agent hafiza sistemi yok" | Var - previous_messages ile short-term memory calisiyor |
| "Yeni agent eklenmeli" | Sprint 1-2 kapsaminda degil, backlog'da |
| "Frontend yok" | Sprint planinda hic yoktu, Streamlit Sprint 3'te |
| "Memory/retrieval mekanizmasi eksik" | Neo4j Sprint 4 backlog'unda, su an kapsam disi |

---

## SPRINT 3 - SIRADAKI GOREVLER

### Gorev A - LLM Call Logger (Kisi 1, ~2 saat)
`app/infrastructure/llm_logger.py` olustur:
- Her LLM cagrisini logla: agent adi, senaryo, sure (ms), basari/fallback
- Python logging modulu - JSON degil, text log yeterli
- Yeni model baglandiginda karsilastirma icin kullanilacak
- Sprint 3 sonunda Streamlit'te gosterilecek

### Gorev B - ML Orkestrator (Kisi 2, ~1 hafta)
1. Sentetik veri uret (1000 senaryo simulasyonu)
2. Feature engineering: agent stance'larindan sayisal ozellikler cikar
3. scikit-learn (LogisticRegression veya RandomForest) ile egit
4. aggregator.py'i ML agirliklarini kullanacak sekilde guncelle

### Gorev C - Async DB Gecisi (Kisi 2, ~3 saat)
```python
# session.py - su an
engine = create_engine(DATABASE_URL)  # psycopg2, senkron

# Olmasi gereken
engine = create_async_engine(
    DATABASE_URL.replace("postgresql+psycopg2", "postgresql+asyncpg")
)
```
Repository'leri async/await ile guncelle.

### Gorev D - Streamlit Dashboard (Kisi 3, ~1 hafta)
- Senaryo girisi formu
- Agent tartisma akisi gorsellestirmesi (tur bazli)
- Final karar gosterimi (APPROVE/REVISE/REJECT)
- LLM log goruntuleyici

---

## DOKUNULMAYACAK SEYLER - KESIN KURAL

```python
# Bu satirlari/siniflari asla degistirme:

# models.py
@dataclass(frozen=True)
class AgentMessage:    # frozen - alan ekleyemezsin
    agent: str
    stance: Stance
    confidence: float
    reasoning: str
    metrics: dict
    round_number: int

@dataclass(frozen=True)
class ScenarioInput:   # frozen - alan ekleyemezsin

def to_legacy_result() # aggregator uyumlulugu icin sart

# aggregator.py
if average >= 75: APPROVE   # esikler sabittir
elif average >= 50: REVISE
else: REJECT

# factory.py
AgentFactory.create_default_agents()  # imzasi degismez
```

---

## TEST STRATEJISI

```bash
# Gunluk hizli kontrol - 0.25 saniye
pytest tests/test_aggregator.py tests/test_agent_message_schema.py tests/test_classifier.py -v

# PR oncesi tam suite - 6-7 dakika (Ollama acik olmali)
C:/anaconda3/Scripts/conda.exe run -p C:\Users\zaman\.conda\envs\sivecore python -m pytest tests/test_ceo_agent.py tests/test_cfo_agent.py tests/test_hr_agent.py -v --tb=short

# YAPMA: tum testleri conda olmadan calistirma
# pytest tests/ -v  <- bu 1 saat surer, Ollama her test icin cagrilir
```

---

## KOD STANDARTLARI

1. Type hints: `str | None` (Python 3.10+, Optional kullanma)
2. Docstring: Turkce aciklama tercih edilir
3. Import sirasi: stdlib -> third-party -> local
4. LLM system prompt'larinda her zaman: "You MUST respond in English only."
5. Her yeni metot icin en az 1 pytest testi
6. Logging: `logger.info` LLM oncesi, `logger.warning` fallback durumunda

---

## GIT WORKFLOW

```
main          <- sadece stabil, demo-ready kod
develop       <- sprint entegrasyon branch'i
|- feature/JIRA-01-env-setup-and-prompt-template  <- tamamlandi
|- feature/sprint3-ml-orchestrator               <- sirada (Kisi 2)
|- feature/sprint3-llm-logger                    <- sirada (Kisi 1)
\- feature/sprint3-streamlit-dashboard           <- sirada (Kisi 3)
```

Commit mesaji formati:
```
feat(JIRA-XX): kisa aciklama
fix(agents): Ingilizce system prompt duzeltmesi
test(ceo): dil bagimsiz assertion eklendi
```
