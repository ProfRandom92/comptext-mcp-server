#!/bin/bash

# Branch Cleanup Script for comptext-mcp-server
# This script deletes obsolete branches from the remote repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# List of branches to delete
branches_to_delete=(
  "copilot/fix-all-errors"
  "copilot/fix-functionality-issues"
  "copilot/fix-issues-in-backend"
  "copilot/fix-pull-request-24"
  "copilot/fix-server-configuration-issue"
  "copilot/fix-test-reference-issue"
  "copilot/create-sub-issue-for-issue-40"
  "v0/frauschnegg-4034-49317aa2"
)

echo -e "${YELLOW}=== Branch Deletion Script ===${NC}"
echo "This will delete ${#branches_to_delete[@]} branches from the remote repository."
echo ""
echo "Repository: ProfRandom92/comptext-mcp-server"
echo ""
echo -e "${RED}Branches to be deleted:${NC}"
for branch in "${branches_to_delete[@]}"; do
  echo "  - $branch"
done
echo ""
echo -e "${YELLOW}⚠️  WARNING: This action cannot be undone!${NC}"
echo ""
read -p "Are you sure you want to proceed? (yes/no): " confirmation

if [ "$confirmation" != "yes" ]; then
  echo -e "${YELLOW}Aborted.${NC}"
  exit 1
fi

echo ""
echo -e "${GREEN}Deleting branches...${NC}"
success_count=0
fail_count=0

for branch in "${branches_to_delete[@]}"; do
  echo -n "Deleting: $branch ... "
  if git push origin --delete "$branch" 2>/dev/null; then
    echo -e "${GREEN}✓ Success${NC}"
    ((success_count++))
  else
    echo -e "${RED}✗ Failed${NC}"
    ((fail_count++))
  fi
done

echo ""
echo -e "${GREEN}=== Cleanup Summary ===${NC}"
echo "Successfully deleted: $success_count branches"
echo "Failed to delete: $fail_count branches"
echo ""

if [ $success_count -gt 0 ]; then
  echo -e "${YELLOW}Next steps:${NC}"
  echo "1. Close associated pull requests on GitHub"
  echo "2. Run 'git fetch --all --prune' to update your local repository"
  echo "3. Run 'git remote prune origin' to remove stale remote-tracking branches"
  echo ""
fi

echo -e "${GREEN}Done!${NC}"
