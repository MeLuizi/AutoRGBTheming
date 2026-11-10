#!/usr/bin/env bash

LUA_FILE="$HOME/.config/hypr/scheme/current.lua"
PYTHON_SCRIPT="$HOME/.local/bin/auto-victus-backlight.py"

python3 "$PYTHON_SCRIPT"
LAST_MOD=""

while true; do
    if [ -f "$LUA_FILE" ]; then
        CURRENT_MOD=$(stat -c %Y "$LUA_FILE" 2>/dev/null)
        if [ "$CURRENT_MOD" != "$LAST_MOD" ] && [ -n "$CURRENT_MOD" ]; then
            LAST_MOD="$CURRENT_MOD"
            python3 "$PYTHON_SCRIPT"
        fi
    fi
    sleep 0.5
done
