#!/bin/bash
# Package PM Skill to zip file
set -e

cd "$(dirname "$0")"
mkdir -p dist

DATE=$(date +%Y%m%d)
ZIP="dist/pm-skill-${DATE}.zip"
rm -f "$ZIP"

zip -r "$ZIP" \
  SKILL.md \
  README.md \
  references/ \
  wiki/ \
  -x "wiki/entities/*.md" "wiki/concepts/*.md" "wiki/index.md" "wiki/glossary.md" "wiki/log.md" \
  -x "*.pyc" "__pycache__/*" ".git/*" ".DS_Store"

SIZE=$(du -h "$ZIP" | cut -f1)
COUNT=$(unzip -l "$ZIP" | tail -1 | awk '{print $2}')
echo "Created: $ZIP ($SIZE, $COUNT files)"
