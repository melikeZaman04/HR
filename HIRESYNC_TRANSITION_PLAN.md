# HireSync AI - Geçiş Planı ve Mevcut Durum Raporu

## 📌 Mevcut Durum (Neredeyiz?)
Eski proje olan BMU326 Multi-Agent Karar Destek Sistemi'nden **HireSync AI** projesine geçişimizin ilk aşamasını tamamladık. Şu ana kadar yaptıklarımız:

1. **Domain Veri Modelleri Güncellendi (`models.py`)** 
   - Eski finansal yatırım senaryosundan (CEO/CFO), insan kaynakları işe alım formülüne geçtik.
   - Yeni veri alanlarımız sisteme eklendi: `candidate_name`, `applied_role`, `experience_years`, `tech_test_score`, `avg_months_per_job`, `glassdoor_score`, `expected_salary`.
2. **API ve Response Şemaları Taşındı (`schemas/scenario.py`)**
   - FastAPI Rest uçlarında aday verisinin akışını sağlamak için Pydantic DTO (Data Transfer Object) şemalarını yeniledik.
3. **Veritabanı Yapısı Çizildi (`scenario_repository.py` & `database/models.py`)**
   - SQLAlchemy SQLAlchemyORM yapısında adaya ait sütunlar yaratıldı.
4. **Test Suitlerindeki Hatalar Ayıklandı**
   - Mock/Fake servislerde hâlâ eski alanları (`name`, `budget_million_usd`) kullanan test servisleri `Ahmet Yılmaz`, `Backend Developer` vb. mock datalarla revize edildi. Bütün testler şu an yeşil yanıyor.
5. **Agent Dosya İsimleri Localde Taşındı**
   - `ceo_agent.py` ➔ `strategy_agent.py`
   - `hr_agent.py` ➔ `culture_agent.py`
   - `cfo_agent.py` ➔ `salary_agent.py`

---

## 🤖 Ajanların Yeni Kimlikleri (Henüz Kodlanmadı, Yol Haritamız)
Dosya isimlerini güncelledik ancak içlerindeki sınıflar hâlâ (eski adıyla) çalışıyor. Ajanlarımızın yeni kimlikleri ve Katman 1 (Matematik) / Katman 2 (LLM Açıklaması) sorumlulukları şunlar olacak:

### 1. Strategy Agent (Strateji ve Yetenek Uzmanı)
- **Karakter:** Acımasız, teknik odaklı ve şirketin vizyonunu kovalayan bir teknoloji lideri (CTO mentalitesi).
- **Matematik (Katman 1):** `tech_test_score` ile `experience_years` arasındaki korelasyona bakar. Yüksek deneyimli ama test skoru çok düşük birine tolerans göstermez (Oppose verir).
- **LLM Yorumu (Katman 2):** "Adayın 5 yıllık deneyimine rağmen teknik testten 65 alması, sistem tasarımı konusunda zayıf olduğunu gösteriyor. Ancak..."

### 2. Culture Agent (Kültür ve Sadakat Uzmanı)
- **Karakter:** İnsan odaklı, şirketteki uyuma, adayın istikrarlılığına değer veren bir İnsan Kaynakları Direktörü.
- **Matematik (Katman 1):** Adayın ortalama iş değiştirme süresine (`avg_months_per_job`) ve bir önceki şirketinin Glassdoor skoruna (`glassdoor_score`) bakar. Sürekli iş değiştiren (Job Hopper) adaya güven puanını düşük verir.
- **LLM Yorumu (Katman 2):** "Adayın son 3 yılda 4 şirket değiştirmesi yüksek churn (elde tutamama) riskine işaret ediyor. Glassdoor puanının 4.2 olduğu nezih bir ortamdan bile ayrılmış."

### 3. Salary Agent (Maaş ve Bütçe Uzmanı)
- **Karakter:** Rasyonel, piyasa gerçekliklerinin farkında ve şirket bütçesini savunan bir CFO/Finans Lideri.
- **Matematik (Katman 1):** Adayın `expected_salary` (beklenen maaşı) değerini, o rol (`applied_role`) ve deneyim yılı için sektör bandıyla (şimdilik statik bir formül) karşılaştırır.
- **LLM Yorumu (Katman 2):** "Backend Developer için 90.000 TL maaş beklentisi 5 yıllık tecrübe için makul, ancak şirket bütçe bandımızın üst sınırında."

---

## 🛠️ GitHub PR ve Git Akışı (Gelecek Planı)
Projede temiz bir GitHub geçmişi oluşturmak ve ekip olarak çalışmak için uygulanacak Git Workflow adımları:

### Adım 1: Migration Issue'su & PR (Şu anki Hedef)
Alembic ile Postgres üzerinde yeni sütunları yaratmamız şart. 
- **Branch:** `feature/database-migration`
- **İçerik:** `alembic revision --autogenerate` ile DB şeması yenilenir.
- **PR:** "Veritabanı tablolarının yeni CV parametrelerine uyarlanması"

### Adım 2: Ajan Refactoring Issue'su & PR (Bir Sonraki Hedef)
- **Branch:** `feature/agent-identities`
- **İçerik:** `strategy_agent.py`, `culture_agent.py` ve `salary_agent.py` içindeki eski isimleri ve mantığı silip, yukarıdaki HR kurallarını kodlamak. İngilizce Promptların LLM'e uyarlanması. `test_*.py` testlerinin yazılması.
- **PR:** "Ajan mantığının HireSync AI senaryosuna göre baştan yazılması"

### Adım 3: Soru Üretici Ajan Issue'su & PR (Ekstra)
- **Branch:** `feature/question-agent`
- **İçerik:** `question_agent.py` dosyasının yaratılması. LLM entegreli olarak diğer 3 ajanın çıktılarını okuyup, 8-10 Türkçe spesifik mülakat sorusu üretecek tek fonksiyonlu bir LLM yapısı.
- **PR:** "Soru üreten 4. Ajan eklendi"

### Adım 4: Frontend / Dashboard Bağlantısı
- **Branch:** `feature/api-integration`
- Yukarıdaki ajanların konsensüs (`aggregator.py`) kararlarını (`MÜLAKATA AL`, `BEKLET`, `REDDET`) frontend Next.js paneline iletmek için entegrasyonlar.

### Git Kullanımında En İyi Yöntem:
Artık `main` veya `develop` dalına doğrudan kod atmayalım. Bu notları okuduktan sonra benimle her adımda şu komutları uygulayacağız:
1. `git checkout -b feature/agent-identities`
2. Kodu yaz ve test et (`pytest`)
3. `git commit -m "feat(agents): update agent reasoning logic"`
4. Sonra GitHub'da PR aç. Ben (yapay zeka) senin adına PR mantığını da hazırlayabilirim.

---
**Bekleyen Onay:** Hazırsan GitHub Branch'ini (`feature/agent-identities`) açıp `strategy_agent.py` dosyasının içindeki mantığı yenilemeye başlayalım.