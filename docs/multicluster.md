# Multi-cluster chaos

Run experiments or GameDays across **registered clusters** with guardrails.

## Cluster registry

Copy and edit:

```bash
cp config/clusters.yaml.example config/clusters.yaml
```

Each cluster entry:

| Field | Purpose |
|-------|---------|
| `name` | Logical name for CLI |
| `context` | kubectl context |
| `chaos_env` | Blast-radius profile (`dev`, `staging`, `prod`) |
| `allowed_experiments` | Optional allow-list (empty = use `CHAOS_ENV` rules only) |
| `enabled` | Skip when false |

Policies block `prod` unless `allow_prod: true` and `CHAOS_CONFIRM=yes`.

## CLI

```bash
k8s-chaos list --clusters
k8s-chaos clusters                          # list registered
k8s-chaos clusters local --experiment pod-delete
k8s-chaos clusters staging-primary --gameday quickstart
k8s-chaos run pod-delete --cluster local
k8s-chaos gameday quickstart --cluster staging-primary
```

## Reports

Multi-cluster GameDay writes `reports/multicluster-<workflow>.json` with per-cluster verdicts.

## Production guardrails

```bash
# Blocked by default:
k8s-chaos clusters prod-primary --experiment pod-delete

# Explicit opt-in:
export CHAOS_CONFIRM=yes
k8s-chaos clusters prod-primary --experiment pod-delete --allow-prod
```

Enable prod cluster in `config/clusters.yaml` (`enabled: true`) only when policies allow.

## Context switching

The runner uses `kubectl config use-context` and restores the previous context after each cluster.
