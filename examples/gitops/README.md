# GitOps examples

Deploy the **quickstart workload** and **chaos experiments** with Argo CD or Flux.

Prerequisites:

- Cluster with Argo CD or Flux installed
- [LitmusChaos](https://litmuschaos.io) installed (`make install-litmus`)
- This repository cloned or referenced by URL

## Layout

| Path | Tool | Purpose |
|------|------|---------|
| [argocd/](argocd/) | Argo CD | `Application` for quickstart + experiments |
| [flux/](flux/) | Flux | `GitRepository` + `Kustomization` |

## Argo CD

```bash
kubectl apply -f examples/gitops/argocd/project.yaml
kubectl apply -f examples/gitops/argocd/application-quickstart.yaml
# After sync: kubectl get pods -n hello-world-app
kubectl apply -f examples/gitops/argocd/application-experiments.yaml
```

Application manifests default to `https://github.com/akintunero/k8s-chaos-engineering.git`. Change `spec.source.repoURL` only if you deploy from a fork.

## Flux

```bash
kubectl apply -f examples/gitops/flux/gitrepository.yaml
kubectl apply -f examples/gitops/flux/kustomization-quickstart.yaml
kubectl apply -f examples/gitops/flux/kustomization-experiments.yaml
```

## CI smoke test

Use the composite action [`.github/actions/chaos-test`](../../.github/actions/chaos-test) after GitOps sync in CI.

See [docs/gitops.md](../../docs/gitops.md) for details.
