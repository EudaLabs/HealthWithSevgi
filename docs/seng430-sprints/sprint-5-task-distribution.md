# Sprint 5 — Gorev Dagitimi & Zaman Plani

> **Proje:** HealthWithSevgi — SENG 430
> **Sprint 5 Scope:** Polish, User Testing, Performance, Docker, Accessibility, Final Jury Presentation
> **Deadline:** 29 Nisan 2026 (Carsamba), 13:00
> **Bugun:** 20 Nisan 2026 (Pazartesi)
> **Toplam sure:** 9 gun (20 Nisan – 28 Nisan, 29 Nisan sabah son kontroller)
> **Kaynak:** `docs/seng430-sprints/sprint-5.md` (WebOnline assignment)

---

## Takim

| Kisaltma | Isim | Sorumluluk Alani |
|----------|------|------------------|
| **BE** | Efe + Berat | Backend + ML + Jira (Scrum Master rolu) |
| **FE** | Batu + Burak | Frontend + GitHub + Wiki |
| **QA** | Berfin | QA Lead — User Testing, SUS, Video, Consent, E2E, Reports |

> **Not:** Jira = BE ekibi (backlog, burndown, progress report koordinasyon).
> GitHub Wiki = FE ekibi (Sprint 5 sayfasi, Accessibility Fix Log, retros).
> QA Lead = Berfin (user testing, tum raporlar, video, SUS skoru).

---

## 0. Master Ozet Tablosu

| # | Deliverable / Gorev | Ekip | Kisi | Sure | Deadline | Bagimlilik |
|---|---------------------|------|------|------|----------|------------|
| 1 | Docker `compose up` 30s + README Quick Start | FE | Batu + Burak | 2 sa | Pzt 20 | — |
| 2 | Jira Sprint 5 Backlog (US-501..507) | BE | Efe + Berat | 2 sa | Pzt 20 | — |
| 3 | Bug Fix Log (Sprint 4 retro → Jira) | BE | Efe + Berat | 2 sa | Car 22 | — |
| 4 | Backend docstring ≥ 80% (`interrogate`) | BE | Efe + Berat | 4 sa | Cum 24 | — |
| 5 | QA bug ticket'larini fix | BE | Efe + Berat | 3-4 sa | Pzr 26 | QA-7 |
| 6 | Week 9 Progress Report PDF | BE | Efe + Berat | 2 sa | Pzt 27 | 7, 12, 13, 14, 15 |
| 7 | Burndown / velocity export | BE | Efe + Berat | 1 sa | Pzt 27 | 2 |
| 8 | Lighthouse audit + PNG screenshot | FE | Batu + Burak | 1 sa | Pzt 20 | `pnpm build` |
| 9 | Lighthouse Performance fixes (≥ 80) | FE | Batu + Burak | 3-4 sa | Car 22 | 8 |
| 10 | Accessibility audit (axe + Lighthouse) | FE | Batu + Burak | 2 sa | Pzt 20 | — |
| 11 | Accessibility fixes (≥ 85) | FE | Batu + Burak | 4-5 sa | Cmt 25 | 10 |
| 12 | Wiki: Accessibility-Log.md | FE | Batu + Burak | 2 sa | Pzr 26 | 11 |
| 13 | Frontend JSDoc ≥ 80% | FE | Batu + Burak | 4 sa | Pzr 26 | — |
| 14 | Wiki: Sprint-5.md | FE | Batu + Burak | 2 sa | Pzt 27 | 15, 16, 17 |
| 15 | Final Jury slide deck | FE | Batu + Burak | 2-3 sa | Sal 28 | 8, 12, 17 |
| 16 | E2E regression bug fix destek | FE | Batu + Burak | 2 sa | Cmt 25 | QA-6 |
| 17 | User Testing: katilimci + Consent Form | QA | Berfin | 2 sa | Pzt 20 | — |
| 18 | User Testing oturumu (7 task + SUS + kayit) | QA | Berfin | 3 sa | Sal 21 | 1, 9 |
| 19 | User Testing Report PDF | QA | Berfin | 3 sa | Car 22 | 18 |
| 20 | Usability Video 5 dk MP4 edit | QA | Berfin | 2 sa | Per 23 | 18 |
| 21 | Full Domain Coverage (20 specialty) | QA | Berfin | 4-5 sa | Cmt 25 | — |
| 22 | E2E Regression (3 CSV) | QA | Berfin | 2 sa | Pzr 26 | — |
| 23 | Bug ticket acimi (QA-5 + QA-6) | QA | Berfin | 1 sa | Pzr 26 | 21, 22 |
| 24 | Week 9 Progress Report destek | QA | Berfin | 1 sa | Pzt 27 | 6 |

