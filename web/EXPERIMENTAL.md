# Web UI (beta)

React dashboard + FastAPI API for managing chaos experiments. Usable via **Docker Compose**; not required for `make quickstart`.

## Run with Docker

```bash
# From repo root — mounts ~/.kube so the API can reach the Kubernetes cluster
make web-up
```

- UI: http://localhost:3000  
- API: http://localhost:8000  
- Health: http://localhost:8000/healthz  

```bash
make web-down
```

## Run locally (development)

```bash
make install
pip install -r web/backend/requirements.txt

cd web/backend && uvicorn main:app --reload --port 8000

cd web/frontend && npm install && npm run dev
```

Frontend dev server proxies `/api` to port 8000 (see `vite.config.ts`).

## Authentication

Optional API key:

```bash
export CHAOS_API_KEY="$(openssl rand -hex 32)"
# Requests must include header: X-Api-Key: <same value as CHAOS_API_KEY>
```

If unset, the API does not require a key (local development only).

## Limitations

- Requires `kubectl` access to the cluster from the backend process
- No built-in OIDC/RBAC yet — use API key + network policy in production
- Scheduling and notifications inherit CLI behavior

See [docs/safety.md](../docs/safety.md) for blast-radius profiles when running experiments from the UI.
