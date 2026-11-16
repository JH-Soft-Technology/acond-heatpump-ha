# Changelog

Všechny významné změny v tomto projektu jsou dokumentovány zde.

Formát vychází z [Keep a Changelog](https://keepachangelog.com/),
projekt používá [sémantické verzování](https://semver.org/lang/cs/).

## [1.0.0] - 2026-11-16

### Přidáno
- YAML balíček `packages/acond.yaml`: Modbus TCP hub, senzory (input 30001–30018,
  holding 40006), termostaty okruhu 1 a TUV, binární senzory z bitů `TC_status`,
  `select` režimu TČ a typu regulace, `number` žádané zpátečky.
- Ilustrovaná záložka dashboardu se schématem systému a živými hodnotami
  (samostatná verze pro počítač a telefon, animace ventilátoru, upozornění na poruchu)
  a grafy teplot a provozu za 24 h.
