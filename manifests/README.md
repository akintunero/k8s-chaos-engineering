# Legacy manifests

**Use the golden path:** [`examples/quickstart/`](../examples/quickstart/)

Files in this directory remain for backward compatibility. New installs should run:

```bash
kubectl apply -k examples/quickstart
```

`flask-app.yaml` mirrors the quickstart application and will be removed in a future release.
