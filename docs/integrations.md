# Integrations

## Installable CLI

```bash
make install   # from a git clone; or: pip install k8s-chaos-engineering
k8s-chaos doctor
k8s-chaos list
k8s-chaos run pod-delete
k8s-chaos gameday quickstart
k8s-chaos report pod-delete
k8s-chaos abort
```

## GitHub Action v2

Composite action [`.github/actions/chaos-test`](../.github/actions/chaos-test):

```yaml
- uses: ./.github/actions/chaos-test
  with:
    mode: gameday          # experiment | gameday
    gameday: quickstart
    chaos-env: dev
    upload-report: "true"
```

Outputs: `verdict`, `report-file`

Example workflow: [`.github/workflows/example-chaos-smoke.yml`](../.github/workflows/example-chaos-smoke.yml)

## HTTP API v1

Stable routes under `/api/v1`:

| Method | Path |
|--------|------|
| GET | `/api/v1/health` |
| GET | `/api/v1/experiments` |
| POST | `/api/v1/experiments/run` |
| POST | `/api/v1/experiments/{name}/stop` |
| GET | `/api/v1/config` |

Legacy routes under `/api/*` remain for the web UI.

Optional auth: `CHAOS_API_KEY` + header `X-Api-Key`.

## Notifications

Enable Slack/webhook on GameDay completion:

```bash
export NOTIFICATIONS_ENABLED=true
export SLACK_WEBHOOK_URL=https://hooks.slack.com/...
k8s-chaos gameday quickstart
```

## Plugins

See [plugins.md](plugins.md).

## Multi-cluster

See [multicluster.md](multicluster.md).
