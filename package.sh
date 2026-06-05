#!/bin/bash
set -e

cd "$(dirname "$0")"

DATE=$(date +%Y%m%d)
ZIP="dist/pm-skill-${DATE}.zip"

echo "==> Checking for secrets..."

SECRET_PATTERNS=(
  'sk-[a-zA-Z0-9]{32,}'
  'api_key\s*=\s*"[^"]{20,}"'
  'api_key_env\s*=\s*"[^"]{20,}"'
  'ANTHROPIC_API_KEY\s*=\s*"[^"]{20,}"'
  'OPENAI_API_KEY\s*=\s*"[^"]{20,}"'
  '[a-zA-Z0-9+/]{40,}={0,2}'
)

FOUND=0
for pattern in "${SECRET_PATTERNS[@]}"; do
  for f in SKILL.md README.md references/**/*.md references/**/**/*.md commands/**/*.md workflows/*.md templates/*.md templates/*.json; do
    [ -f "$f" ] || continue
    matched=$(grep -nE "$pattern" "$f" 2>/dev/null | grep -vE '(https?://|gist\.github|github\.com|\{[a-zA-Z]|^\|.*\{|`.*\{)' || true)
    if [ -n "$matched" ]; then
      echo "  [!] SUSPECT: $f"
      echo "$matched" | head -3
      FOUND=1
    fi
  done
done

if [ "$FOUND" -eq 1 ]; then
  echo ""
  echo "SECRETS DETECTED. Remove them before packaging."
  exit 1
fi

echo "  OK — no secrets found"

mkdir -p dist
rm -f "$ZIP"

zip -r "$ZIP" \
  SKILL.md \
  README.md \
  commands/ \
  workflows/ \
  templates/ \
  references/ \
  design/ \
  -x "*.pyc" "__pycache__/*" ".git/*" ".DS_Store" "*.zip"

SIZE=$(du -h "$ZIP" | cut -f1)
COUNT=$(unzip -l "$ZIP" | tail -1 | awk '{print $2}')
echo "==> Created: $ZIP ($SIZE, $COUNT files)"