**Toplam:** BE 14-15 sa · FE 24-27 sa · QA 18-19 sa

---

## 0.1 Deliverable → Sorumlu Tablosu

| Sprint 5 Deliverable (Spec) | Format | Asil Sorumlu | Dosya Hedefi |
|-----------------------------|--------|--------------|--------------|
| Sprint 5 Backlog | Jira | **BE** | Jira board screenshot |
| Bug Fix Log | Jira | **BE** | Jira screenshot `docs/reports/Sprint5_Bug_Fix_Log.png` |
| Week 9 Progress Report | PDF | **BE** (+QA destek) | `docs/reports/Sprint5_Weekly_Progress_Report.pdf` |
| Docker working (`docker compose up`) | Canli demo | **FE** | `docker-compose.yml`, `README.md` |
| Code Documentation ≥ 80% | Kod | **BE** (backend) + **FE** (frontend) | docstring + JSDoc |
| User Testing Report | PDF | **QA** | `docs/reports/Sprint5_User_Testing_Report.pdf` |
| Signed Consent Forms | PDF | **QA** | `docs/reports/Sprint5_Consent_Form.pdf` |
| Usability Test Video | MP4 ≤ 5 min | **QA** | `docs/reports/Sprint5_Usability_Video.mp4` |
| SUS Score ≥ 68 | Anket | **QA** | User Testing Report icinde |
| Full Domain Coverage (20) | PDF | **QA** | `docs/reports/Sprint5_Full_Domain_Coverage.pdf` |
| E2E Regression (3 CSV) | PDF | **QA** | `docs/reports/Sprint5_E2E_Regression.pdf` |
| Lighthouse Report Screenshot | PNG | **FE** | `docs/reports/Sprint5_Lighthouse_Report.png` |
| Accessibility Fix Log | GitHub Wiki | **FE** | `docs/wiki/Accessibility-Log.md` + push |
| Sprint-5 Wiki sayfasi | GitHub Wiki | **FE** | `docs/wiki/Sprint-5.md` + push |
| Final Jury Slide Deck | PDF | **FE** | `docs/reports/Sprint5_Showcase.pdf` |

---

## 0.2 Gun / Kisi Matrisi (Kim Ne Gun Ne Yapacak)

| Gun | Tarih | Efe + Berat (BE) | Batu + Burak (FE) | Berfin (QA) |
|-----|-------|------------------|-------------------|-------------|
| 1 | 20 Nis Pzt | BE-2 Jira backlog | FE-10 Docker · FE-1 Lighthouse · FE-3 A11y audit | QA-1 Katilimci + Consent |
| 2 | 21 Nis Sal | BE-3 Bug Log (baslangic) | FE-2 Perf fixes | QA-2 User Testing oturumu |
| 3 | 22 Nis Car | BE-3 tamamla · BE-4 docstring | FE-2 tamamla · FE-6 JSDoc | QA-3 Report yazim |
| 4 | 23 Nis Per | BE-4 devam | FE-4 A11y fixes | QA-4 Video edit |
| 5 | 24 Nis Cum | BE-4 tamamla · BE-5 baslangic | FE-4 · FE-6 devam | QA-5 Domain test (1-10) |
| 6 | 25 Nis Cmt | BE-5 QA bug fix | FE-9 bug fix · FE-4 finalize | QA-5 Domain test (11-20) |
| 7 | 26 Nis Pzr | BE-5 tamamla | FE-5 A11y Log · FE-6 tamamla | QA-6 E2E + QA-7 ticket |
| 8 | 27 Nis Pzt | BE-6 Progress Report · BE-7 burndown | FE-7 Wiki S5 · FE-8 slide | QA-8 Report destek |
| 9 | 28 Nis Sal | BE-6 finalize | FE-8 slide · upload | Tum PDF upload |
| 10 | 29 Nis Car | Final Jira check | Docker canli demo provasi · Wiki push verify | Jury 13:00 |

---

## 1. Sprint 5 Gereksinimleri Ozeti

### 1.1 User Testing Protocol (non-CS katilimci, bagimsiz)

| Task | Ne yapilacak | Basari Kriteri | Sure |
|------|--------------|----------------|------|
| T1 | Domain pill bar'da 2 farkli specialty arasinda gecis | Dogru pill, Step 1 icerik guncelleniyor | 90s |
| T2 | Sample CSV upload + Column Mapper acma | CSV kabul edildi, mapper acildi | 3 min |
| T3 | Column Mapper validation + Step 3 gecis | Save → yesil banner → Step 3 | 2 min |
| T4 | Step 3 preparation + Step 4 gecis | Apply → yesil banner → Step 4 | 3 min |
| T5 | KNN egit + Step 5'te Sensitivity bulma | Dogru deger + renk okunuyor | 3 min |
| T6 | Step 6'da top feature bulma | En onemli ozellik isimlendiriliyor | 2 min |
| T7 | Summary Certificate indir | PDF basariyla indi | 1 min |

