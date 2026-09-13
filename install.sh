#!/bin/bash
# Instala el tema Claude (oscuro y claro) y el plugin animado "Claude Aura" en Omarchy.
#
# Uso:
#   git clone https://github.com/answer2002/omarchy-claude-theme
#   cd omarchy-claude-theme && ./install.sh
#
# Copia los ficheros (sin .git) a ~/.config/omarchy/themes/, así Omarchy trata el tema
# como escrito por ti y conserva hyprland.lua (bordes que giran, animaciones, blur).
# Un `omarchy theme install <url>` también funciona, pero descarta el hyprland.lua.
set -euo pipefail
cd "$(dirname "$0")"

THEMES="$HOME/.config/omarchy/themes"
PLUGINS="$HOME/.config/omarchy/plugins"
SHELL_JSON="$HOME/.config/omarchy/shell.json"
PLUGIN_ID="answer.claude-aura"

echo "→ Tema Claude (oscuro)"
mkdir -p "$THEMES/claude/backgrounds"
cp colors.toml shell.toml hyprland.lua icons.theme unlock.png preview.png "$THEMES/claude/"
cp backgrounds/*.png "$THEMES/claude/backgrounds/"

echo "→ Tema Claude Light"
mkdir -p "$THEMES/claude-light/backgrounds"
cp light/colors.toml light/shell.toml light/hyprland.lua light/icons.theme light/unlock.png light/preview.png "$THEMES/claude-light/"
cp light/backgrounds/*.png "$THEMES/claude-light/backgrounds/"
cp backgrounds/03-claude-terracotta-bloom.png "$THEMES/claude-light/backgrounds/02-claude-terracotta-bloom.png"
cp backgrounds/01-claude-ember.png "$THEMES/claude-light/backgrounds/03-claude-ember.png"

if [[ ${1:-} != "--no-aura" ]]; then
  echo "→ Plugin Claude Aura (Clawds paseando por el escritorio)"
  mkdir -p "$PLUGINS/$PLUGIN_ID/assets"
  cp aura/manifest.json aura/Aura.qml "$PLUGINS/$PLUGIN_ID/"
  cp aura/assets/*.png "$PLUGINS/$PLUGIN_ID/assets/"

  if [[ -f $SHELL_JSON ]] && command -v jq >/dev/null; then
    if ! jq -e --arg id "$PLUGIN_ID" '.plugins[]? | select(.id == $id)' "$SHELL_JSON" >/dev/null; then
      jq --arg id "$PLUGIN_ID" '.plugins = ((.plugins // []) + [{id: $id}])' "$SHELL_JSON" > "$SHELL_JSON.tmp" \
        && mv "$SHELL_JSON.tmp" "$SHELL_JSON"
      echo "  activado en shell.json"
    fi
  else
    echo "  ⚠ añade {\"id\": \"$PLUGIN_ID\"} a \"plugins\" en $SHELL_JSON"
  fi
fi

echo "→ Aplicando tema"
if command -v omarchy-theme-set >/dev/null; then
  omarchy-theme-set claude
  # El plugin registra su IPC al arrancar el shell; un reinicio lo deja listo.
  command -v omarchy-restart-shell >/dev/null && omarchy-restart-shell || true
fi

echo
echo "Listo. Cambia de fondo con: omarchy theme bg next"
echo "Tema claro:               omarchy theme set claude-light"
echo "Estado de la animación:   omarchy-shell claude-aura status"
