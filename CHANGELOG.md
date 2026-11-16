# Changelog

Všechny významné změny v tomto projektu jsou dokumentovány zde.

Formát vychází z [Keep a Changelog](https://keepachangelog.com/),
projekt používá [sémantické verzování](https://semver.org/lang/cs/).

## [2.0.0] - 2026-11-16

### Změněno
- Projekt je nově **integrace pro HACS** (`custom_components/acond_heatpump`) místo YAML balíčku:
  nastavení přes UI (adresa, port, Modbus ID, interval čtení, volitelný 2. okruh a solanka),
  vlastní Modbus TCP klient bez dalších Python závislostí, čtení všech registrů dvěma dotazy.
- Stavy selectů jsou klíče nezávislé na jazyce (`auto`, `heat_pump`, … / `acondtherm`, `equitherm`, `manual`),
  zobrazované názvy jsou přeložené (čeština, angličtina).
- SVG pro dashboard servíruje integrace na `/acond_heatpump/…`, kopírování do `/config/www` odpadá.
- YAML balíček přesunut do `legacy/packages/acond.yaml`.

### Přidáno
- Termostat a senzory 2. okruhu, oběh okruhu 2 a solanky (volitelně), stav topí/nečinný u termostatů.
- Ikona integrace (`brand/`), HACS metadata, GitHub Actions (HACS, hassfest, testy), testy proti simulovanému TČ.

## [1.0.0] - 2026-11-16

### Přidáno
- YAML balíček `packages/acond.yaml`: Modbus TCP hub, senzory (input 30001–30018,
  holding 40006), termostaty okruhu 1 a TUV, binární senzory z bitů `TC_status`,
  `select` režimu TČ a typu regulace, `number` žádané zpátečky.
- Ilustrovaná záložka dashboardu se schématem systému a živými hodnotami
  (samostatná verze pro počítač a telefon, animace ventilátoru, upozornění na poruchu)
  a grafy teplot a provozu za 24 h.
