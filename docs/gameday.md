# GameDay orchestration

Run ordered chaos scenarios with **pass/fail gates** between steps. Each experiment step runs SLO probes from the [experiment catalog](../experiments/catalog.yaml).

## List GameDays

```bash
python3 scripts/gameday.py --list
# or
make gameday-list
```

Built-in workflows:

| Name | Description |
|------|-------------|
| `quickstart` | Baseline probe + pod-delete |
| `resilience-basics` | Baseline → pod-delete → cooldown → network-latency |

## Run a GameDay

```bash
export CHAOS_ENV=dev
make preflight
make gameday GAMEDAY=quickstart
```

Report written to `reports/gameday-<name>.json`.

## Workflow format

Workflows live in `workflows/gameday/*.yaml`:

```yaml
name: quickstart
namespace: hello-world-app
deployment: flask-app
expected_replicas: 3

steps:
  - id: baseline
    type: probe
    probes: [...]

  - id: pod-delete
    type: experiment
    experiment: pod-delete
    chaos_wait_seconds: 45
    recovery_timeout_seconds: 120
    cleanup: true

  - id: cooldown
    type: wait
    seconds: 20
```

### Step types

| Type | Purpose |
|------|---------|
| `probe` | Steady-state / baseline SLO checks |
| `experiment` | Run Litmus experiment + SLO evaluation + optional cleanup |
| `wait` | Cooldown between experiments |

### Options

- `skip_if_chaos_env: [prod]` — skip step in given profiles
- `cleanup: true` — delete ChaosEngine after step (default for experiments)

## CI

Use in pipeline after cluster bootstrap:

```bash
SKIP_LITMUS=0 make quickstart  # or deploy app + litmus separately
make gameday GAMEDAY=quickstart
```

See [slo-reporting.md](slo-reporting.md) for probe details.
