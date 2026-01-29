#!/bin/bash
# Branch Cleanup Script for comptext-mcp-server
# Erstellt am: 2026-01-29
# Beschreibung: Loescht veraltete und unnoetige Branches

set -e

echo "=== Branch Cleanup Script ==="
echo ""

# Farben fuer Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Branches die geloescht werden sollen
BRANCHES_TO_DELETE=(
    # Neuere copilot Branches (redundant/abgeschlossen)
    "copilot/remove-old-branches"
    "copilot/fix-server-configuration-issue"
    "copilot/release-comptext-version"
    "copilot/create-sub-issue-for-issue-40"
    "copilot/fix-all-errors"

    # Alte Session-basierte Branches
    "claude/update-mcp-integration-JpZH5"

    # Kryptische v0 Branches
    "v0/frauschnegg-4034-49317aa2"
    "v0/frauschnegg-4034-aa30de2f"

    # Veraltete copilot Branches (3+ Tage alt)
    "copilot/fix-functionality-issues"
    "copilot/fix-pull-request-24"
    "copilot/fix-issues-in-backend"
    "copilot/fix-test-reference-issue"
    "copilot/add-nl-to-comptext-tool"

    # Veraltete Dependabot Branches (6-8 Wochen alt)
    "dependabot/github_actions/actions/cache-5"
    "dependabot/github_actions/github/codeql-action-4"
    "dependabot/github_actions/actions/checkout-6"
    "dependabot/github_actions/docker/build-push-action-6"
    "dependabot/github_actions/actions/setup-python-6"
)

# Branches die BEHALTEN werden
BRANCHES_TO_KEEP=(
    "main"
)

echo -e "${GREEN}Branches die BEHALTEN werden:${NC}"
for branch in "${BRANCHES_TO_KEEP[@]}"; do
    echo "  - $branch"
done
echo ""

echo -e "${RED}Branches die GELOESCHT werden:${NC}"
for branch in "${BRANCHES_TO_DELETE[@]}"; do
    echo "  - $branch"
done
echo ""

# Bestaetigung anfordern
read -p "Moechtest du diese Branches wirklich loeschen? (ja/nein): " confirm
if [[ "$confirm" != "ja" ]]; then
    echo "Abgebrochen."
    exit 0
fi

echo ""
echo "Loesche Remote-Branches..."
echo ""

# Fetch um sicherzustellen, dass wir aktuell sind
git fetch --prune

deleted_count=0
skipped_count=0

for branch in "${BRANCHES_TO_DELETE[@]}"; do
    # Pruefen ob der Branch existiert
    if git ls-remote --heads origin "$branch" | grep -q "$branch"; then
        echo -e "${YELLOW}Loesche:${NC} $branch"
        if git push origin --delete "$branch" 2>/dev/null; then
            echo -e "  ${GREEN}Erfolgreich geloescht${NC}"
            ((deleted_count++))
        else
            echo -e "  ${RED}Fehler beim Loeschen${NC}"
        fi
    else
        echo -e "  Uebersprungen (existiert nicht): $branch"
        ((skipped_count++))
    fi
done

echo ""
echo "=== Zusammenfassung ==="
echo -e "${GREEN}Geloescht:${NC} $deleted_count Branches"
echo -e "${YELLOW}Uebersprungen:${NC} $skipped_count Branches"
echo ""

# Lokale Referenzen aufraumen
echo "Raeume lokale Referenzen auf..."
git remote prune origin

echo ""
echo -e "${GREEN}Fertig!${NC}"
echo ""
echo "Verbleibende Branches:"
git branch -r | grep -v HEAD
