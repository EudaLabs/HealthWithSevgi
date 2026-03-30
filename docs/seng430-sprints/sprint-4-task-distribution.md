# Sprint 4 — Gorev Dagitimi & Zaman Plani

> **Proje:** HealthWithSevgi — SENG 430
> **Sprint 4 Scope:** Steps 6 (Explainability) & 7 (Ethics & Bias)
> **Deadline:** 15 Nisan 2026, 13:00
> **Calismaya baslama:** 31 Mart 2026
> **Toplam sure:** 3 gun (31 Mart – 2 Nisan)
> **Hazirlayan:** Batuhan

---

## Takim

| Kisaltma | Isim | Sorumluluk Alani |
|----------|------|------------------|
| **BE** | Berat + Efe | Backend + ML (Python / FastAPI) |
| **FE** | Batu + Burak | Frontend (React/TS) + GitHub + Wiki |
| **RP** | Berfin | Raporlar + Screenshots + Test Report |

---

## 1. Eksik Listesi (Spec vs Codebase)

### 1.1 What-If Banner — TAMAMEN EKSIK (Kritik)

| | Detay |
|---|---|
| **Spec** | "blue what-if banner with probability shift" |
| **Showcase** | "Show what-if info banner changing probability" |
| **Mevcut durum** | Step 6'da boyle bir ozellik yok — ne backend endpointi ne frontend componenti |
| **Neden kritik** | Week 9 demo agenda'sinda acikca isteniyor |
| **Backend (BE)** | Yeni endpoint: `GET /api/explain/whatif/{model_id}/{patient_index}?feature={name}&value={new_value}`. Modeli secilen feature icin yeni degerle calistirip `{original_prob, new_prob, shift_pp, feature_name, original_value, new_value}` dondur. `ExplainService`'e `whatif()` metodu ekle — hastanin feature vektorunu kopyala, secilen feature'u degistir, `model.predict_proba()` calistir |
| **Frontend (FE)** | Step 6 sayfasina mavi `alert-info` banner ekle. Icerisinde: feature dropdown (global importance'daki top 5 feature), yeni deger input, "Simulate" butonu. Sonuc: "If [Clinical Name] changed from [old] to [new], the predicted probability would shift from X% to Y% (±Z pp)" |
| **Schema (BE)** | `explain_schemas.py`'e `WhatIfResponse(BaseModel)` ekle: `model_id, patient_index, feature_name, clinical_name, original_value, new_value, original_probability, new_probability, shift_pp` |

---

### 1.2 Patient Selector — YANLIS FORMAT

| | Detay |
|---|---|
| **Spec** | "dropdown with 3 test patients" |
| **Mevcut durum** | `Step6Explainability.tsx:228` — `<input type="number" min={1} max={testSize}>` serbest sayi girisi |
| **Neden yanlis** | Spec acikca "dropdown" ve "3 test patients" diyor; kullanici testSize kadar hasta arasinda secim yapiyor |
| **Backend (BE)** | Global explainability response'a `sample_patients` alani ekle: test setinden 3 hasta sec (dusuk/orta/yuksek risk). Her biri: `{index, predicted_class, probability, summary}`. Secim kriterleri: prob < 0.3 (low), 0.4-0.6 (mid), > 0.7 (high) |
| **Frontend (FE)** | `<input type="number">` yerine `<select>` dropdown. Her option: "Patient #12 — Diabetic (82.3% probability)". Secim degisince otomatik `fetchPatientExplanation` cagir |

---

### 1.3 Case Study Kartlari — RENK KODLAMASI YANLIS

| | Detay |
|---|---|
| **Spec** | "3 cards: **red** failure, **amber** near-miss, **green** prevention" |
| **Mevcut durum** | `Step7Ethics.tsx:283` — 3 karttin hepsi ayni: `borderLeft: '4px solid var(--danger)'` (kirmizi) ve `badge-danger` |
| **Neden yanlis** | Spec 3 farkli renk istiyor; her kartin tipi farkli olmali |
| **Backend (BE)** | `ethics_service.py` CASE_STUDIES listesindeki her item'a `"severity"` alani ekle: Pulse Ox → `"failure"`, Sepsis Alert → `"near_miss"`, Dermatology AI → `"prevention"`. `EthicsResponse` schema'da `case_studies` tipini `list[dict]`'ten structured `CaseStudy` modeline cevir |
| **Frontend (FE)** | `severity` degerine gore: `failure` → `var(--danger)` kirmizi border + `badge-danger`, `near_miss` → `var(--warning)` / `#b36800` amber border + `badge-warning`, `prevention` → `var(--success)` yesil border + `badge-success` |

---

### 1.4 Training Data Chart — >15pp Uyari EKSIK

| | Detay |
|---|---|
| **Spec** | "amber warning if >15pp gap" |
| **Mevcut durum** | `Step7Ethics.tsx:255-272` — Bar chart var ama hicbir uyari gosterilmiyor |
| **Backend (BE)** | `_training_representation()` donus degerine `warnings: list[str]` ekle. Her kategori (Male, Female, 18-60, vs.) icin `abs(dataset - population_norm) > 15` kontrolu yap. Ornek: `"Female representation (38.2%) differs from population norm (50.0%) by 11.8pp — exceeds 15pp threshold"` |
| **Frontend (FE)** | Chart altina amber `alert-warning` ekle: backend'den gelen her warning icin bir satir goster. Warning yoksa alert gosterme |

---

### 1.5 Certificate Endpoint Path — SPEC ILE UYUMSUZ

| | Detay |
|---|---|
| **Spec** | `POST /api/generate-certificate` |
| **Mevcut durum** | `explain_router.py:110` → `@router.post("/certificate")` yani `/api/certificate` |
| **Backend (BE)** | `explain_router.py:110`'da `"/certificate"` → `"/generate-certificate"` olarak degistir |
| **Frontend (FE)** | `frontend/src/api/explain.ts:26`'da `'/certificate'` → `'/generate-certificate'` olarak degistir |

---

### 1.6 Subgroup Table "Fairness" Kolonu — ISIM UYUMSUZ

| | Detay |
|---|---|
| **Spec** | "Fairness column with OK/Review/⚠" |
| **Mevcut durum** | `Step7Ethics.tsx:158` — Kolon basligi "Status", degerler "✓ acceptable / ⚠ review / ✗ action needed" |
| **Frontend (FE)** | `<th>Status</th>` → `<th>Fairness</th>`. Deger label'lari: `acceptable` → "OK", `review` → "Review", `action_needed` → "⚠ Action Needed" |

---

### 1.7 Step 6 — "Continue to Step 7" CTA Butonu YOK

| | Detay |
|---|---|
| **Spec** | Sprint 3'te Step 5'e eklenen gibi in-page CTA bekleniyor |
| **Mevcut durum** | `Step6Explainability.tsx` — `onNext` prop alinip JSX'te hic kullanilmiyor. BottomNav ile gezinme calisiyor ama sayfa icerisinde belirgin bir "Devam" butonu yok |
| **Frontend (FE)** | Sayfa sonuna (bottom reminder alert'ten once) buton ekle: `<button className="btn btn-primary btn-lg" onClick={onNext}>Continue to Step 7 — Ethics & Bias →</button>` |

---

### 1.8 Backend Testleri — HICBIRI YOK

| | Detay |
|---|---|
| **Spec** | Sprint 4 metrics: "End-to-End Flow", "Certificate Content", "Bias Detection Accuracy", "Checklist Toggle" |
| **Mevcut durum** | `tests/` klasorunde Step 6/7 ile ilgili hicbir test dosyasi yok |
| **Backend (BE)** | Minimum test kapsamı: |

**Gerekli testler:**

| Test dosyasi | Test case'ler |
|---|---|
| `test_step6_explainability.py` | `test_global_importance_returns_features`, `test_global_importance_clinical_names`, `test_global_importance_sorted_descending`, `test_global_importance_values_0_to_1`, `test_single_patient_valid_index`, `test_single_patient_invalid_index_422`, `test_whatif_changes_probability` |
| `test_step7_ethics.py` | `test_ethics_returns_subgroups`, `test_bias_detection_10pp_hidden`, `test_bias_detection_11pp_shown`, `test_checklist_8_items`, `test_checklist_2_prechecked`, `test_checklist_toggle`, `test_training_representation_has_gender` |
| `test_certificate.py` | `test_certificate_returns_pdf`, `test_certificate_content_type`, `test_certificate_under_10_seconds`, `test_certificate_3_domains` |

---

### 1.9 GitHub Wiki Eksikleri

| Sayfa | Durum | Aciklama |
|---|---|---|
| `Sprint-3.md` | EKSIK | Sprint-1/2 formatinda Sprint 3 ozeti |
| `Sprint-4.md` | EKSIK | Sprint 4 ozeti |
| `Domain-Clinical-Review.md` | EKSIK | 20 domain tablosu: Domain \| Top Feature \| Clinical Justification |
| Full Pipeline Test Report (PDF) | EKSIK | Steps 1-7 end-to-end CSV ile test |
| Weekly Progress Report (PDF) | EKSIK | Velocity, demo screenshots, Sprint 5 carryovers |

---

### 1.10 Sprint 4 Screenshot Report — YOK

| | Detay |
|---|---|
| **Mevcut durum** | `docs/reports/` icinde Sprint 2 ve Sprint 3 raporu var, Sprint 4 yok |
| **Gereken** | Step 6 + Step 7 tum UI ekran goruntuleri, certificate PDF ornekleri, 3 farkli domain ile demo |

---

## 2. Gorev Atama Tablosu

### BERAT + EFE (Backend)

| ID | Gorev | Ilgili Eksik | Dosya(lar) | Tahmini Sure |
|----|-------|-------------|------------|-------------|
| BE-1 | What-If endpoint + service metodu | 1.1 | `explain_service.py`, `explain_router.py`, `explain_schemas.py` | 3-4 saat |
| BE-2 | Sample patients (3 hasta secimi) | 1.2 | `explain_service.py`, `explain_schemas.py` | 1-2 saat |
| BE-3 | Case study severity alani | 1.3 | `ethics_service.py`, `explain_schemas.py` | 30 dk |
| BE-4 | Training data >15pp warnings | 1.4 | `ethics_service.py`, `explain_schemas.py` | 1 saat |
| BE-5 | Certificate endpoint rename | 1.5 | `explain_router.py:110` | 5 dk |
| BE-6 | Backend testleri (3 dosya) | 1.8 | `tests/test_step6_*.py`, `tests/test_step7_*.py`, `tests/test_certificate.py` | 3-4 saat |

---

### BATU + BURAK (Frontend + GitHub + Wiki)

| ID | Gorev | Ilgili Eksik | Dosya(lar) | Tahmini Sure | Bagimlilik |
|----|-------|-------------|------------|-------------|-----------|
| FE-1 | What-If banner UI | 1.1 | `Step6Explainability.tsx`, `api/explain.ts`, `types/index.ts` | 2-3 saat | BE-1 bitmeli |
| FE-2 | Patient dropdown (3 hasta) | 1.2 | `Step6Explainability.tsx` | 1 saat | BE-2 bitmeli |
| FE-3 | Case study kart renkleri | 1.3 | `Step7Ethics.tsx:282-327` | 30 dk | BE-3 bitmeli |
| FE-4 | Training data >15pp uyari | 1.4 | `Step7Ethics.tsx:255-272` | 30 dk | BE-4 bitmeli |
| FE-5 | Fairness kolon ismi | 1.6 | `Step7Ethics.tsx:158` | 10 dk | — |
| FE-6 | Certificate path rename | 1.5 | `api/explain.ts:26` | 5 dk | BE-5 ile esanli |
| FE-7 | Step 6 onNext CTA butonu | 1.7 | `Step6Explainability.tsx` | 15 dk | — |
| FE-8 | Wiki: Sprint-3 sayfasi | 1.9 | GitHub Wiki | 1 saat | — |
| FE-9 | Wiki: Sprint-4 sayfasi | 1.9 | GitHub Wiki | 1 saat | — |
| FE-10 | Wiki: Domain Clinical Review | 1.9 | GitHub Wiki | 2 saat | — |
| FE-11 | Wiki: Pipeline Test Report PDF | 1.9 | GitHub Wiki | 1.5 saat | Tum kod bitmeli |

---

### BERFIN (Raporlar)

| ID | Gorev | Ilgili Eksik | Format | Tahmini Sure | Bagimlilik |
|----|-------|-------------|--------|-------------|-----------|
| RP-1 | Sprint 4 Screenshot Report | 1.10 | PDF/DOCX → `docs/reports/` | 3 saat | Tum FE bitmeli |
| RP-2 | Weekly Progress Report | 1.9 | PDF → GitHub Wiki | 2 saat | — |
| RP-3 | Full Pipeline Test Report | 1.9 | PDF → GitHub Wiki | 3 saat | Tum kod bitmeli |
| RP-4 | 3 Domain Certificate Testi | Sprint metric | Screenshots | 1 saat | Tum kod bitmeli |

---

## 3. WBS / Gantt — 3 Gunluk Plan

```
GOREV               SORUMLU    GUN 1 (31 Mart)     GUN 2 (1 Nisan)     GUN 3 (2 Nisan)
                               AM    PM             AM    PM             AM    PM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BE-1 What-If EP      Berat+Efe ████████████████
BE-2 Sample Patients  Berat+Efe                 ████████
BE-3 Case Severity    Berat+Efe                     ████
BE-4 >15pp Warnings   Berat+Efe                     ████████
BE-5 EP Rename        Berat+Efe                         ██
BE-6 Backend Tests    Berat+Efe                              ████████████████████████
                                ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
FE-5 Fairness Kolon   Batu+Brk ██
FE-7 Step6 CTA        Batu+Brk ████
FE-6 EP Path Rename   Batu+Brk ████
FE-8 Wiki Sprint-3    Batu+Brk     ████████
FE-9 Wiki Sprint-4    Batu+Brk             ████████
FE-10 Wiki Domain Rev Batu+Brk                          ████████████
                               ─ ─ ── BEKLE: BE-1,2,3,4 ── ─ ─ ─
FE-1 What-If Banner   Batu+Brk                              ████████████
FE-2 Patient Dropdown Batu+Brk                                   ████████
FE-3 Case Renkleri    Batu+Brk                                       ████
FE-4 >15pp Uyari      Batu+Brk                                       ████
FE-11 Pipeline Report Batu+Brk                                           ████
                                ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
RP-2 Progress Report   Berfin  ████████████████████████
                               ─ ─ ── BEKLE: Tum kod ── ─ ─ ─ ─
RP-1 Screenshot Report Berfin                                ████████████████████████
RP-3 Pipeline Test     Berfin                                ████████████████████████
RP-4 3 Domain Cert     Berfin                                            ████████████
```

---

## 4. Gun Bazli Detayli Plan

### GUN 1 — 31 Mart (Pazartesi)

#### Berat + Efe
| Saat | Gorev | Teslim |
|------|-------|--------|
| 09:00–13:00 | **BE-1** What-If endpoint: `WhatIfResponse` schema, `ExplainService.whatif()` metodu, `GET /api/explain/whatif/{model_id}/{patient_index}` router | Endpoint calisiyor, Postman/curl ile test edilmis |
| 14:00–16:00 | **BE-1** devam — edge case'ler (invalid feature name, scaler inverse transform) | PR-ready |
| 16:00–18:00 | **BE-2** Sample patients: global response'a `sample_patients` alani, 3 hasta secme mantigi (low/mid/high risk) | Global endpoint guncellenmis |

#### Batu + Burak
| Saat | Gorev | Teslim |
|------|-------|--------|
| 09:00–09:15 | **FE-5** Fairness kolon ismi degisikligi | 1 satir degisiklik, commit |
| 09:15–09:45 | **FE-7** Step 6 onNext CTA butonu | Buton gorunuyor, commit |
| 09:45–10:00 | **FE-6** Certificate endpoint path rename | 1 satir degisiklik, commit |
| 10:00–13:00 | **FE-8** GitHub Wiki Sprint-3 sayfasi olustur | Wiki'de yayinda |
| 14:00–18:00 | **FE-9** GitHub Wiki Sprint-4 sayfasi olustur | Wiki'de yayinda |

> **Not:** Gun 1'de backend'e bagimli isler (FE-1,2,3,4) yapilamaz. Wiki ve bagimsiz UI islerle doldurulur.

#### Berfin
| Saat | Gorev | Teslim |
|------|-------|--------|
| 09:00–18:00 | **RP-2** Weekly Progress Report: velocity chart, sprint ozeti, burndown, Sprint 5 carryovers taslagi | PDF taslak hazir |

> **Not:** Jira burndown ve velocity verilerini cekmek icin sprint board'a erisim gerekli.

---

### GUN 2 — 1 Nisan (Sali)

#### Berat + Efe
| Saat | Gorev | Teslim |
|------|-------|--------|
| 09:00–09:30 | **BE-3** Case study severity alani ekleme (3 dict'e 1'er satir + schema) | Commit |
| 09:30–11:00 | **BE-4** Training data >15pp warnings mantigi + response'a warnings alani | Commit |
| 11:00–11:15 | **BE-5** Certificate endpoint path rename | 1 satir, commit |
| 11:15–13:00 | **BE-6** Test dosyasi #1: `test_step6_explainability.py` (7 test case) | pytest gecen testler |
| 14:00–16:00 | **BE-6** Test dosyasi #2: `test_step7_ethics.py` (7 test case) | pytest gecen testler |
| 16:00–18:00 | **BE-6** Test dosyasi #3: `test_certificate.py` (4 test case) | pytest gecen testler |

> **Kritik:** BE-3, BE-4, BE-5 ogle oncesi bitmeli ki FE-3, FE-4 ogleden sonra baslayabilsin.

#### Batu + Burak
| Saat | Gorev | Teslim |
|------|-------|--------|
| 09:00–12:00 | **FE-10** GitHub Wiki Domain Clinical Review tablosu (20 domain) | Wiki'de yayinda |
| 12:00–13:00 | **FE-3** Case study kart renkleri (BE-3 bitmis olmali) | Commit |
| 14:00–14:30 | **FE-4** Training data >15pp uyari banneri (BE-4 bitmis olmali) | Commit |
| 14:30–18:00 | **FE-1** What-If banner UI baslangic: types, API client, temel banner layout | WIP — types ve API client hazir |

#### Berfin
| Saat | Gorev | Teslim |
|------|-------|--------|
| 09:00–18:00 | **RP-2** Progress Report finalize + Jira board screenshots | PDF final |

---

### GUN 3 — 2 Nisan (Carsamba) — SON GUN

#### Berat + Efe
| Saat | Gorev | Teslim |
|------|-------|--------|
| 09:00–12:00 | **BE-6** Test fix + coverage artirma | Tum testler yesil |
| 12:00–13:00 | FE-1 entegrasyonu icin backend destek (gerekirse whatif edge case fix) | — |
| 14:00–18:00 | Genel bug fix + code review + PR | main branch stabil |

#### Batu + Burak
| Saat | Gorev | Teslim |
|------|-------|--------|
| 09:00–12:00 | **FE-1** What-If banner tamamla: feature dropdown, simulate butonu, sonuc banneri | Calisan banner |
| 12:00–13:00 | **FE-2** Patient dropdown (3 hasta secimi) | Calisan dropdown |
| 14:00–15:00 | End-to-end test: Steps 1-7 sifirdan CSV ile tam gecis | Bug varsa fix |
| 15:00–17:00 | **FE-11** Full Pipeline Test Report (screenshot + yazim) | PDF hazir |
| 17:00–18:00 | Final code review + merge to main | main deploy-ready |

#### Berfin
| Saat | Gorev | Teslim |
|------|-------|--------|
| 09:00–14:00 | **RP-1** Sprint 4 Screenshot Report: tum Step 6+7 ekranlari | PDF/DOCX |
| 14:00–16:00 | **RP-3** Full Pipeline Test Report: Steps 1-7 fresh CSV ile | PDF |
| 16:00–17:00 | **RP-4** 3 farkli domain icin certificate indirip dogrula | Screenshots |
| 17:00–18:00 | Tum PDF'leri GitHub Wiki'ye ve `docs/reports/`'a yukle | Upload tamam |

---

## 5. Bagimlilik Diyagrami

```
GUN 1                          GUN 2                          GUN 3
─────                          ─────                          ─────

BE-1 (What-If EP) ─────────────────────────────────┐
                                                    ├──→ FE-1 (What-If UI)
BE-2 (Sample Patients) ────────────────────────────┤
                                                    └──→ FE-2 (Dropdown)

                               BE-3 (Severity) ──────→ FE-3 (Kart Renkleri)
                               BE-4 (>15pp) ─────────→ FE-4 (Uyari Banner)
                               BE-5 (EP Rename) ─────→ FE-6 (Path Rename)

FE-5 (Fairness) ──┐
FE-7 (CTA Buton) ─┤── Bagimsiz, Gun 1 yapilir
FE-6 (Path) ──────┘

FE-8 (Wiki S3) ───┐
FE-9 (Wiki S4) ───┤── Bagimsiz, Gun 1-2 yapilir
FE-10 (Wiki DR) ──┘

                               BE-6 (Testler) ─────────────────────────┐
                                                                        │
                               RP-2 (Progress) ───────────────────────┤
                                                                        │
                                                    FE-1+2+3+4 bitmeli ┤
                                                                        ├──→ RP-1 (Screenshots)
                                                                        ├──→ RP-3 (Pipeline Test)
                                                                        └──→ RP-4 (Certificate Test)
```

---

## 6. Kontrol Listesi (Teslim Oncesi)

### Kod Kalitesi
- [ ] Tum backend testleri geciyior (`pytest -v`)
- [ ] Frontend build hatasiz (`pnpm build`)
- [ ] End-to-end: Steps 1-7 sifirdan, page reload olmadan calisyor
- [ ] 0 raw column name gorunuyor (clinical names only)
- [ ] 3 farkli domain icin Step 6 + Step 7 dogru calisiyor

### Sprint 4 Metrics Dogrulama
- [ ] Bias banner: 10pp gap'te gizli, 11pp gap'te gorunur
- [ ] Checklist: 8 item, 2 pre-checked, hepsi toggle edilebilir
- [ ] Certificate: 3 domain icin PDF indirildi, icerik dogru
- [ ] Certificate: < 10 saniyede uretildi
- [ ] What-if banner: feature degistiginde olasilik degisiyor

### Deliverables
- [ ] Jira: Sprint 4 stories, story points, sub-tasks
- [ ] GitHub: Feature importance chart (URL)
- [ ] GitHub: Clinical sense-check banner (URL)
- [ ] GitHub: Patient selector + waterfall (URL)
- [ ] GitHub: Caution + what-if banners (URL)
- [ ] GitHub Wiki: Domain Clinical Review tablosu
- [ ] GitHub: Subgroup table (URL)
- [ ] GitHub: Bias auto-detection banner (URL)
- [ ] GitHub: EU AI Act checklist (URL)
- [ ] GitHub: Training data chart (URL)
- [ ] GitHub: AI failure case studies (URL)
- [ ] GitHub: PDF certificate generation (URL)
- [ ] GitHub Wiki: Full Pipeline Test Report (PDF)
- [ ] GitHub Wiki: Weekly Progress Report (PDF)

---

## 7. Risk & Notlar

| Risk | Etki | Onlem |
|------|------|-------|
| What-If endpoint SHAP hesaplamasi yavas olabilir | Demo'da bekleme | Whatif icin SHAP kullanma, sadece `predict_proba` cagir — cok daha hizli |
| Bazi dataset'lerde sex/age kolonu yok | Subgroup tablosu bos kalir | Backend zaten bu durumu handle ediyor (`demographics_available` flag) |
| Wiki PDF upload boyut limiti | Buyuk dosyalar yuklenemez | PDF'leri `docs/reports/` klasorune commit at, wiki'den link ver |
| Jira burndown verisi | Berfin'in erisimi lazim | Sprint board URL'sini paylasın |
