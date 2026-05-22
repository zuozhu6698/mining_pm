# Deployment Operations

## Rollback State

The deploy script stores the last known good commit in:

```bash
/var/lib/mining-pm/last_good_commit
```

Initialize the state file on the 180 server:

```bash
sudo bash /home/frappe/frappe-bench/apps/mining_pm/scripts/install-rollback-state.sh
```

The installer is idempotent. If the file already exists, it leaves the existing
commit untouched.

## Manual Scenarios

Reset `last_good_commit` when you intentionally want an older rollback target:

```bash
cd /home/frappe/frappe-bench/apps/mining_pm
git rev-parse --short HEAD
echo "<known-good-commit>" | sudo tee /var/lib/mining-pm/last_good_commit
sudo chown frappe:frappe /var/lib/mining-pm/last_good_commit
```

Disable automatic rollback during debugging:

```bash
ROLLBACK_DISABLED=1 /usr/local/bin/deploy-mining-pm.sh
```

Re-enable rollback by running the script without `ROLLBACK_DISABLED=1`.

Inspect a failed deploy without changing code:

```bash
journalctl -u cron --since "1 hour ago"
cat /var/lib/mining-pm/last_good_commit
cd /home/frappe/frappe-bench/apps/mining_pm && git log --oneline -5
```

## Local Rollback Test Plan

This repository cannot run the 180 bench services locally. To validate rollback
logic without touching production:

```bash
tmp_state="$(mktemp -d)"
STATE_FILE="$tmp_state/last_good_commit" \
BENCH_DIR="/home/frappe/frappe-bench" \
APP_DIR="/home/frappe/frappe-bench/apps/mining_pm" \
ROLLBACK_DISABLED=1 \
bash scripts/deploy-mining-pm.sh
```

On the 180 server, validate for real by setting `last_good_commit` to the current
healthy commit, temporarily deploying a known-bad branch, and confirming the
script resets back to the stored commit. Do not keep `ROLLBACK_DISABLED=1` set
for scheduled deploys.
