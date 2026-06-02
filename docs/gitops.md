# GitOps guide

Deploy and manage chaos resources declaratively with **Argo CD** or **Flux**.

## Overview

```text
Git repo (this project)
    ├── examples/quickstart/   → sample app + RBAC
    └── experiments/           → Litmus ChaosEngine manifests
              ↓
    Argo CD / Flux sync
              ↓
    Cluster (Litmus already installed)
```

Litmus itself is installed via Helm (`make install-litmus`), not by these examples.

## Argo CD

1. Install [Argo CD](https://argo-cd.readthedocs.io/).
2. Install Litmus: `make install-litmus`
3. Apply project and applications:

```bash
kubectl apply -f examples/gitops/argocd/project.yaml
kubectl apply -f examples/gitops/argocd/application-quickstart.yaml
```

4. Wait for sync:

```bash
argocd app wait chaos-quickstart
kubectl get pods -n hello-world-app
```

5. When ready for chaos, apply experiments (manual sync recommended first):

```bash
kubectl apply -f examples/gitops/argocd/application-experiments.yaml
argocd app sync chaos-experiments
```

Manifests use `https://github.com/akintunero/k8s-chaos-engineering.git` by default. Change `spec.source.repoURL` only when deploying from a fork.

## Flux

1. Install [Flux](https://fluxcd.io/flux/installation/).
2. Install Litmus on the cluster.
3. Apply GitOps manifests:

```bash
kubectl apply -f examples/gitops/flux/gitrepository.yaml
kubectl apply -f examples/gitops/flux/kustomization-quickstart.yaml
```

4. Confirm reconciliation:

```bash
flux get kustomizations
```

5. Enable experiments when ready:

```bash
# Edit kustomization-experiments.yaml: spec.suspend: false
kubectl apply -f examples/gitops/flux/kustomization-experiments.yaml
```

## CI integration

After GitOps deploys the quickstart app, run chaos in CI:

```yaml
- uses: akintunero/k8s-chaos-engineering/.github/actions/chaos-test@v1
  with:
    experiment: pod-delete
```

Pin to a release tag when available. For KinD-based full e2e, see `.github/workflows/e2e-kind.yml`.

## Validation in PRs

Manifest changes are checked by:

- `.github/workflows/manifests.yml` — Helm lint, kustomize, kubeconform
- `hack/validate-manifests.sh` — local equivalent
