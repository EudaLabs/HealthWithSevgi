# Sprint 3 — Gap Analysis & Task List

> **Sprint Scope:** Steps 4 (Model & Parameters) – 5 (Results)
> **Due:** Wednesday, 1 April 2026, 12:00 AM
> **Analysis Date:** 2026-03-25

---

## Takim Dagilimi

| Takim | Uyeler | Alan |
|-------|--------|------|
| Takim 1 | Efe + Berat | Step 4: Model & Parameters |
| Takim 2 | Burak + Batuhan + Berfin | Step 5: Results |

| Ortak Gorev | Sorumlu |
|-------------|---------|
| Jira Sprint 3 Backlog | Berat + Efe |
| Test Report (PDF) | Berfin |
| Weekly Progress Report | Berfin |
| Domain Switching Testi | Her takim kendi adimi |

---

## Takim 1: Efe & Berat — Step 4 Eksikleri

### ZATEN TAMAM (kod yazilmis)
- [x] 8-Model Tab Bar (spec 6 istiyor, 8 var — OK)
- [x] Model Parameter Panel — tum 8 model icin slider/dropdown var
- [x] Clinical plain-language tooltips (PARAM_HINTS) her model icin
- [x] Auto-Retrain Toggle calisiyor (debounce suresi yanlis)
- [x] Backend: 8 model train/evaluate pipeline

### EKSIK #1 — KNN Scatter Canvas (KRITIK, P0)
- **Durum:** HIC YOK
- **Spec:** "KNN scatter canvas redraws on K change ≤ 16 ms"
- **Showcase:** "Instructor checks: KNN canvas redraw smoothness"
- **Ne Gerekli:** KNN secildiginde gorunen canvas-based 2D scatter plot. Data point'ler class'a gore renkli, K degistikce nearest neighbor'lar anlik yeniden cizilir. `requestAnimationFrame` kullanmali.
- **Efor:** BUYUK — yeni component
- **Sorumlu:** Efe veya Berat (kod)

### EKSIK #2 — Debounce Suresi: 500ms → 300ms (P1)
- **Durum:** YANLIS DEGER
- **Dosya:** `frontend/src/pages/Step4ModelParameters.tsx:201`
- **Simdiki:** `setTimeout(() => {...}, 500)`
- **Spec:** "300 ms ± 50 ms" (250–350ms arasi)
- **Efor:** Kucuk — tek satir
- **Sorumlu:** Efe veya Berat

### EKSIK #3 — Clinical Tooltip Review / Wiki Screenshots (P1)
- **Durum:** YOK
- **Ne Gerekli:** 8 modelin her birinin parametre panelinin screenshot'i, klinik tooltip'ler gorunur sekilde. GitHub Wiki'ye yukle.
- **Efor:** Manuel (screenshot + wiki)
- **Sorumlu:** Efe veya Berat

### EKSIK #4 — Step 4 Kendi Testleri (P1)
- **Ne Gerekli:** US-012, US-013, US-014, US-015 icin test case screenshot'lari (Berfin'e gonderilecek)
- **Sorumlu:** Efe + Berat (test calistirip screenshot alir)

---

## Takim 2: Burak, Batuhan & Berfin — Step 5 Eksikleri

### ZATEN TAMAM (kod yazilmis)
- [x] 6 metrik karti (Accuracy, Sensitivity, Specificity, Precision, F1, AUC-ROC)
- [x] Renk esikleri (green/amber/red) dogru calisiyor
- [x] Klinik yorum cumlesi her metrik icin mevcut (METRIC_DEFS.meaning)
- [x] Confusion Matrix — 2x2 binary + NxN multiclass, renk kodlamasi, plain labels
- [x] ROC Curve — Recharts SVG, diagonal cizgi, AUC annotation, aciklama notu
- [x] PR Curve (bonus — spec'te yok)
- [x] Low Sensitivity Danger Banner (`metrics.low_sensitivity_warning`)
- [x] Model Comparison Table — + Compare, AUC-ROC'a gore sirali, Sensitivity renkli, duplicate engelli
- [x] Cross-validation scores, overfitting warning, strengths/improvements

### EKSIK #5 — FN Red Banner + FP Info Banner (P1)
- **Durum:** KISMI — hucre icinde metin var, ayri banner yok
- **Spec:** "FN red banner; FP info banner"
- **Dosya:** `frontend/src/pages/Step5Results.tsx` (confusion matrix bolumunun altina)
- **Simdiki:** Hucrelerde "MISSED — most dangerous" ve "Unnecessary alarm" yazisi var
- **Ne Gerekli:** Confusion matrix'in altinda 2 ayri banner:
  - Kirmizi (danger): FN aciklamasi — "X patient was MISSED by the AI — missed cases are the most dangerous error in screening"
  - Mavi (info): FP aciklamasi — "X patient was flagged unnecessarily — causes extra tests but no direct harm"
  - FN ve FP sayilari dinamik olarak gosterilmeli
- **Efor:** Orta
- **Sorumlu:** Batuhan veya Burak

### EKSIK #6 — Step 5 onNext CTA Butonu (P2)
- **Durum:** Prop alinmis ama kullanilmiyor
- **Dosya:** `frontend/src/pages/Step5Results.tsx`
- **Ne Gerekli:** Sayfanin altinda "Continue to Explainability →" butonu
- **Efor:** Kucuk — 5 satir
- **Sorumlu:** Batuhan veya Burak

### EKSIK #7 — Step 5 Kendi Testleri (P1)
- **Ne Gerekli:** US-016, US-017, US-018, US-019 icin test case screenshot'lari (Berfin'e gonderilecek)
- **Sorumlu:** Burak + Batuhan (test calistirip screenshot alir)

