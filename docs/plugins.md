# Experiment plugins

Register custom experiment manifest generators without forking core runners.

## Configure

`config/plugins.yaml`:

```yaml
plugins:
  - name: log-stress-demo
    module: plugins.log_stress_demo
    function: generate_manifest
    enabled: true
```

## Implement

```python
# plugins/my_plugin.py
def generate_manifest(params: dict) -> str:
    return "apiVersion: litmuschaos.io/v1alpha1\nkind: ChaosEngine\n..."
```

## Use from Python

```python
from utils.plugins import generate_plugin_manifest

yaml_text = generate_plugin_manifest("log-stress-demo", {"namespace": "hello-world-app"})
```

Example stub: [`plugins/log_stress_demo.py`](../plugins/log_stress_demo.py)

Future: `k8s-chaos plugin run <name>` CLI subcommand.
