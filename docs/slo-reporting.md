# SLO-linked reporting

Experiment and GameDay reports include **SLO probe results** with an overall **PASS/FAIL** verdict.

## Reports

| Command | Output |
|---------|--------|
| `python3 scripts/quickstart_report.py` | `reports/latest.json` |
| `python3 scripts/gameday.py quickstart` | `reports/gameday-quickstart.json` |
| `make quickstart` | Runs quickstart report after pod-delete |

## Report shape (experiment)

```json
{
  "report_type": "experiment",
  "experiment": "pod-delete",
  "hypothesis": "Deployment restores desired replicas...",
  "verdict": "PASS",
  "recovery_seconds": 38.5,
  "probes": [
    {
      "name": "deployment_recovery",
      "type": "deployment_ready",
      "verdict": "PASS",
      "message": "deployment/flask-app ready 3/3 (min 3)"
    }
  ]
}
```

## Probe types

Defined per experiment in [`experiments/catalog.yaml`](../experiments/catalog.yaml) under `slo:`.

| Type | Description |
|------|-------------|
| `deployment_ready` | Wait until Deployment has `min_ready_replicas` within `max_recovery_seconds` |
| `pods_ready_ratio` | Fraction of pods matching `label_selector` that are Ready |
| `prometheus` | PromQL query vs threshold (optional if Prometheus unavailable) |

### Prometheus probes (optional)

```bash
export PROMETHEUS_SLO_ENABLED=true
export PROMETHEUS_URL=http://localhost:9090
python3 scripts/quickstart_report.py --experiment pod-delete
```

If Prometheus is down, optional probes show `SKIP`; required probes fail.

Configuration defaults: [`config/slo.yaml`](../config/slo.yaml).

## Hypothesis registry

Each catalog entry includes a `hypothesis` string describing the expected resilient behavior. Reports attach this for audit trails and GameDay readouts.

## Extend SLOs

Add probes to an experiment in `catalog.yaml`:

```yaml
  - name: my-experiment
    hypothesis: Service recovers within 90s
    slo:
      - name: deployment_recovery
        type: deployment_ready
        min_ready_replicas: 3
        max_recovery_seconds: 90
```

No code changes required unless adding a new probe `type` in `scripts/utils/slo.py`.
