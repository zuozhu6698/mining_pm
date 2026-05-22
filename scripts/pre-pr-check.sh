#!/usr/bin/env bash
set -euo pipefail

REPORT_PATH="${PRE_PR_REPORT_PATH:-/tmp/pre-pr-report.md}"
REPORT_LINES=()

add_report() {
  REPORT_LINES+=("- [x] $1")
}

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

write_report() {
  {
    echo "## Pre-PR Check Report"
    printf '%s\n' "${REPORT_LINES[@]}"
  } > "$REPORT_PATH"
  echo "Report written to $REPORT_PATH"
}

check_json_schema() {
  echo "== JSON schema =="
  local count=0
  local found=0
  while IFS= read -r json_file; do
    found=1
    echo "Validating $json_file"
    python scripts/validate-doctype.py "$json_file"
    count=$((count + 1))
  done < <(find mining_pm/mining_pm/doctype -mindepth 2 -maxdepth 2 -name "*.json" | sort)

  [ "$found" -eq 1 ] || fail "No DocType JSON files found"
  add_report "JSON schema (${count} files OK)"
}

check_py_compile() {
  echo "== py_compile =="
  local count=0
  while IFS= read -r py_file; do
    echo "Compiling $py_file"
    python -m py_compile "$py_file"
    count=$((count + 1))
  done < <(git ls-files "*.py" | sort)

  add_report "py_compile (${count} files OK)"
}

check_patches_txt() {
  echo "== patches.txt consistency =="
  local count=0
  local patches_file="mining_pm/patches.txt"
  [ -f "$patches_file" ] || fail "$patches_file not found"

  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%%#*}"
    line="$(printf '%s' "$line" | xargs)"
    [ -n "$line" ] || continue

    local module_path="${line//./\/}.py"
    [ -f "$module_path" ] || fail "Patch module not found: $line -> $module_path"
    echo "Found patch $line"
    count=$((count + 1))
  done < "$patches_file"

  add_report "patches.txt consistency (${count} patches OK)"
}

check_fixtures_json() {
  echo "== fixtures JSON =="
  local count=0
  local found=0
  while IFS= read -r fixture_file; do
    found=1
    echo "Parsing $fixture_file"
    python -m json.tool "$fixture_file" > /dev/null
    count=$((count + 1))
  done < <(find mining_pm/mining_pm/fixtures -maxdepth 1 -name "*.json" | sort)

  [ "$found" -eq 1 ] || fail "No fixture JSON files found"
  add_report "fixtures JSON (${count} files OK)"
}

check_diff_stat() {
  echo "== diff stat =="
  if git rev-parse --verify main >/dev/null 2>&1; then
    git diff --stat main...HEAD || true
  else
    git diff --stat || true
  fi
  add_report "diff stat captured"
}

check_three_layer_structure() {
  echo "== three-layer structure guard =="
  [ -d "mining_pm" ] || fail "mining_pm app package missing"
  [ -f "mining_pm/hooks.py" ] || fail "mining_pm/hooks.py missing"
  [ -d "mining_pm/mining_pm" ] || fail "mining_pm/mining_pm module package missing"
  [ -d "mining_pm/mining_pm/doctype" ] || fail "mining_pm/mining_pm/doctype missing"
  [ ! -d "mining_pm/doctype" ] || fail "T015 类错误:不要扁平化目录结构"
  add_report "three-layer structure guard OK"
}

run_all() {
  check_json_schema
  check_py_compile
  check_patches_txt
  check_fixtures_json
  check_diff_stat
  check_three_layer_structure
  write_report
}

if [ "$#" -gt 0 ]; then
  for check_name in "$@"; do
    "$check_name"
  done
  write_report
else
  run_all
fi
