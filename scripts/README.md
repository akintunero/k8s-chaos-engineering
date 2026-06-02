# Scripts directory

Legacy entrypoints and shims. **Preferred interface:** the `k8s-chaos` CLI from the installable package (`src/k8s_chaos/`).

## Install

From the repository root:

```bash
make install          # editable install + sync packaged YAML
k8s-chaos doctor
k8s-chaos list
```

See [CONTRIBUTING.md](../CONTRIBUTING.md) and [docs/pypi.md](../docs/pypi.md).

## Shims (backward compatible)

| File | Maps to |
|------|---------|
| `cli.py` | `k8s_chaos.cli` |
| `chaos-runner.py` | `k8s_chaos.chaos_runner` |
| `doctor.py` | `k8s_chaos.doctor` |
| `gameday.py` | `k8s_chaos.gameday` |
| `preflight.py` | `k8s_chaos.preflight` |
| `abort.py` | `k8s_chaos.abort` |
| `quickstart_report.py` | `k8s_chaos.quickstart_report` |
| `setup.py` | Interactive Litmus/app/monitoring setup (still uses `scripts/utils` imports via shims) |

Run the same commands via CLI:

```bash
k8s-chaos run pod-delete
k8s-chaos abort
k8s-chaos gameday quickstart
k8s-chaos report pod-delete
```

## Dependencies

Python dependencies are defined in [pyproject.toml](../pyproject.toml). Install with `make install` or `pip install -e ".[dev]"`.

`requirements.txt` and `requirements-dev.txt` remain for CI paths that have not migrated to `pyproject.toml` yet.

## Makefile shortcuts

```bash
make quickstart
make run-experiment EXPERIMENT=pod-delete
make gameday GAMEDAY=quickstart
make doctor
```

Full list: `make help`.

## Troubleshooting

```bash
k8s-chaos doctor
kubectl cluster-info
kubectl get pods -n hello-world-app
kubectl get pods -n litmus
```

If `pip install` resolves the package to `scripts/` instead of `src/`, remove stale metadata and reinstall:

```bash
./hack/ensure-dev-install.sh
pip install -e ".[dev]" --force-reinstall
```
