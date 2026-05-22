#!/usr/bin/env bash
set -euo pipefail

BENCH_DIR="${BENCH_DIR:-/home/frappe/frappe-bench}"
APP_DIR="${APP_DIR:-$BENCH_DIR/apps/mining_pm}"
SITE="${FRAPPE_SITE:-mining.local}"
UPSTREAM_REMOTE="${UPSTREAM_REMOTE:-upstream}"
UPSTREAM_BRANCH="${UPSTREAM_BRANCH:-main}"
STATE_FILE="${STATE_FILE:-/var/lib/mining-pm/last_good_commit}"
HEALTH_URL="${HEALTH_URL:-http://localhost/}"
ROLLBACK_DISABLED="${ROLLBACK_DISABLED:-0}"

send_feishu() {
  local text="$1"
  if [ -z "${FEISHU_WEBHOOK:-}" ]; then
    echo "[deploy] FEISHU_WEBHOOK not set, skip notification: $text"
    return
  fi

  python - "$FEISHU_WEBHOOK" "$text" <<'PY'
import json
import sys
import urllib.request

webhook, text = sys.argv[1], sys.argv[2]
payload = json.dumps({"msg_type": "text", "content": {"text": text}}).encode()
request = urllib.request.Request(
    webhook,
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
urllib.request.urlopen(request, timeout=10).read()
PY
}

run_migrate() {
  cd "$BENCH_DIR"
  bench --site "$SITE" migrate
}

health_check() {
  local status
  status="$(curl -fsS --max-time 10 -o /dev/null -w "%{http_code}" "$HEALTH_URL")"
  echo "[deploy] Health check $HEALTH_URL -> $status"
  [ "$status" = "200" ]
}

rollback() {
  local target_commit="$1"
  local reason="$2"

  if [ "$ROLLBACK_DISABLED" = "1" ]; then
    echo "[deploy] Rollback disabled; original failure: $reason" >&2
    send_feishu "❌ 部署失败且自动回滚已禁用。失败 commit: $target_commit，原因: $reason"
    exit 1
  fi

  if [ ! -s "$STATE_FILE" ]; then
    echo "[deploy] $STATE_FILE missing or empty; cannot determine rollback target" >&2
    send_feishu "❌ 部署失败且无法回滚：last_good_commit 丢失或为空。失败 commit: $target_commit"
    exit 1
  fi

  local last_good
  last_good="$(cat "$STATE_FILE" | tr -d '[:space:]')"
  if ! git -C "$APP_DIR" rev-parse --verify --quiet "$last_good^{commit}" >/dev/null; then
    echo "[deploy] last_good_commit is invalid: $last_good" >&2
    send_feishu "❌ 部署失败且无法回滚：last_good_commit 无效 ($last_good)。失败 commit: $target_commit"
    exit 1
  fi

  echo "[deploy] Rolling back from $target_commit to $last_good because: $reason"
  git -C "$APP_DIR" reset --hard "$last_good"

  run_migrate
  health_check

  send_feishu "⚠️ 部署失败已回滚到 $last_good，失败 commit 为 $target_commit"
  exit 1
}

main() {
  [ -d "$APP_DIR/.git" ] || {
    echo "[deploy] $APP_DIR is not a git repository" >&2
    exit 1
  }

  cd "$APP_DIR"
  git fetch "$UPSTREAM_REMOTE"
  git reset --hard "$UPSTREAM_REMOTE/$UPSTREAM_BRANCH"

  local target_commit
  target_commit="$(git rev-parse --short HEAD)"
  echo "[deploy] Deploying $target_commit"

  run_migrate || rollback "$target_commit" "bench migrate failed"
  health_check || rollback "$target_commit" "health check failed"

  printf '%s\n' "$target_commit" > "$STATE_FILE"
  send_feishu "✅ 部署成功: $target_commit"
  echo "[deploy] Success: $target_commit"
}

main "$@"
