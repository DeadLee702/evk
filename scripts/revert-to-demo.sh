#!/usr/bin/env bash
set -euo pipefail

# Revert-to-demo.sh
# Restore repository files to the state at commit e135950aa3f78c165dadbfc8d9c45ae40d31bd91
# This script creates new commits that restore critical files to their demo-ready state.

# Files to restore and their source commit (e135950aa3f78c165...)
REV_COMMIT="e135950aa3f78c165dadbfc8d9c45ae40d31bd91"

# Ensure we're at repo root
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Check git status clean
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Please commit or stash your changes before running this script." >&2
  exit 1
fi

# Files to restore
FILES=(
  "Cargo.toml"
  "src/hardware_trust_tpm.rs"
  "src/lib.rs"
  ".github/workflows/demo.yml"
)

# For each file, restore its contents from REV_COMMIT if present; otherwise remove it if it didn't exist
for f in "${FILES[@]}"; do
  if git ls-tree -r --name-only "$REV_COMMIT" | grep -q "^$f$"; then
    echo "Restoring $f from $REV_COMMIT"
    git show "$REV_COMMIT:$f" > "$f"
  else
    echo "Removing $f (not present in $REV_COMMIT)"
    if [[ -f "$f" ]]; then
      git rm -f "$f"
    fi
  fi
done

# Commit the restored state
git add -A
if git diff --staged --quiet; then
  echo "No changes to commit — repository already at desired state.";
else
  git commit -m "revert: restore repository to demo state at ${REV_COMMIT}";
  git push origin HEAD
fi

echo "Restore complete. If any step failed due to permissions, apply the diffs manually."