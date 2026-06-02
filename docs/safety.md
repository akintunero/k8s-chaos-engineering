# Safety and blast-radius controls

Chaos experiments can affect running workloads. This project provides **profiles**, **pre-flight checks**, and an **abort** command to reduce risk.

## Profiles (`CHAOS_ENV`)

Configured in [`config/blast-radius.yaml`](../config/blast-radius.yaml):

| Profile | Use case | Typical experiments |
|---------|----------|---------------------|
| `dev` | Local / quickstart | Most experiments |
| `staging` | Pre-prod | pod-delete, network-latency, cpu/memory hog |
| `prod` | Restricted | pod-delete only + `CHAOS_CONFIRM=yes` |

```bash
export CHAOS_ENV=staging
make list-experiments
python3 scripts/chaos-runner.py run pod-delete
```

Production example:

```bash
export CHAOS_ENV=prod
export CHAOS_CONFIRM=yes
python3 scripts/preflight.py
python3 scripts/chaos-runner.py run pod-delete
```

## Pre-flight

Validates before `run`:

- Cluster reachable
- Litmus pods present
- Quickstart app deployment healthy
- No existing `ChaosEngine` in target namespace

```bash
make preflight
# or
python3 scripts/preflight.py
```

Skip (not recommended):

```bash
SKIP_PREFLIGHT=1 python3 scripts/chaos-runner.py run pod-delete
```

## Abort (kill switch)

Stop and delete all `ChaosEngine` resources in the app namespace:

```bash
make abort
# or
python3 scripts/chaos-runner.py abort
python3 scripts/abort.py --namespace hello-world-app
```

Cluster-wide (dev/staging profiles only):

```bash
python3 scripts/abort.py --all-namespaces
```

## Blocked namespaces

Each profile blocks system namespaces (e.g. `kube-system`). Running chaos against a blocked namespace fails fast with a clear error.

## Web UI

When `CHAOS_API_KEY` is set, API requests must send header `X-Api-Key`. Configure `CORS_ORIGINS` (for example `http://localhost:3000` for the web UI).

See [web/README.md](../web/README.md).
