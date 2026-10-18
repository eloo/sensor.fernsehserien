This repository contains a Home Assistant HACS integration.

Requirements:

- Async only
- Config Flow only
- DataUpdateCoordinator pattern
- Strict typing
- Ruff clean
- Home Assistant quality scale compliance

Always generate:

- diagnostics.py
- translations
- tests
- README updates
- manifest.json updates

Never use:

- requests
- blocking I/O
- thread-based polling

Prefer existing Home Assistant helpers and APIs over custom implementations.