---

## Berat & Efe — Jira Gorevleri

### EKSIK #8 — Sprint 3 Backlog Olusturma (P0)
- **Durum:** YAPILMAMIS — Jira hala Sprint 1 gorunuyor
- **Ne Gerekli:**
  1. Jira'da "Sprint 3" olustur
  2. Su story'leri Sprint 3'e tasi:
     - US-012: Select ML model type for training (Berat)
     - US-013: Tune model hyperparameters via interactive sliders (Berat)
     - US-014: Toggle auto-retrain on hyperparameter change (Berat)
     - US-015: Compare multiple trained models side by side (Berat)
     - US-016: View six performance metrics after model training (Efe)
     - US-017: View confusion matrix with plain clinical labelling (Efe)
     - US-018: View ROC curve for model discrimination ability (Efe)
     - US-019: Display low sensitivity warning banner automatically (Efe)
  3. Story point'leri ata
  4. Sub-task'lari olustur
  5. Burndown chart icin Jira sprint'i baslat
- **Efor:** Manuel (Jira UI)
- **Sorumlu:** Berat + Efe

---

## Berfin — Dokumantasyon Gorevleri

### EKSIK #9 — Test Report Sprint 3 (PDF) (P0)
- **Durum:** BASLANMAMIS — `docs/qa/sprint-3/` dizini bile yok
- **Ne Gerekli:**
  - Step 4 test case'leri (US-012 to US-015) — screenshot'lar Efe & Berat'tan gelecek
  - Step 5 test case'leri (US-016 to US-019) — screenshot'lar Burak & Batuhan'dan gelecek
  - Performance timing testleri: her model train < 3,000ms
  - Pass/fail status per story + evidence screenshot
  - PDF formatinda, GitHub Wiki'ye yukle
- **Efor:** Buyuk
- **Sorumlu:** Berfin (diger takimlardan screenshot toplama)

