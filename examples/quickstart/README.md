# Quickstart workload

Canonical sample application for chaos experiments in this repository.

## Deploy

```bash
kubectl apply -k examples/quickstart
kubectl wait --for=condition=available deployment/flask-app -n hello-world-app --timeout=120s
```

## Verify

```bash
kubectl get pods -n hello-world-app -l app=flask-app
```

## Full guided path

From the repository root:

```bash
make quickstart
# or
./hack/quickstart.sh
```

See the root [README](../../Readme.md) for prerequisites and version support.
