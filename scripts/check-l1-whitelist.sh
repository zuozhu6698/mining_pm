#!/usr/bin/env bash
set -euo pipefail
shopt -s globstar

if [ "$#" -eq 0 ]; then
  echo "No changed files provided" >&2
  exit 1
fi

is_allowed() {
  local path="$1"

  case "$path" in
    *.json)
      return 1
      ;;
    docs/**|scripts/**|.github/workflows/**|.github/PULL_REQUEST_TEMPLATE.md|README.md|AGENTS.md|mining_pm/mining_pm/mining_pm/translations/**)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

blocked=()
for changed_file in "$@"; do
  if ! is_allowed "$changed_file"; then
    blocked+=("$changed_file")
  fi
done

if [ "${#blocked[@]}" -gt 0 ]; then
  echo "L1 whitelist rejected these files:" >&2
  printf '  - %s\n' "${blocked[@]}" >&2
  exit 1
fi

echo "All files are within the L1 whitelist."
