#!/usr/bin/env bash
set -euo pipefail

STATE_DIR="${MINING_PM_STATE_DIR:-/var/lib/mining-pm}"
STATE_FILE="$STATE_DIR/last_good_commit"
APP_DIR="${MINING_PM_APP_DIR:-/home/frappe/frappe-bench/apps/mining_pm}"
STATE_OWNER="${MINING_PM_STATE_OWNER:-frappe:frappe}"

if [ "$(id -u)" -ne 0 ]; then
  echo "This installer must run as root because it writes $STATE_DIR" >&2
  exit 1
fi

mkdir -p "$STATE_DIR"
chown "$STATE_OWNER" "$STATE_DIR"

if [ ! -f "$STATE_FILE" ]; then
  if [ -d "$APP_DIR/.git" ]; then
    current_commit="$(git -C "$APP_DIR" rev-parse --short HEAD)"
  else
    current_commit="$(git rev-parse --short HEAD)"
  fi
  printf '%s\n' "$current_commit" > "$STATE_FILE"
  echo "Initialized $STATE_FILE to $current_commit"
else
  echo "$STATE_FILE already exists: $(cat "$STATE_FILE")"
fi

chown "$STATE_OWNER" "$STATE_FILE"
chmod 664 "$STATE_FILE"