**Basari esigi:** 7 task'tan ≥ 5'i bagimsiz olarak sure limitinde tamamlanmali.

### 1.2 Week 10 Deliverables

| # | Artifact | Format | Asil Sorumlu |
|---|----------|--------|--------------|
| 1 | Sprint 5 Backlog | Jira | BE (Scrum) |
| 2 | User Testing Report | PDF | QA |
| 3 | Signed Consent Forms | PDF | QA |
| 4 | Usability Test Video | MP4 ≤ 5 min | QA |
| 5 | Lighthouse Report Screenshot | PNG/PDF | FE |
| 6 | Accessibility Fix Log | GitHub Wiki | FE |
| 7 | Bug Fix Log | Jira | BE |
| 8 | Week 9 Progress Report | PDF → Wiki | BE (Scrum) + QA destek |

### 1.3 Metrics (Gecis Esikleri)

| Metric | Target |
|--------|--------|
| Usability Task Completion | ≥ 5 / 7 |
| SUS Score | ≥ 68 |
| Lighthouse Performance | ≥ 80 |
| Lighthouse Accessibility | ≥ 85 |
| Docker Startup | ≤ 30 saniye |
| E2E Regression (3 CSV) | 0 crash |
| Code Documentation | ≥ 80% (JSDoc + docstring) |
| Full Domain Coverage | 20 / 20 domain Step 1-7 |

### 1.4 Showcase (Carsamba, 5 dk / grup)

1. Usability test videosundan 3 dk kesit + task tamamlama sayisi
2. Lighthouse raporu (perf + accessibility skorlari)
3. Bir accessibility fix before/after
4. **Canli `docker-compose up` demo** (app 30s icinde acilmali)

---

## 2. Eksik Listesi (Spec vs Mevcut Durum)

### 2.1 User Testing Artifacts — TAMAMEN EKSIK (Kritik)

| | Detay |
|---|---|
| **Mevcut durum** | `docs/reports/` icinde user testing yok. Consent form template yok. SUS form yok. Video yok. |
| **Gereken** | Katilimci bulma, 7 task'i calistirma, SUS anketi, screen record, PDF rapor |
| **QA** | (1) Katilimci profili: non-CS + university-level education. (2) Consent form imzalat (video/gozlem izni). (3) Screen record (OBS / Loom). (4) 7 task'i coaching YAPMADAN yaptir, sure tut. (5) Sonrasinda SUS (10 soru) doldurt. (6) PDF rapor: profil, task tablosu, failure notes, katilimci quote'lari, SUS skoru. (7) Video 5 dk max MP4 |
| **Bagimlilik** | Production build + Docker calisir durumda olmali |

---

### 2.2 Docker-Compose — INCOMPLETE