### EKSIK #10 — Weekly Progress Report (P0)
- **Durum:** BASLANMAMIS
- **Ne Gerekli:** Sprint 2 ile ayni yapi:
  - Header (group name, week, scrum master, date, domain count)
  - Burndown chart screenshot (Jira'dan)
  - Completed this week (story ID + title + points → Done)
  - In progress (story + % completion)
  - Blocked / at risk + resolution plan
  - Key decisions made (2-3 cumle)
  - Test results + evidence screenshots
  - Sprint 3 metrics tablosu
  - Next week plan (assignee'ler ile)
  - Retrospective note (even week ise: 1 Keep, 1 Improve, 1 Try)
- **Efor:** Orta
- **Sorumlu:** Berfin

---

## Ortak Test & Dogrulama Gorevleri

### TEST #11 — Tum Modeller Basariyla Egitiliyor mu? (P0)
- **Spec:** "Instructor gate: all 6 models must train successfully and all 6 metrics must update"
- **Ne Gerekli:** 8 modelin her birini egit, 6 metrik guncelleniyor mu kontrol et, screenshot al
- **Sorumlu:** Efe & Berat (Step 4 tarafinda), Burak & Batuhan (Step 5 tarafinda)

### TEST #12 — Domain Switching Testi (P1)
- **Spec:** "Switch domain, retrain, check metrics update — at least 5 domains tested"
- **Ne Gerekli:** 5+ farkli domain ile Step 4-5 akisini test et
- **Sorumlu:**
  - Step 4 tarafi: Efe & Berat (model parametreleri dogru reset oluyor mu?)
  - Step 5 tarafi: Burak & Batuhan (metrikler, confusion matrix, ROC dogru guncelleniyor mu?)

### TEST #13 — Model Training Latency (P1)
- **Spec:** "POST /api/train response time < 3,000 ms for dataset ≤ 50,000 rows"
- **Ne Gerekli:** DevTools Network tab ile her model icin response time olc
- **Sorumlu:** Berat (backend developer)

### TEST #14 — Metric Renk Esigi Boundary Testi (P1)
- **Spec:** "All 6 metrics tested at boundary values"
- **Esikler:**
  | Metrik | Green | Amber | Red |
  |--------|-------|-------|-----|
  | Accuracy | ≥ 65% | ≥ 55% | < 55% |
  | Sensitivity | ≥ 70% | ≥ 50% | < 50% |
  | Specificity | ≥ 65% | ≥ 55% | < 55% |
  | Precision | ≥ 60% | ≥ 50% | < 50% |
  | F1 | ≥ 65% | ≥ 55% | < 55% |
  | AUC-ROC | ≥ 75% | ≥ 65% | < 65% |
- **Sorumlu:** Burak & Batuhan (Step 5 UI tarafinda)

---

## Showcase Demo Checklist

> Week 5 Showcase — 5 min per group

- [ ] Jira Sprint 3 board + burndown chart goster (Berat)
- [ ] KNN train → metrics update → confusion matrix → ROC curve (Efe)
- [ ] Random Forest'a gec → + Compare → comparison table'da 2 model gozuksun (Efe)
- [ ] Low Sensitivity danger banner'i tetikle (yuksek K veya kotu split ile) (Batuhan)
- [ ] Instructor gate: 6+ model basariyla egitilsin, 6 metrik guncellensin (tum takim)
- [ ] Instructor check: KNN canvas redraw smoothness (Efe & Berat)
- [ ] Instructor check: klinik dilde tooltip'ler (Efe & Berat)

---

## Ozet: Kim Ne Yapacak?

### Efe (Step 4 Kod + Jira)
| # | Gorev | Oncelik | Durum |
|---|-------|---------|-------|
| 1 | KNN Scatter Canvas component | P0 | YOK |
| 2 | Jira Sprint 3 — Step 5 story'lerini olustur (US-016 to US-019) | P0 | YOK |
| 3 | Clinical Tooltip Review wiki sayfasi | P1 | YOK |
| 4 | Step 4 test screenshot'lari → Berfin'e gonder | P1 | YOK |

### Berat (Step 4 Kod + Jira + Backend)
| # | Gorev | Oncelik | Durum |
|---|-------|---------|-------|
| 1 | Debounce 500ms → 300ms fix | P1 | YANLIS DEGER |
| 2 | Jira Sprint 3 — Step 4 story'lerini olustur (US-012 to US-015) | P0 | YOK |
| 3 | KNN Scatter Canvas — backend data endpoint (eger gerekirse) | P0 | YOK |
| 4 | Model training latency testi | P1 | YOK |

### Batuhan (Step 5 Kod)
| # | Gorev | Oncelik | Durum |
|---|-------|---------|-------|
| 1 | FN Red Banner + FP Info Banner ekle | P1 | KISMI |
| 2 | Step 5 onNext CTA butonu ekle | P2 | EKSIK |
| 3 | Step 5 test screenshot'lari → Berfin'e gonder | P1 | YOK |
| 4 | Metric renk esigi boundary testi | P1 | YOK |

### Burak (Step 5 Kod)
| # | Gorev | Oncelik | Durum |
|---|-------|---------|-------|
| 1 | Domain switching testi (Step 5 tarafi, 5+ domain) | P1 | YOK |
| 2 | Step 5 test screenshot'lari → Berfin'e gonder | P1 | YOK |
| 3 | FN/FP banner'lari code review | P2 | YOK |

### Berfin (Dokumantasyon + QA)
| # | Gorev | Oncelik | Durum |
|---|-------|---------|-------|
| 1 | Test Report Sprint 3 PDF | P0 | BASLANMAMIS |
| 2 | Weekly Progress Report | P0 | BASLANMAMIS |
| 3 | Tum takimlardan screenshot toplama | P1 | YOK |
| 4 | `docs/qa/sprint-3/` dizini olustur | P1 | YOK |

---

## Zaten Tamam Olan Her Sey

- [x] 8-Model Tab Bar (spec 6 istiyor, 8 var — fazlasi iyi)
- [x] Model Parameter Panel — 8 model icin slider/dropdown/radio
- [x] Clinical PARAM_HINTS — her model icin klinik aciklama
- [x] Auto-Retrain Toggle calisiyor (debounce suresi fix gerekli)
- [x] Training results: 8 metrik karti + green/amber/red
- [x] Confusion Matrix: 2x2 binary + NxN multiclass, renk kodlu, plain labels
- [x] ROC Curve: SVG (Recharts), diagonal referans, AUC annotated, aciklama notu
- [x] PR Curve (bonus)
- [x] Low Sensitivity Danger Banner (< %50 tetiklenir)
- [x] Model Comparison Table: + Compare, AUC-ROC sirali, Sensitivity renkli, duplicate yok
- [x] Cross-validation fold scores
- [x] Overfitting warning
- [x] Backend: 8 model, train/evaluate pipeline, RandomizedSearchCV tuning, feature selection
- [x] Step 5: 6 buyuk metrik karti + klinik meaning + strengths/improvements
- [x] Training vs Test Accuracy karsilastirmasi
