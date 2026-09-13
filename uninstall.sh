#!/bin/bash
# Quita el tema Claude, Claude Light y el plugin Claude Aura.
set -euo pipefail
rm -rf "$HOME/.config/omarchy/themes/claude" "$HOME/.config/omarchy/themes/claude-light" "$HOME/.config/omarchy/plugins/answer.claude-aura"
S="$HOME/.config/omarchy/shell.json"
if [[ -f $S ]] && command -v jq >/dev/null; then
  jq '.plugins = ((.plugins // []) | map(select(.id != "answer.claude-aura")))' "$S" > "$S.tmp" && mv "$S.tmp" "$S"
fi
echo "Tema y plugin eliminados. Elige otro tema con: omarchy theme set <nombre>"