| | Detay |
|---|---|
| **Mevcut durum** | Root'ta `docker-compose.yml` var ama tek service (hf-space, 7860). Frontend+backend split yok. Sprint 5 `docker-compose up` canli demo istiyor |
| **Spec** | `docker-compose up` → 30 saniyede tam yuklensin |
| **FE** | (1) Root `docker-compose.yml` `docker compose up` ile Windows+Linux'ta calistigini dogrula. (2) Build cache warm iken 30s altinda acilmali — oyle degilse Dockerfile'i iyilestir (multi-stage mevcut, deps onboard ama ilk build uzun; frontend build stage'i optimize et). (3) README.md'ye "Docker Quick Start" bolumu ekle: `docker compose up` → http://localhost:7860. (4) `.dockerignore` kontrolu (node_modules, venv, __pycache__ disinda olmali) |
| **Dogrulama** | Temiz makinede `docker compose up` → ilk container start ≤ 30s |

---

### 2.3 Lighthouse Audit — HIC CALISTIRILMADI

| | Detay |
|---|---|
| **Spec** | Performance ≥ 80, Accessibility ≥ 85 |
| **Mevcut durum** | `frontend/`'de lighthouse config yok. Audit calismamis. Skor bilinmiyor |
| **FE** | (1) `pnpm build` + `pnpm preview` ile production build calistir. (2) Chrome DevTools Lighthouse audit (Performance + Accessibility + Best Practices + SEO). (3) Skor < 80 / < 85 ise iyilestir: code splitting (Step5/6 zaten lazy), image optimization (qa_screenshots disarida), font preload, unused CSS purge. (4) PNG screenshot al. (5) `docs/reports/Sprint5_Lighthouse_Report.png` olarak commit |

---

### 2.4 Accessibility Fixes + Fix Log — EKSIK

| | Detay |
|---|---|
| **Spec** | GitHub Wiki'de "Accessibility Fix Log" sayfasi — bulunan her violation + nasil duzeltildigi |
| **Mevcut durum** | Wiki'de yok. axe DevTools / Lighthouse Accessibility hic calistirilmamis |
| **FE** | (1) `pnpm build` sonrasi Lighthouse Accessibility + axe DevTools ile tum Step sayfalarini (1-7) taraman. (2) Tespit edilen her violation icin dosyayi + satiri bul: eksik `aria-label`, dusuk kontrast, keyboard nav, focus ring, form label'lari, `alt` eksikleri. (3) Her birini duzelt (before/after commit ayri olsun). (4) Wiki'de `Accessibility-Log.md` sayfasi: tablo — `Violation \| Dosya:Satir \| Duzeltme \| Sprint Commit SHA`. (5) En az 1 tane before/after screenshot al — showcase'de gosterilecek |

---

### 2.5 Bug Fix Log (Sprint 4 retrospective'inden) — EKSIK

| | Detay |
|---|---|
| **Spec** | Sprint 4 retro'sundaki tum bug'lar ya kapali ya da dokumante |
| **Mevcut durum** | Sprint 4 retrospective bolumu eklendi (`docs/wiki/Sprint-4.md`) ama Jira'da formal bug tracking yok |
| **BE** | (1) Jira Sprint 5 board'a "Bug Fix Log" epic'i ac. (2) Sprint 4 retro Improve listesindeki her item icin Jira ticket ac (ornek: "dayanikli CSV parse", "ML tahmin sonrasi loading state", "sub-group banner 15pp threshold edge case"). (3) Her ticket'i ya "Done" ya "Won't Fix" ya "Deferred to Sprint 6" statusune cek. (4) Sprint sonunda Jira ekran goruntusu `docs/reports/Sprint5_Bug_Fix_Log.png` olarak eklenecek |

---

### 2.6 Sprint 5 Backlog (Jira) — AC

| | Detay |
|---|---|
| **Spec** | Sprint 5 Backlog: remaining bugs, polish tasks, user testing stories, Docker story, documentation stories |
| **BE** | (1) Jira'da Sprint 5 sprint'ini ac. (2) Stories: US-501 User Testing, US-502 Lighthouse ≥ 80, US-503 Accessibility ≥ 85, US-504 Docker 30s, US-505 Code Docs ≥ 80%, US-506 Full Domain Coverage, US-507 Sprint 5 Final Report + Showcase. (3) Her story'e acceptance criteria (Gherkin). (4) Story point tahmini (planning poker). (5) Sprint board screenshot |

---

### 2.7 Code Documentation Coverage — HIC OLCULMEDI

| | Detay |
|---|---|
| **Spec** | ≥ 80% fonksiyon dokumante (JSDoc / docstring) |
| **Mevcut durum** | `backend/app/services/` icinde bazi docstring var, `frontend/src/` icinde JSDoc neredeyse yok |
| **BE** | (1) `interrogate` python kutuphanesi ile docstring coverage olc: `pip install interrogate && interrogate backend/app -v`. (2) < 80% ise eksik fonksiyonlara 1-2 satir docstring ekle (service metodlari, router handler'lari, pydantic model field'lari) |
| **FE** | (1) `jsdoc` + `documentation` ile coverage olc veya manuel: `frontend/src/pages/`, `frontend/src/api/`, `frontend/src/components/` icindeki export fonksiyonlara `/** */` JSDoc ekle. (2) En onemli: each `Step{N}*.tsx` component + `api/*.ts` export'lar + `components/charts/*.tsx`. (3) Rapor screenshot |

---

### 2.8 Full Domain Coverage (20 domain E2E) — MANUEL TEST GEREKLI

| | Detay |
|---|---|
| **Spec** | 20 specialty icin Steps 1-7 hatasiz tamamlansin |
| **Mevcut durum** | Sprint 4'te 3-4 domain test edildi. 20 domain full test yok |
| **QA** | (1) `specialty_registry.py`'deki 20 specialty icin tablo olustur. (2) Her domain icin: CSV yukle → Step 1-7 tamamla → hata / uyari logla. (3) Bulunan her hata Jira bug ticket'a donussun (BE'ye ilet). (4) Sonuc tablosu: `Domain \| Step 1 \| Step 2 \| ... \| Step 7 \| Notes`. (5) `docs/reports/Sprint5_Full_Domain_Coverage.pdf` |
| **BE** | QA'in actigi bug ticket'lari fix |

---

### 2.9 E2E Regression (3 CSV, 0 crash) — EKSIK

| | Detay |
|---|---|
| **Spec** | 3 farkli CSV ile Steps 1-7 full run — sifir crash |
| **Mevcut durum** | Sprint 4'te pipeline testi var ama 3 farkli CSV degil |
| **QA** | Diyabet + Breast Cancer + Heart Disease CSV'leri ile 3 ayri run. Her run screenshot + timing. Crash varsa immediate bug ticket. `docs/reports/Sprint5_E2E_Regression.pdf` |

---

### 2.10 Week 9 Progress Report — EKSIK

| | Detay |
|---|---|
| **Spec** | Burndown, user testing status, performance scores, Docker status |
| **BE** | (1) Jira'dan burndown chart export. (2) Template: `docs/reports/Sprint4_Weekly_Progress_Report.pdf`'i kopyala, Sprint 5 verileriyle guncelle |
| **QA** | Destek: user testing durumu, SUS skoru, performance skoru bilgileri BE'ye ilet |
| **Final** | PDF GitHub Wiki'ye yuklenecek |

---

### 2.11 Sprint 5 Wiki Sayfasi — EKSIK

| | Detay |
|---|---|
| **Mevcut durum** | Wiki'de Sprint-4.md var, Sprint-5.md yok |
| **FE** | (1) Sprint-1..4 formatinda `Sprint-5.md` olustur. (2) Icerik: Scope, User Testing sonuclari, Lighthouse skorlari, Accessibility fix ozeti, Docker status, Metrics tablosu, Retrospective (Keep/Improve/Try). (3) `docs/wiki/Sprint-5.md` mirror + GitHub Wiki push |

---

### 2.12 Final Jury Presentation — EKSIK

| | Detay |
|---|---|
| **Spec** | 5 dk showcase (video 3 dk + Lighthouse + a11y before/after + `docker-compose up`) |
| **FE** | Slide deck hazirla: (1) 1 slide — proje ozet. (2) 3 dk video embed/ekran kaydi. (3) Lighthouse skor screenshot. (4) Accessibility before/after. (5) Docker demo icin backup screenshot (canli demo fail olursa) |
| **QA** | Videoyu son haliyle onayla + SUS skorunu sunuma hazir hale getir |

---

## 3. Gorev Atama Tablosu

### BE — Efe + Berat (Backend + ML + Jira)

| ID | Gorev | Ilgili Eksik | Dosya(lar) | Sure |
|----|-------|--------------|------------|------|
| BE-2 | Jira Sprint 5 Backlog olustur (US-501..507) | 2.6 | Jira | 2 saat |
| BE-3 | Bug Fix Log (Sprint 4 retro → Jira tickets) | 2.5 | Jira | 2 saat |
| BE-4 | Backend docstring coverage ≥ 80% (`interrogate`) | 2.7 | `backend/app/services/*.py`, `backend/app/routers/*.py`, `backend/app/models/*.py` | 4 saat |
| BE-5 | QA bug ticket'larini fix (full domain coverage'den) | 2.8 | `backend/app/*` | 3-4 saat |
| BE-6 | Week 9 Progress Report PDF | 2.10 | `docs/reports/Sprint5_Weekly_Progress_Report.pdf` | 2 saat |
| BE-7 | Burndown chart + velocity guncelle | 2.10 | Jira export | 1 saat |

---

### FE — Batu + Burak (Frontend + GitHub + Wiki)

| ID | Gorev | Ilgili Eksik | Dosya(lar) | Sure | Bagimlilik |
|----|-------|--------------|------------|------|------------|
| FE-1 | Lighthouse audit + PNG screenshot (≥80 / ≥85) | 2.3 | `frontend/` production build | 1 saat | `pnpm build` |
| FE-2 | Lighthouse Performance fixes (< 80 ise) | 2.3 | `frontend/src/*`, `frontend/vite.config.ts` | 3-4 saat | FE-1 |
| FE-3 | Accessibility audit (axe + Lighthouse) + violation listesi | 2.4 | frontend Step 1-7 | 2 saat | FE-1 |
| FE-4 | Accessibility fixes (aria-label, kontrast, focus, alt, label) | 2.4 | `frontend/src/pages/Step*.tsx`, `frontend/src/styles/globals.css` | 4-5 saat | FE-3 |
| FE-5 | Wiki: Accessibility-Log.md (violation + fix + before/after) | 2.4 | `docs/wiki/Accessibility-Log.md` + GitHub Wiki | 2 saat | FE-4 |
| FE-6 | Frontend JSDoc coverage ≥ 80% | 2.7 | `frontend/src/pages/*.tsx`, `api/*.ts`, `components/charts/*.tsx` | 4 saat | — |
| FE-7 | Wiki: Sprint-5.md (scope + metrics + retro) | 2.11 | `docs/wiki/Sprint-5.md` + GitHub Wiki | 2 saat | QA-1..3 bitmeli |
| FE-8 | Final Jury slide deck | 2.12 | `docs/reports/Sprint5_Showcase.pdf` | 2-3 saat | QA-3, FE-1 |
| FE-9 | End-to-end regression destek (QA ile birlikte bug fix) | 2.9 | frontend bugs | 2 saat | QA-4 |
| FE-10 | Docker-compose 30s verify + README Quick Start | 2.2 | `docker-compose.yml`, `Dockerfile`, `README.md`, `.dockerignore` | 2 saat | — |

---

### QA — Berfin (QA Lead)

| ID | Gorev | Ilgili Eksik | Dosya/Format | Sure | Bagimlilik |
|----|-------|--------------|--------------|------|------------|
| QA-1 | User Testing katilimci bulma + Consent Form | 2.1 | `docs/reports/Consent_Form_Template.pdf` | 2 saat | — |
| QA-2 | User Testing oturumu (7 task + SUS) + video kayit | 2.1 | OBS/Loom, raw MP4 | 3 saat | FE-10 (Docker), FE-2 (Lighthouse fixed) |
| QA-3 | User Testing Report PDF (profil + task + SUS + quotes) | 2.1 | `docs/reports/Sprint5_User_Testing_Report.pdf` | 3 saat | QA-2 |
| QA-4 | Video 5 dk MP4 edit (3 dk showcase kesit + full) | 2.1 | `docs/reports/Sprint5_Usability_Video.mp4` | 2 saat | QA-2 |
| QA-5 | Full Domain Coverage test (20 specialty) | 2.8 | `docs/reports/Sprint5_Full_Domain_Coverage.pdf` | 4-5 saat | — |
| QA-6 | E2E Regression (3 CSV) | 2.9 | `docs/reports/Sprint5_E2E_Regression.pdf` | 2 saat | — |
| QA-7 | Bug ticket actimi (QA-5 + QA-6 sonuclari) | 2.5, 2.8 | Jira | 1 saat | QA-5, QA-6 |
| QA-8 | Week 9 Progress Report destek + final review | 2.10 | BE-6 ile koord | 1 saat | BE-6 |

---

## 4. Gun Bazli Plan (9 Gun)

```
Hafta 1 (20–26 Nisan)                  Hafta 2 (27–29 Nisan)
─────────────────────                  ──────────────────────

Pzt 20    Sal 21    Car 22    Per 23    Cum 24    Cmt 25    Pzr 26    Pzt 27    Sal 28    Car 29
─────     ─────     ─────     ─────     ─────     ─────     ─────     ─────     ─────     ─────
BE-2      BE-3      BE-3      BE-4      BE-4      BE-4      BE-5      BE-5      BE-6      Final
                              BE-4                BE-5                          BE-7       Check

FE-10     FE-2      FE-2      FE-3      FE-4      FE-4      FE-5      FE-6      FE-7      Docker
FE-1                FE-6      FE-4     FE-6      FE-9      FE-6      FE-8      FE-8      prova
FE-3                                                                                       + Wiki
                                                                                           push
QA-1      QA-2      QA-3      QA-4      QA-5      QA-5      QA-6      QA-7      QA-8      Jury
          (if app                                                                          13:00
          ready)
```

### GUN 1 — 20 Nisan (Pazartesi, **bugun**)

**BE (Efe + Berat):**
- **BE-2** (09:00–12:00) Jira Sprint 5 Backlog (US-501..507, story points, acceptance criteria)
- Sprint 4 retro bug listesini cikart (BE-3 prep)

**FE (Batu + Burak):**
- **FE-10** (09:00–11:00) Docker compose up test + timing + README Quick Start bolumu + `.dockerignore` dogrulama
- **FE-1** (11:00–12:00) Production build + Lighthouse audit + PNG screenshot
- **FE-3** (13:00–15:00) Accessibility audit (axe + Lighthouse) → violation listesi
- Sonuclara gore FE-2 / FE-4 icin todo-list cikart

**QA (Berfin):**
- **QA-1** (tum gun) Non-CS katilimci kontak kur + consent form template hazirla + test senaryosu (7 task detayli adim adim) yazim

---

### GUN 2 — 21 Nisan (Sali)

**BE:**
- Dun bitmemis BE-2 tamamla
- **BE-3** baslangic (Sprint 4 retro bug'lari Jira'ya)

**FE:**
- **FE-2** (tum gun) Lighthouse Performance fix (code split, bundle, images)

**QA:**
- **QA-2** (eger app hazir degilse Sali erteleme) — degilse katilimci prep + SUS form dogrula

---

### GUN 3 — 22 Nisan (Carsamba)

**BE:**
- **BE-3** tamamla
- **BE-4** baslangic (backend docstring coverage)

**FE:**
- **FE-2** tamamla (Lighthouse ≥ 80 dogrula)
- **FE-6** baslangic (JSDoc)

**QA:**
- **QA-3** User Testing Report taslak yazim (QA-2 yapildiysa)

---

### GUN 4 — 23 Nisan (Persembe)

**BE:** BE-4 devam

**FE:** **FE-4** Accessibility fixes baslangic (aria-label, kontrast)

**QA:** **QA-4** Video edit (3 dk showcase kesit + full 5 dk)

---

### GUN 5 — 24 Nisan (Cuma)

**BE:** BE-4 tamamla + **BE-5** bug fix baslangic

**FE:** FE-4 devam + **FE-6** JSDoc devam

**QA:** **QA-5** Full Domain Coverage baslangic (10 domain)

---

### GUN 6 — 25 Nisan (Cumartesi)

**BE:** BE-5 devam (QA-7 ticket'larina gore)

**FE:** **FE-9** QA bug'larini fix + FE-4 finalize

**QA:** QA-5 devam (kalan 10 domain)

---

### GUN 7 — 26 Nisan (Pazar)

**BE:** BE-5 tamamla

**FE:** **FE-5** Accessibility-Log.md yazim + **FE-6** tamamla

**QA:** **QA-6** E2E Regression (3 CSV) + **QA-7** bug ticket acimi

---

### GUN 8 — 27 Nisan (Pazartesi)

**BE:** **BE-6** Week 9 Progress Report PDF + **BE-7** burndown

**FE:** **FE-7** Wiki Sprint-5.md yazim + **FE-8** slide deck baslangic

**QA:** **QA-8** Progress Report review + SUS skoru final

---

### GUN 9 — 28 Nisan (Sali) — SON HAZIRLIK

**BE:** BE-6 finalize, tum Jira kapali ticket'lari dogrula

**FE:** FE-8 slide deck tamamla, Wiki push, son regression

**QA:** Tum PDF'leri + video'yu `docs/reports/` ve GitHub Wiki'ye upload

---

### 29 Nisan (Carsamba) — SUBMISSION + JURY

- **09:00–12:00** Final check: Docker canli demo provasi, tum PDF upload verify, wiki link check
- **13:00** Submission
- **Jury** (Carsamba Showcase — 5 dk): video + Lighthouse + a11y + Docker

---

## 5. Bagimlilik Diyagrami

```
Gun 1                   Gun 2-3                 Gun 4-5                 Gun 6-7                 Gun 8-9
─────                   ───────                 ───────                 ───────                 ───────

FE-10 (Docker) ──────────────────────────────────────────────────────────────────────────┐
                                                                                          │
BE-2 (Jira) ──────────────────────────────────────────────────────────────────────────┤
                                                                                          │
FE-1 (Lighthouse audit) ──→ FE-2 (Perf fix) ──→ [≥80 ✓]                                ├──→ QA-2 (User Test)
                                                                                         │         │
FE-3 (A11y audit) ────────→ FE-4 (A11y fix) ──→ FE-5 (A11y Log)                       │         │
                                                                                         │         ↓
                                                                                         │    QA-3 (Report)
                                                                                         │    QA-4 (Video)
BE-3 (Bug Log) ──────→ BE-5 (QA bug fix) ──────────────────────────────────────────────┤
                                                                                         │
QA-5 (20 domain) ──→ QA-7 (ticket) ──→ BE-5 (fix)                                     │
QA-6 (3 CSV E2E) ──→ QA-7 (ticket)                                                     │
                                                                                         │
BE-4 (docstring) ─────────────────────────────────────────────────────────────→ [≥80% ✓]│
FE-6 (JSDoc) ─────────────────────────────────────────────────────────────────→ [≥80% ✓]│
                                                                                         │
QA-3 + QA-4 + FE-1 + FE-5 + BE-6 ───────────→ FE-7 (Wiki S5) + FE-8 (Slide deck) ──→ JURY
```

---

## 6. Kontrol Listesi (Teslim Oncesi)

### Metrics
- [ ] Usability: ≥ 5 / 7 task non-CS katilimci tarafindan sure limitinde tamamlandi
- [ ] SUS skoru ≥ 68
- [ ] Lighthouse Performance ≥ 80
- [ ] Lighthouse Accessibility ≥ 85
- [ ] `docker compose up` → app ≤ 30 saniyede acildi
- [ ] E2E: 3 farkli CSV ile 0 crash
- [ ] JSDoc + docstring coverage ≥ 80%
- [ ] 20 domain Steps 1-7 full pipeline hatasiz

### Deliverables (Wiki + `docs/reports/`)
- [ ] Jira Sprint 5 Backlog screenshot
- [ ] Jira Bug Fix Log screenshot
- [ ] User Testing Report PDF (`docs/reports/Sprint5_User_Testing_Report.pdf`)
- [ ] Signed Consent Form PDF (`docs/reports/Sprint5_Consent_Form.pdf`)
- [ ] Usability Test Video MP4 (`docs/reports/Sprint5_Usability_Video.mp4`)
- [ ] Lighthouse Report PNG (`docs/reports/Sprint5_Lighthouse_Report.png`)
- [ ] Accessibility Fix Log Wiki sayfasi (`docs/wiki/Accessibility-Log.md` + push)
- [ ] Week 9 Progress Report PDF (`docs/reports/Sprint5_Weekly_Progress_Report.pdf`)
- [ ] Sprint-5 Wiki sayfasi (`docs/wiki/Sprint-5.md` + push)
- [ ] Full Domain Coverage PDF (`docs/reports/Sprint5_Full_Domain_Coverage.pdf`)
- [ ] E2E Regression PDF (`docs/reports/Sprint5_E2E_Regression.pdf`)
- [ ] Final Jury slide deck (`docs/reports/Sprint5_Showcase.pdf`)

### Showcase Hazirligi
- [ ] Video 3 dk kesit hazir
- [ ] Lighthouse screenshot slide'da
- [ ] Accessibility before/after slide'da
- [ ] Docker backup screenshot (canli demo fail olursa)
- [ ] `docker compose up` canli demo prova edildi

---

## 7. Risk & Notlar

| Risk | Etki | Onlem |
|------|------|-------|
| Non-CS katilimci bulunamaz | User Testing yapilamaz | Sali'ye kadar 2 aday belirle (aile / farkli bolum arkadas) |
| Lighthouse Performance < 80 cikar | Target kacar | FE-2'ye tum Carsamba ayrilabilir — code split zaten Step 5+6 icin var, bundle analyzer calistir |
| Accessibility violation cok fazla | FE-4 overflow | Sadece "critical" + "serious" violation'lari fix et, "minor" olanlari Sprint 6'ya ertele |
| `docker compose up` 30s'yi gecer | Showcase riski | Dockerfile build cache optimize, CMD'den async import'lari cikart |
| 20 domain testi cok uzun | QA overflow | QA-5'i 2 gune bol (10+10), bulunan hatalari priority'ye gore sirala |
| Jury'de canli Docker fail | Demo crash | Backup screenshot slide'da hazir; `docker compose up` ekran kaydi video'ya embed |
| Branch protection | Push fail | Sprint 5 calismalarinda `feature/US-5XX` branch + PR akisi (CLAUDE.md branch strategy) |

---

## 8. Ozet — Herkes Ne Yapacak

**Efe + Berat (BE) — Backend, ML, Jira:**
Jira Sprint 5 backlog, bug fix log, backend docstring ≥ 80%, QA bug'larini fix, Week 9 Progress Report PDF, burndown.

**Batu + Burak (FE) — Frontend, GitHub, Wiki, Docker:**
Docker `compose up` 30s validate + README Quick Start, Lighthouse audit (≥ 80 / ≥ 85), Performance + Accessibility fixes, Wiki Accessibility-Log sayfasi, frontend JSDoc ≥ 80%, Wiki Sprint-5 sayfasi, Final Jury slide deck.

**Berfin (QA) — QA Lead:**
User Testing (katilimci + 7 task + SUS + video), User Testing Report PDF, Consent Form, 5dk MP4 edit, 20 domain coverage, 3 CSV E2E regression, bug ticket acimi, Week 9 Progress Report destek.

---

**Son teslim:** 29 Nisan 2026 Carsamba 13:00.
**Jury showcase:** Carsamba, 5 dk / grup.
**Wiki URL:** https://github.com/EudaLabs/HealthWithSevgi/wiki
**Jira:** https://eudaimonia06101.atlassian.net (Sprint 5 board)
