# Contributing

Thanks for helping with the Acond Heat Pump integration! 🇨🇿 Příspěvky v češtině jsou vítány.

## Reporting bugs
Open an [issue](https://github.com/JH-Soft-Technology/acond-heatpump-ha/issues/new/choose) and include:
- Home Assistant and integration version
- heat pump model and firmware version (shown in the heat pump web interface)
- relevant log lines (enable debug logging for `custom_components.acond_heatpump`)

## Development
```bash
python -m venv .venv && . .venv/bin/activate
pip install pytest-homeassistant-custom-component
pytest
```
Tests run against a simulated heat pump (`tests/conftest.py`), no hardware needed.

## Pull requests
- One topic per pull request, branch from `main`.
- Keep `strings.json`, `translations/en.json` and `translations/cs.json` in sync when adding entities.
- Add or update tests for behaviour changes and make sure `pytest` passes.
- Update `CHANGELOG.md`; bump `version` in `manifest.json` only in release PRs.
- CI (HACS validation, hassfest, tests) must be green.

## Writing to the heat pump
Writes go to holding registers that change how the heat pump runs. Keep values within the ranges from the Acond documentation and never add automatic writes without an explicit user action.
