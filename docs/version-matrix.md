# Version matrix

Supported combinations for the **quickstart golden path** (`make quickstart`). Other versions may work but are not regularly tested.

| Component        | Tested / recommended | Notes                                      |
|------------------|----------------------|--------------------------------------------|
| Kubernetes       | 1.27 – 1.30          | kind, minikube, Docker Desktop, DOKS, EKS  |
| kubectl          | 1.27+                | Must match cluster within skew policy      |
| Helm             | 3.12+                | Used for Litmus install                    |
| Litmus (Helm)    | 3.29.x `litmus-core` | ChaosEngine path; use `LITMUS_MODE=center` for ChaosCenter UI |
| Python           | 3.9 – 3.11           | Automation scripts and reports             |

## Local clusters

| Provider            | Quickstart support |
|---------------------|--------------------|
| kind                | Recommended        |
| minikube            | Supported          |
| Docker Desktop K8s  | Supported          |
| Cloud (DOKS/EKS/GKE)| Supported          |

## Reporting issues

Include `kubectl version`, `helm version`, cluster provider, and Litmus pod status from namespace `litmus` when filing bugs.
