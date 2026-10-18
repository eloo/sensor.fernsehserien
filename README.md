# Fernsehserien.de für Home Assistant

Die Integration liest kommende Folgen von [fernsehserien.de](https://www.fernsehserien.de/) aus und stellt sie als Sensorattribut `data` für die Upcoming Media Card bereit.

## Installation

1. Installiere das Repository über HACS als benutzerdefiniertes Repository (Kategorie **Integration**) oder kopiere `custom_components/fernsehserien` nach `config/custom_components/fernsehserien`.
2. Starte Home Assistant neu.
3. Öffne **Einstellungen → Geräte & Dienste → Integration hinzufügen**, suche **Fernsehserien.de**.
4. Trage die Slugs ein, die im Serienpfad von fernsehserien.de stehen, zum Beispiel `breaking-bad`.

Die Integration erzeugt einen aggregierten Sensor `sensor.fernsehserien_upcoming_media`. Er enthält weiterhin das JSON-Attribut `data` für die Upcoming Media Card. Standardmäßig erfolgt die Aktualisierung alle sechs Stunden (`scan_interval: 21600`) mit bis zu zwei Folgen je Serie (`max_per_show: 2`).

## Serien verwalten

Öffne unter **Einstellungen → Geräte & Dienste** den Integrationseintrag und wähle **Optionen**. Eine Serie pro Zeile: neue Slugs ergänzen, Zeilen löschen, um Serien zu entfernen. Dort kannst du auch `scan_interval` in Sekunden (mindestens 60) und `max_per_show` (1–50) einstellen. Änderungen werden gespeichert und der Sensor automatisch neu geladen. Doppelte Slugs werden zusammengeführt.

## Umstieg von YAML

Die alte YAML-Sensorplattform wird nicht mehr geladen. Entferne deren `sensor:`-Konfiguration (insbesondere `platform: fernsehserien_upcoming_media`) aus deiner YAML-Datei, starte Home Assistant neu und richte die Integration über die UI ein. Übertrage die Werte aus `showNames` als Slugs in den Einrichtungsdialog sowie `scan_interval` und `max_per_show` in die entsprechenden Felder. Vorhandene Sensor-Entitäten können nach dem Umstieg in der Entitätenverwaltung bereinigt werden.

## Lokale Entwicklung und Tests

[UV](https://docs.astral.sh/uv/) installieren, dann im Repository ausführen:

```sh
uv sync
uv run pytest
uv run ruff check .
```

`uv sync` erstellt oder aktualisiert `.venv` und installiert die in `pyproject.toml` definierten Entwicklungsabhängigkeiten. `uv.lock` hält deren Versionen reproduzierbar fest. Die Tests verwenden simulierte Antworten und benötigen keinen Zugriff auf fernsehserien.de.

Für bequeme Standardaufgaben [go-task](https://taskfile.dev/) installieren. `task` führt alle Prüfungen aus; einzelne Aufgaben: `task dependencies`, `task lint` oder `task test`. Die Dependency-Prüfung vergleicht die Python-Pakete samt Versionsangaben aus `manifest.json` mit den UV-Entwicklungsabhängigkeiten.