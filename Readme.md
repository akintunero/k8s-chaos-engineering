
# **Kubernetes Chaos Engineering Framework**  

![Chaos Engineering](https://img.shields.io/badge/Chaos%20Engineering-Kubernetes-blue?style=for-the-badge)  
![LitmusChaos](https://img.shields.io/badge/LitmusChaos-Experimenting-orange?style=for-the-badge)  
![License](https://img.shields.io/github/license/your-username/kubernetes-chaos-framework?style=for-the-badge)  
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen?style=for-the-badge)  

##  Overview  
The **Kubernetes Chaos Engineering Framework** helps teams **test, analyze, and improve resilience** of Kubernetes applications by injecting controlled failures using **LitmusChaos**.  

With this framework, you can simulate failures like **pod crashes, network delays, CPU stress, and more**, ensuring that your cloud-native applications are **fault-tolerant and highly available**.  

---

## **🎯 Features**  
✅ **Automated Chaos Experiments** (Pod Delete, CPU Stress, Network Latency, Disk Stress)  
✅ **Customizable Chaos Workflows** with LitmusChaos CRDs  
✅ **Easy Deployment** with Helm Charts  
✅ **Monitoring & Observability** via Prometheus & Grafana  
✅ **Prometheus Alerts** for Chaos Failures  
✅ **Extensible Architecture** for adding new experiments  

---

## **📥 Clone This Project**  
To set up the project locally, run:  
```sh
git clone https://github.com/akintunero/kubernetes-chaos-framework.git
cd kubernetes-chaos-framework
```

---

## **🛠️ Prerequisites**  
Ensure the following are installed on your system:  
- ✅ Kubernetes Cluster (Minikube, Kind, or cloud-based cluster)  
- ✅ kubectl (Kubernetes CLI)  
- ✅ Helm (v3+)  
- ✅ LitmusChaos (Installed in the cluster)  

---

## **🚀 Getting Started**  

### **1️⃣ Install LitmusChaos**  
If LitmusChaos is not installed, deploy it using Helm:  
```sh
helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/
helm repo update
helm install litmus litmuschaos/litmus --namespace litmus --create-namespace
```

Verify installation:  
```sh
kubectl get pods -n litmus
```

---

### **2️⃣ Deploy a Sample Application**  
To test chaos, deploy a simple **Flask App**:  
```sh
kubectl apply -f manifests/flask-app.yaml
```

Check if the app is running:  
```sh
kubectl get pods -n hello-world-app
```

---

### **3️⃣ Running a Chaos Experiment (Pod Delete)**  
Apply the `pod-delete.yaml` chaos experiment:  
```sh
kubectl apply -f experiments/pod-delete.yaml
```

Check the **ChaosEngine status**:  
```sh
kubectl get chaosengine pod-delete -n hello-world-app -o jsonpath='{.status.engineStatus}'
```

Check the logs for any running chaos pods:  
```sh
kubectl get pods -n hello-world-app
```

---

### **4️⃣ Stopping a Chaos Experiment**  
To stop a running chaos experiment:  
```sh
kubectl patch chaosengine pod-delete -n hello-world-app --type='merge' -p '{"spec":{"engineState":"stop"}}'
```

To completely delete it:  
```sh
kubectl delete chaosengine pod-delete -n hello-world-app
```

---

## **📊 Monitoring Chaos Experiments**  
To monitor and visualize chaos tests:  

1️⃣ **Install Prometheus & Grafana** using Helm:  
```sh
helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
```

2️⃣ **Access Grafana Dashboard**  
```sh
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
```

3️⃣ Open `http://localhost:3000`, login with `admin/admin`, and import LitmusChaos dashboards.

---

## **📜 Customizing Chaos Experiments**  
Modify the `experiments/` YAML files to create custom scenarios.  

Example: **CPU Stress Test**
```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: cpu-stress
  namespace: hello-world-app
spec:
  appinfo:
    appns: hello-world-app
    applabel: "app=flask-app"
    appkind: deployment
  annotationCheck: "false"
  engineState: "active"
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-cpu-hog
      spec:
        components:
          env:
            - name: CPU_CORES
              value: "2"
            - name: TOTAL_CHAOS_DURATION
              value: "60"
```
Apply it:  
```sh
kubectl apply -f experiments/cpu-stress.yaml
```

---

## **📜 Project Structure**  
```
kubernetes-chaos-framework/
│── manifests/            # Sample Kubernetes application manifests
│── experiments/          # YAML files defining chaos experiments
│── helm/                 # Helm charts for easy deployment
│── monitoring/           # Grafana dashboards & Prometheus alerts
│── scripts/              # Python automation scripts
│── docs/                 # Project documentation
│── README.md             # Project documentation
│── LICENSE               # License file
```

---

## **📜 Future Enhancements**  
🔹 Add **network latency & disk stress** chaos tests  
🔹 Integrate with **Slack alerts** for failure notifications  
🔹 Provide **Web UI Dashboard** for chaos testing  

---

## **📄 License**  
This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for more details.

---

## **🙌 Contributing**  
We welcome contributions! Follow these steps:  

1️⃣ **Fork the repository**  
2️⃣ **Create a new branch**: `feature-branch`  
3️⃣ **Commit changes** & push to your branch  
4️⃣ **Open a Pull Request** 🚀  

---


---