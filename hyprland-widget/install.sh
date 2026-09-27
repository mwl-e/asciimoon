#!/usr/bin/env sh
# Installs the ASCIIMoon widget into ~/.local/share/asciimoon-widget
# and puts an `asciimoon-widget` command in ~/.local/bin.
set -eu

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/asciimoon-widget/app"
BIN="$HOME/.local/bin"

mkdir -p "$DEST/vendor" "$BIN"
cp "$SRC/asciimoon-widget.py" "$SRC/widget.html" "$DEST/"
cp "$SRC/vendor/suncalc.js" "$SRC/vendor/SUNCALC-LICENSE" "$DEST/vendor/"
chmod +x "$DEST/asciimoon-widget.py"
ln -sf "$DEST/asciimoon-widget.py" "$BIN/asciimoon-widget"

echo "Installed. Add this to ~/.config/hypr/hyprland.conf:"
echo "  exec-once = $BIN/asciimoon-widget --position top-right"
