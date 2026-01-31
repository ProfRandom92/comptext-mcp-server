# Branch-Strategie

## Aktive Branches

| Branch | Beschreibung | Status |
|--------|--------------|--------|
| `main` | Produktions-Branch mit stabilem Code | Aktiv |

## Branch-Namenskonventionen

### Feature Branches
- Format: `feature/<beschreibung>`
- Beispiel: `feature/add-user-authentication`

### Bugfix Branches
- Format: `fix/<beschreibung>`
- Beispiel: `fix/memory-leak-in-parser`

### Release Branches
- Format: `release/<version>`
- Beispiel: `release/2.1.0`

### Temporaere Branches (automatisch erstellt)
- `claude/*` - Claude Code Session-Branches (werden nach Merge geloescht)
- `copilot/*` - GitHub Copilot Branches (werden nach Merge geloescht)
- `dependabot/*` - Automatische Dependency Updates

## Aufraeum-Richtlinien

1. **Nach jedem PR-Merge**: Branch loeschen
2. **Woechentliche Pruefung**: Veraltete Branches identifizieren
3. **Automatische Branches**: Nach 7 Tagen ohne Aktivitaet loeschen

## Cleanup-Script

Ein Cleanup-Script ist verfuegbar unter:
```bash
./scripts/cleanup-branches.sh
```

Das Script:
- Listet alle zu loeschenden Branches auf
- Fragt nach Bestaetigung
- Loescht veraltete Remote-Branches
- Raeumt lokale Referenzen auf

## Branch-Schutzregeln

Der `main` Branch sollte folgende Schutzregeln haben:
- Require pull request reviews
- Require status checks to pass
- No force pushes
- No deletions
