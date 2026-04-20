# 🎯 Proje Durum Analizi ve Takım Görev Dağılımı

> **Tarih:** 11 Mart 2026  
> **Takım Büyüklüğü:** 3 Kişi

---

## 📊 MEVCUT DURUM ÖZETİ

### Proje Nedir?
**AI Decision Ecosystem Engine** - Şirketlerin stratejik kararlarını (yatırım, proje onayı vb.) değerlendiren **çok ajanlı karar destek sistemi**.

### Nasıl Çalışıyor?
```
┌─────────────────────────────────────────────────────────────────┐
│                         KARAR AKIŞI                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📥 SENARYO GİRİŞİ                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Proje Adı: "AI Platform Yatırımı"                     │   │
│  │ • Bütçe: 25 Milyon USD                                  │   │
│  │ • Beklenen ROI: %45                                     │   │
│  │ • Risk Seviyesi: 6/10                                   │   │
│  │ • Takım Hazırlığı: 7/10                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  🤖 ML SINIFLANDIRMA                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Senaryo Tipi: HIGH_GROWTH (Yüksek Büyüme)               │   │
│  │ Güven: %85                                              │   │
│  │ Önerilen Ağırlıklar: CEO %40 | CFO %35 | HR %25         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  🎭 AGENT ANALİZİ (Tur Tabanlı Tartışma)                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │   TUR 1: İlk Görüşler                                   │   │
│  │   ┌─────────┐   ┌─────────┐   ┌─────────┐              │   │
│  │   │   CEO   │   │   CFO   │   │    HR   │              │   │
│  │   │ SUPPORT │   │ NEUTRAL │   │ SUPPORT │              │   │
│  │   │  %80    │   │  %60    │   │  %75    │              │   │
│  │   └────┬────┘   └────┬────┘   └────┬────┘              │   │
│  │        │             │             │                    │   │
│  │        └─────────────┼─────────────┘                    │   │
│  │                      ▼                                  │   │
│  │   TUR 2: Birbirlerini Görerek Güncelleme                │   │
│  │   ┌─────────┐   ┌─────────┐   ┌─────────┐              │   │
│  │   │   CEO   │   │   CFO   │   │    HR   │              │   │
│  │   │ SUPPORT │   │ SUPPORT │   │ SUPPORT │              │   │
│  │   │  %85    │   │  %70    │   │  %80    │              │   │
│  │   └─────────┘   └─────────┘   └─────────┘              │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  📊 AĞIRLIKLI BİRLEŞTİRME                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Final Skor = (CEO_skor × 0.40) + (CFO_skor × 0.35) +    │   │
│  │              (HR_skor × 0.25)                            │   │
│  │                                                         │   │
│  │ Örnek: (78 × 0.40) + (68 × 0.35) + (82 × 0.25) = 75.5   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ✅ FİNAL KARAR                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │   ≥75 → 🟢 APPROVE (Onayla)                             │   │
│  │   50-74 → 🟡 REVISE (Revize Et)                         │   │
│  │   <50 → 🔴 REJECT (Reddet)                              │   │
│  │                                                         │   │
│  │   Bu Senaryo: 75.5 → 🟢 APPROVE                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ TAMAMLANAN İŞLER (SPRINT 1 & 2)

| Durum | Özellik / Görev | Detay / Açıklama |
|-------|----------------|------------------|
| ✅ | **Clean Architecture** | 4 Katmanlı temiz mimari (API, Application, Domain, Infrastructure). |
| ✅ | **Core Agent Sistemi** | CEO, CFO, HR agentları kural tabanlı (rule-based) mantıkla başarıyla kuruldu. |
| ✅ | **İletişim Protokolü** | `AgentMessage` standardı (stance, confidence, reasoning, metrics) oluşturuldu. |
| ✅ | **Round-Based Discussion** | 2 turlu tartışma, ajanın önceki tur mesajlarını okuma becerisi eklendi. |
| ✅ | **Veritabanı & Docker** | PostgreSQL + Alembic Migrations ve `docker-compose` eklendi. |
| ✅ | **REST API Endpointleri** | FastAPI ile tüm oluşturma ve okuma senaryoları uç noktaları aktif. |
| ✅ | **LLM Entegrasyon Temelleri** | Base Agent içerisine `qwen` için `system prompt` ve `fallback` mekanizması yazıldı. |
| ✅ | **Test Suite** | 92 test yazıldı, tamamı sorunsuz (`PASSED`) çalışıyor. |

---

## 🚧 YAPILACAKLAR / DEVAM EDEN İŞLER (SPRINT 3)
*Şu an üzerinde çalışmamız gereken aktif sprint görevleri:*

| Görev | Sorumlu | Tahmini Süre | Durum | Detay |
|-------|---------|--------------|-------|-------|
| **Görev A: LLM Call Logger** | Kişi 1 | ~2 Saat | ⏳ Yapılacak | `app/infrastructure/llm_logger.py` yazılacak. Süre, senaryo ve başarı durumu loglanacak. |
| **Görev B: ML Orchestrator** | Kişi 2 | ~1 Hafta | ⏳ Yapılacak | Rule-based (esik tabanlı) karardan scikit-learn tabanlı (RandomForest/Logistic) ağırlıklandırmaya geçiş. Sentetik veri üretimi eklenecek. |
| **Görev C: Async DB Geçişi** | Kişi 2 | ~3 Saat | ⏳ Yapılacak | `psycopg2` -> `asyncpg` dönüşümü. SQLAlchemy repoları `async/await` mimarisine refactor edilecek. |
| **Görev D: Streamlit Dashboard** | Kişi 3 | ~1 Hafta | ⏳ Yapılacak | Senaryo girme formlu, tartışmayı ve LLM loglarını gösteren frontend arayüzü yazılacak. |

---

## 📌 İLERİDE YAPILACAKLAR (SPRINT 4 - BACKLOG)

| Özellik | Tipi | Açıklama |
|---------|------|----------|
| **Uzun Süreli Hafıza (Long-Term Memory)** | Ar-Ge | Agent'ların önceki farklı simülasyonlardan öğrenmesi için Neo4j (Graph DB) entegrasyonu. Şu an kapsam dışı. |

---

### Mevcut Teknoloji Stack
```
Backend:     FastAPI + Uvicorn
Database:    PostgreSQL + SQLAlchemy + Alembic
ML:          Rule-based (scikit-learn'e hazır yapı)
Container:   Docker + Docker Compose
Test:        Pytest (86 test)
Frontend:    Vanilla HTML/CSS/JS
```

---

## ⚠️ KALAN İŞLER VE ZAYIF NOKTALAR

### 1️⃣ Agent Mimarisi - Zayıf Noktalar

| Sorun | Detay | Önem |
|-------|-------|------|
| **Statik Kurallar** | Agentlar sabit kural tabanlı, gerçek zeka yok | 🔴 Kritik |
| **LLM Eksikliği** | Hiçbir gerçek dil modeli entegre değil | 🔴 Kritik |
| **Hafıza Yok** | Agentlar geçmiş senaryoları hatırlamıyor | 🟡 Orta |
| **Sadece 3 Agent** | CEO, CFO, HR dışında agent yok | 🟢 Düşük |
| **Sınırlı Adaptasyon** | Round-based'de pozisyon değişimi sınırlı | 🟡 Orta |

### 2️⃣ ML Sistemi - Zayıf Noktalar

| Sorun | Detay | Önem |
|-------|-------|------|
| **Rule-Based** | Gerçek ML modeli eğitilmiş değil | 🔴 Kritik |
| **Yetersiz Veri** | Sadece 105 senaryo (minimum 500-1000 gerekli) | 🔴 Kritik |
| **Feature Engineering** | Basit normalizasyon, gelişmiş özellik yok | 🟡 Orta |
| **Model Doğrulama** | Cross-validation, A/B test yok | 🟡 Orta |
| **MLOps** | Model versiyonlama, pipeline yok | 🟡 Orta |

### 3️⃣ Genel Sistem - Zayıf Noktalar

| Sorun | Detay | Önem |
|-------|-------|------|
| **Basit Frontend** | Sadece HTML, modern framework yok | 🟡 Orta |
| **Rapor Eksikliği** | PDF/Excel export yok | 🟡 Orta |
| **Feedback Loop** | Karar sonuçları takip edilmiyor | 🟡 Orta |
| **CI/CD** | Otomatik deployment pipeline yok | 🟢 Düşük |
| **Monitoring** | Sistem izleme, alerting yok | 🟢 Düşük |

---

## 👥 3 KİŞİLİK TAKIM GÖREV DAĞILIMI

### Eşit İş Yükü Prensibi
Her takım üyesi için:
- **Sprint Süresi:** 2 hafta
- **Tahmini Efor:** ~40-50 saat/kişi
- **Zorluk Dengesi:** Benzer teknik karmaşıklık

---

## 🧑‍💻 TAKIM ÜYESİ 1: AGENT MİMARİ

### Rol: Agent Sistemini Akıllı Hale Getirmek

### Ana Görevler

| Görev | Açıklama | Tahmini Süre | Zorluk |
|-------|----------|--------------|--------|
| **LLM Entegrasyonu** | Ollama/GPT-4 API bağlantısı | 12-15 saat | 🔴 Zor |
| **Agent Hafızası** | Geçmiş senaryoları hatırlama sistemi | 8-10 saat | 🟡 Orta |
| **Yeni Agent Tipleri** | Legal Agent, Tech Agent ekleme | 6-8 saat | 🟡 Orta |
| **Gelişmiş Tartışma** | 3+ tur, dinamik sonlandırma | 6-8 saat | 🟡 Orta |
| **Agent Testleri** | Yeni özellikler için test yazımı | 4-5 saat | 🟢 Kolay |

### Teknik Detaylar

```
📁 Çalışacağı Dosyalar:
├── app/domain/agents/
│   ├── base.py          → LLM interface ekle
│   ├── ceo_agent.py     → LLM kullanacak şekilde güncelle
│   ├── cfo_agent.py     → LLM kullanacak şekilde güncelle
│   ├── hr_agent.py      → LLM kullanacak şekilde güncelle
│   ├── legal_agent.py   → YENİ: Hukuk perspektifi
│   ├── tech_agent.py    → YENİ: Teknik perspektif
│   └── memory.py        → YENİ: Agent hafıza sistemi
├── app/infrastructure/
│   └── llm/
│       ├── base.py      → YENİ: LLM interface
│       ├── ollama.py    → YENİ: Ollama client
│       └── openai.py    → YENİ: OpenAI client
└── tests/
    ├── test_llm_integration.py
    └── test_agent_memory.py
```

### Beklenen Çıktılar
1. ✅ Çalışan Ollama entegrasyonu
2. ✅ En az 1 yeni agent tipi
3. ✅ Agent hafıza sistemi (son N senaryoyu hatırla)
4. ✅ %80+ test coverage

### Başarı Kriterleri
- [ ] Agent'lar gerçek LLM ile analiz yapabilmeli
- [ ] Hafıza sistemi çalışıyor olmalı
- [ ] Yeni agent entegre ve test edilmiş olmalı
- [ ] Mevcut testler geçmeli + yeni testler eklenmeli

---

## 📊 TAKIM ÜYESİ 2: ML ORCHESTRATOR

### Rol: Gerçek ML Pipeline Kurmak

### Ana Görevler

| Görev | Açıklama | Tahmini Süre | Zorluk |
|-------|----------|--------------|--------|
| **Veri Toplama** | Kaggle'dan uygun dataset indirme | 4-6 saat | 🟢 Kolay |
| **Veri Dönüşümü** | Harici veriyi projemize uyarlama | 8-10 saat | 🟡 Orta |
| **Feature Engineering** | Gelişmiş özellik çıkarımı | 8-10 saat | 🔴 Zor |
| **Model Eğitimi** | RandomForest/XGBoost/Neural Network | 10-12 saat | 🔴 Zor |
| **Model Entegrasyonu** | Eğitilmiş modeli sisteme entegre et | 6-8 saat | 🟡 Orta |
| **Performans Raporu** | Accuracy, F1, Confusion Matrix | 4-5 saat | 🟢 Kolay |

### Teknik Detaylar

```
📁 Çalışacağı Dosyalar:
├── ml/                           → YENİ KLASÖR
│   ├── data/
│   │   ├── raw/                  → Ham veri setleri
│   │   ├── processed/            → İşlenmiş veri
│   │   └── data_transformer.py   → Dönüşüm scripti
│   ├── models/
│   │   ├── classifier_v1.pkl     → Eğitilmiş model
│   │   └── model_config.yaml     → Model parametreleri
│   ├── notebooks/
│   │   ├── 01_data_exploration.ipynb
│   │   ├── 02_feature_engineering.ipynb
│   │   └── 03_model_training.ipynb
│   ├── training/
│   │   ├── train.py              → Eğitim scripti
│   │   └── evaluate.py           → Değerlendirme
│   └── requirements_ml.txt       → ML bağımlılıkları
├── app/domain/services/
│   └── classifier.py             → Gerçek ML modeli çağıracak
└── tests/
    └── test_ml_model.py
```

### Kullanılacak Veri Setleri (Öncelik Sırasıyla)

| # | Dataset | Kaynak | Boyut | Uygunluk |
|---|---------|--------|-------|----------|
| 1 | IT Project Management | Kaggle | ~2,000 | ⭐⭐⭐⭐⭐ |
| 2 | Startup Investments | Kaggle | ~50,000 | ⭐⭐⭐⭐ |
| 3 | Company Investment Decisions | Kaggle | ~5,000 | ⭐⭐⭐⭐⭐ |
| 4 | Credit Approval | UCI | ~690 | ⭐⭐⭐⭐ |

### Veri Dönüşüm Mapping
```python
# Harici veri → Bizim format
{
    "investment_amount": "budget_million_usd",
    "expected_return": "expected_roi_percent", 
    "risk_score": "risk_level",        # 1-10 ölçek
    "team_size": "team_readiness",     # 1-10 ölçek
    "project_status": "scenario_type"  # 5 sınıf
}
```

### Beklenen Çıktılar
1. ✅ Minimum 1000+ kayıtlık temiz veri seti
2. ✅ Eğitilmiş ML modeli (Accuracy ≥ %75)
3. ✅ Feature importance analizi
4. ✅ Model performans raporu
5. ✅ Entegre çalışan classifier

### Başarı Kriterleri
- [ ] Model accuracy ≥ %75
- [ ] F1-score (macro) ≥ 0.70
- [ ] Cross-validation yapılmış
- [ ] Model sisteme entegre ve test edilmiş
- [ ] Performans raporu hazır

---

## 🎨 TAKIM ÜYESİ 3: FULL-STACK / DEVOPS

### Rol: Frontend, API Genişletme ve DevOps

### Ana Görevler

| Görev | Açıklama | Tahmini Süre | Zorluk |
|-------|----------|--------------|--------|
| **React Dashboard** | Modern SPA dashboard geliştirme | 12-15 saat | 🔴 Zor |
| **API Genişletme** | Batch simülasyon, export endpoint'leri | 6-8 saat | 🟡 Orta |
| **Rapor Sistemi** | PDF/Excel export özelliği | 6-8 saat | 🟡 Orta |
| **CI/CD Pipeline** | GitHub Actions, otomatik test/deploy | 6-8 saat | 🟡 Orta |
| **Monitoring** | Logging, health check, alerting | 4-6 saat | 🟡 Orta |
| **Dokümantasyon** | API docs, kullanım kılavuzu | 4-5 saat | 🟢 Kolay |

### Teknik Detaylar

```
📁 Çalışacağı Dosyalar:
├── frontend/                     → YENİ KLASÖR (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ScenarioForm.tsx
│   │   │   ├── SimulationResult.tsx
│   │   │   └── AgentCard.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   └── History.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── app/presentation/api/v1/routes/
│   └── scenarios.py              → Yeni endpoint'ler ekle
├── app/infrastructure/
│   └── export/
│       ├── pdf_generator.py      → YENİ
│       └── excel_generator.py    → YENİ
├── .github/workflows/
│   ├── test.yml                  → CI pipeline
│   └── deploy.yml                → CD pipeline
└── docs/
    ├── API_REFERENCE.md          → Detaylı API dokümantasyonu
    └── USER_GUIDE.md             → Kullanıcı kılavuzu
```

### Yeni API Endpoint'leri

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/api/v1/scenarios/batch` | Toplu senaryo oluşturma |
| POST | `/api/v1/scenarios/batch-simulate` | Toplu simülasyon |
| GET | `/api/v1/scenarios/{id}/export/pdf` | PDF rapor |
| GET | `/api/v1/scenarios/{id}/export/excel` | Excel rapor |
| GET | `/api/v1/analytics/summary` | Genel istatistikler |
| GET | `/api/v1/health/detailed` | Detaylı sistem durumu |

### Frontend Özellikleri
- React + TypeScript + Vite
- TailwindCSS styling
- Recharts grafikleri
- Axios API client
- React Query caching

### Beklenen Çıktılar
1. ✅ Çalışan React dashboard
2. ✅ PDF/Excel export fonksiyonalitesi
3. ✅ GitHub Actions CI/CD
4. ✅ Güncel API dokümantasyonu
5. ✅ Kullanıcı kılavuzu

### Başarı Kriterleri
- [ ] Dashboard tüm endpoint'lerle çalışıyor
- [ ] Export özellikleri fonksiyonel
- [ ] CI: Her PR'da testler çalışıyor
- [ ] CD: main branch'e push'ta deploy
- [ ] Dokümantasyon güncel ve kapsamlı

---

## 📅 SPRINT PLANI

### Sprint 1 (Hafta 1-2)

```
┌──────────────────┬──────────────────┬──────────────────┐
│   AGENT MİMARI   │  ML ORCHESTRATOR │   FULL-STACK     │
├──────────────────┼──────────────────┼──────────────────┤
│ Hafta 1:         │ Hafta 1:         │ Hafta 1:         │
│ • LLM interface  │ • Veri toplama   │ • React setup    │
│ • Ollama setup   │ • Veri temizleme │ • Component'ler  │
│ • CEO agent LLM  │ • EDA notebook   │ • API client     │
│                  │                  │                  │
│ Hafta 2:         │ Hafta 2:         │ Hafta 2:         │
│ • CFO, HR LLM    │ • Feature eng.   │ • Dashboard UI   │
│ • Agent hafızası │ • Model eğitimi  │ • Export API     │
│ • Yeni agent     │ • Entegrasyon    │ • CI/CD setup    │
└──────────────────┴──────────────────┴──────────────────┘
```

### Günlük Sync (15 dk)
- Dün ne yaptım?
- Bugün ne yapacağım?
- Blocker var mı?

### Haftalık Review
- Demo gösterimi
- Kod review
- Sonraki hafta planı

---

## 🔗 BAĞIMLILIKLAR

```
               ┌─────────────────┐
               │  ML ORCHESTATOR │
               │   (Model .pkl)  │
               └────────┬────────┘
                        │ Model dosyası
                        ▼
┌──────────────────────────────────────────────────────┐
│                 AGENT MİMARİ                         │
│  (LLM + Memory + New Agents + Classifier kullanır)  │
└──────────────────────────┬───────────────────────────┘
                           │ API endpoint'leri
                           ▼
               ┌─────────────────┐
               │   FULL-STACK    │
               │ (Dashboard API) │
               └─────────────────┘
```

### Kritik Bağımlılıklar
1. **ML → Agent**: Classifier için eğitilmiş model gerekli
2. **Agent → Full-Stack**: Yeni endpoint'ler dashboard'da kullanılacak
3. **Ortak**: Database schema değişiklikleri koordineli yapılmalı

---

## ✅ SONUÇ: İŞ YÜKÜ KARŞILAŞTIRMASI

| Kriter | Agent Mimarı | ML Orchestrator | Full-Stack |
|--------|--------------|-----------------|------------|
| **Tahmini Saat** | 40-45 | 42-48 | 40-46 |
| **Teknik Zorluk** | Yüksek | Yüksek | Orta-Yüksek |
| **Öğrenme Eğrisi** | Orta (LLM) | Yüksek (ML) | Yüksek (React) |
| **Bağımsız Çalışma** | %70 | %80 | %75 |
| **Test Yazımı** | Evet | Evet | Evet |
| **Dokümantasyon** | Az | Orta | Çok |

### Dengeli Dağılım ✅
- Her kişi farklı domain'de uzmanlaşıyor
- Benzer zorluk ve süre
- Paralel çalışma mümkün
- Net sorumluluk alanları

---

x