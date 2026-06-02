# Chaos Engineering Web UI

React + FastAPI dashboard for Litmus chaos experiments.

> **Beta** — Docker Compose supported. See [EXPERIMENTAL.md](EXPERIMENTAL.md).

## Quick start

```bash
make web-up    # from repository root
```

## Features

- List experiments (respects `CHAOS_ENV` profile)
- Run / stop experiments
- Schedule experiments (CronJob-based)
- WebSocket status channel
- Optional API key auth

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CHAOS_ENV` | `dev` | Blast-radius profile |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed browser origins |
| `CHAOS_API_KEY` | (empty) | If set, require `X-Api-Key` header |
| `CHAOS_CONFIRM` | — | Required for `prod` profile |

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Health check (no auth) |
| GET | `/api/experiments` | List experiments |
| POST | `/api/experiments/run` | Start experiment |
| POST | `/api/experiments/{name}/stop` | Stop experiment |
| POST | `/api/abort` | Abort all engines in namespace |
| GET | `/api/config` | Namespaces and env |
| WS | `/ws` | WebSocket echo / events |
