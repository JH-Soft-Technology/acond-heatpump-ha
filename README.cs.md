# ♨️ Tepelné čerpadlo Acond pro Home Assistant

Integrace tepelného čerpadla **Acond Therm** do Home Assistantu přes **Modbus TCP**: nativní integrace instalovatelná z HACS (nastavení v UI, bez YAML, bez dalších Python závislostí). K tomu ilustrovaná záložka dashboardu, která ukazuje celý systém (venkovní jednotka, výstupní voda a zpátečka, otopný okruh domu, zásobník TUV) s živými hodnotami a umožňuje ho ovládat.

🌐 **[English README](README.md)**

![Platform](https://img.shields.io/badge/platform-Home%20Assistant-41BDF5)
![Protocol](https://img.shields.io/badge/protocol-Modbus%20TCP-orange)
![License](https://img.shields.io/badge/license-MIT-green)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5)](https://hacs.xyz)
![Validate](https://github.com/JH-Soft-Technology/acond-heatpump-ha/actions/workflows/validate.yml/badge.svg)

---

## 📸 Náhled

| Počítač | Telefon |
|---|---|
| ![Počítač](docs/preview-desktop-light.png) | ![Telefon](docs/preview-mobile-dark.png) |

> Náhledy jsou vykreslené z konfigurace dashboardu s ukázkovými hodnotami. V Home Assistantu jsou ikony skutečné MDI ikony a ventilátor se při běhu kompresoru točí.

---

## ✨ Funkce

- čtení všech registrů, které firmware Acond zpřístupňuje (input `30001–30018`, holding `40001–40012`), dvěma dotazy přes **Modbus TCP**, nastavení v UI
- **Senzory**: okruh 1 a 2 (aktuální / žádaná), TUV (aktuální / žádaná), výstupní voda, zpátečka (aktuální / žádaná), venkovní teplota, solanka, heartbeat komunikace
- **Stavové bity** z `TC_status` jako binární senzory: TČ zapnuto, kompresor, porucha, ohřev TUV, oběh okruhu 1, odtávání, bivalence, letní provoz, chlazení
- **Ovládání**:
  - termostaty (`climate`) pro okruh 1, okruh 2 (volitelně) a TUV, včetně stavu topí/nečinný, žádaná teplota se zapisuje do holding registrů
  - `select` pro režim TČ (Automat / Jen TČ / Jen bivalence / Vypnuto / Chlazení), zachovává ostatní bity `TC_set`
  - `select` pro typ regulace (AcondTherm / Ekviterm / Manuál)
  - `number` pro žádanou zpátečku v manuálním režimu
- **Záložka dashboardu**:
  - ilustrované schéma s živými hodnotami: červená = aktuální, zelená = žádaná
  - samostatné rozložení pro počítač a telefon (přepíná se na 768 px)
  - animace ventilátoru při běhu kompresoru, výrazné upozornění na poruchu
  - klepnutím na teplotu se otevře termostat, klepnutím na ikonu režimu/regulace jejich změna
  - grafy teplot a provozu za 24 h

---

## 📦 Obsah

```
custom_components/acond_heatpump/   # integrace (instaluje ji HACS)
  www/                              # SVG pro dashboard, dostupné na /acond_heatpump/...
  brand/                            # ikona integrace
dashboard/heat-pump-view.yaml       # záložka Lovelace (sections)
legacy/packages/acond.yaml          # původní varianta jen v YAML (s integrací není potřeba)
docs/                               # náhledové obrázky
```

---

## 🚀 Instalace

### 1. Zapni Modbus TCP v TČ
Ve webovém rozhraní TČ otevři stránku **ModbusTCP** a zaškrtni **ModbusTCP**. Dokud se nepřipojí Home Assistant, stav ukazuje `ModbusTCP false` – to je v pořádku.

> ⚠️ TČ dovoluje **jen jednoho Modbus mastera**. Ujisti se, že ho nečte žádný jiný systém. Při výpadku komunikace delším než *MaxCommDataRefresh* (výchozí 30 s) se TČ vrací na vlastní regulaci.

### 2. Instalace přes HACS
[![Otevřít repozitář v HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=JH-Soft-Technology&repository=acond-heatpump-ha&category=integration)

Nebo ručně: **HACS → ⋮ → Vlastní repozitáře** → `https://github.com/JH-Soft-Technology/acond-heatpump-ha`, typ **Integrace** → stáhni **Acond Heat Pump** → restartuj Home Assistant.

<details><summary>Ruční instalace bez HACS</summary>

Zkopíruj `custom_components/acond_heatpump` do `/config/custom_components/` a restartuj Home Assistant.
</details>

### 3. Přidej integraci
[![Přidat integraci](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=acond_heatpump)

**Nastavení → Zařízení a služby → Přidat integraci → Acond Heat Pump** a vyplň:

| Pole | Výchozí | Poznámka |
|---|---|---|
| Adresa | – | IP adresa TČ |
| Port | `502` | |
| Modbus ID zařízení | `1` | ID `2` je vyhrazené pro kaskády |
| Interval čtení | `10 s` | 5–25 s, musí být kratší než *MaxCommDataRefresh* |
| 2. topný okruh | vyp | přidá termostat a senzory okruhu 2 |
| Okruh solanky | vyp | jen jednotky země/voda |

Interval a volitelné okruhy jde později změnit přes **Konfigurovat**.

### 4. Přidej záložku dashboardu
Otevři dashboard → **⋮ → Upravit dashboard → ⋮ → Editor surové konfigurace** a vlož obsah `dashboard/heat-pump-view.yaml` jako novou položku pod `views:`. Obrázky servíruje integrace, do `/config/www` se nic nekopíruje.

### Přechod z YAML balíčku (v1.x)
1. Smaž `/config/packages/acond.yaml` (případně i `/config/www/acond/`) a restartuj Home Assistant.
2. V **Nastavení → Entity** smaž osiřelé entity `acond_*` (filtr *Jen pro čtení*), jinak nové dostanou příponu `_2`.
3. Nainstaluj integraci podle postupu výše. Entity ID zůstávají stejná jako ve v1, dashboardy a automatizace fungují dál.
4. V dashboardu změň cesty obrázků z `/local/acond/` na `/acond_heatpump/`.

Stavy selectů jsou teď klíče nezávislé na jazyce: režim `auto` / `heat_pump` / `backup` / `off` / `cooling`, regulace `acondtherm` / `equitherm` / `manual`. Automatizace porovnávající staré české popisky je potřeba upravit.

---

## 🔢 Mapa registrů

Adresy v Modbus rámci jsou **od nuly** (`30001` → input `0`, `40001` → holding `0`). Teploty jsou `int16 × 10`, big endian.

| Registr | Adresa v HA | Význam | Entita |
|---|---|---|---|
| 30001 | input 0 | Okruh 1 žádaná | `sensor.acond_okruh_1_zadana` |
| 30002 | input 1 | Okruh 1 aktuální | `sensor.acond_okruh_1_aktualni` |
| 30003 | input 2 | Okruh 2 žádaná | `sensor.acond_okruh_2_zadana` |
| 30004 | input 3 | Okruh 2 aktuální | `sensor.acond_okruh_2_aktualni` |
| 30005 | input 4 | TUV žádaná | `sensor.acond_tuv_zadana` |
| 30006 | input 5 | TUV aktuální | `sensor.acond_tuv_aktualni` |
| 30007 | input 6 | `TC_status` bitové pole | `sensor.acond_tc_status` → binární senzory |
| 30008 | input 7 | Zpátečka žádaná | `sensor.acond_zpatecka_zadana` |
| 30009 | input 8 | Zpátečka aktuální | `sensor.acond_zpatecka_aktualni` |
| 30010 | input 9 | Venkovní teplota | `sensor.acond_venkovni_teplota` |
| 30014 | input 13 | Režim (0 automat, 1 TČ, 3 bivalence, 4 vyp, 5 manuál, 6 chlazení) | `sensor.acond_rezim` |
| 30015 | input 14 | Regulace (0 AcondTherm, 1 ekviterm, 2 manuál) | `sensor.acond_typ_regulace` |
| 30016 | input 15 | Solanka (země/voda) | `sensor.acond_solanka` |
| 30017 | input 16 | Čítač komunikace 0–255 | `sensor.acond_heartbeat` |
| 30018 | input 17 | Výstupní voda | `sensor.acond_vystupni_voda` |
| 40001 | holding 0 | Okruh 1 žádaná (zápis) | `climate.acond_okruh_1` |
| 40005 | holding 4 | TUV žádaná (zápis) | `climate.acond_tuv` |
| 40006 | holding 5 | `TC_set` bity režimu (zápis) | `select.acond_rezim_tc`, `sensor.acond_tc_set_raw` (ve výchozím stavu vypnutý) |
| 40007 | holding 6 | Typ regulace (zápis) | `select.acond_typ_regulace` |
| 40008 | holding 7 | Žádaná zpátečka – manuál (zápis) | `number.acond_zpatecka_manual` |

Bity `TC_status`: `0` zapnuto · `1` kompresor · `2` porucha · `3` TUV · `4` oběh 1 · `8` odtávání · `9` bivalence · `10` léto · `12` chlazení.

---

## ⚠️ Poznámky

- Entity ID jsou pevná (např. `sensor.acond_tuv_aktualni`), aby dashboard fungoval v libovolném jazyce. Zobrazované názvy se řídí jazykem HA (čeština/angličtina). Při přejmenování entit uprav dashboard.
- Zápisy (`climate`, `select`, `number`) jdou přímo do TČ. Začni malými změnami.
- Po změně SVG zvyš v dashboardu `?v=`, jinak prohlížeč použije starou verzi z cache (obrázky se cachují).
- Entity okruhu 2 a solanky vzniknou jen po zapnutí v možnostech integrace.

---

## 📄 Licence

[MIT](LICENSE)

---

[![buy me a coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/jhoralek)
