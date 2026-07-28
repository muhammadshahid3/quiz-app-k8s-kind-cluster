# Kubernetes Quiz App Deployment on KIND

A simple **Flask + MySQL Quiz Application** deployed on a local **Kubernetes (KIND)** cluster. This project demonstrates how to deploy a multi-container application using Kubernetes resources such as **Namespace, Persistent Volume (PV), Persistent Volume Claim (PVC), ConfigMap, Secret, Deployments, Services, and Horizontal Pod Autoscaler (HPA).**

---

# Project Architecture

<p align="center">
  <img src="screenshot/arch.png" width="900">
</p>

---

# Features

- Flask Quiz Application
- MySQL Database
- Kubernetes Deployment using KIND
- Persistent Volume (PV)
- Persistent Volume Claim (PVC)
- ConfigMap
- Secret
- ClusterIP Services
- Horizontal Pod Autoscaler (HPA)
- Metrics Server
- Dockerized Application

---

# Project Structure

```text
quiz-app/
│
├── kubernetes/
│   ├── namespace.yaml
│   ├── mysql-pv.yaml
│   ├── mysql-pvc.yaml
│   ├── mysql-deployment.yaml
│   ├── mysql-service.yaml
│   ├── flask-deployment.yaml
│   ├── flask-service.yaml
│   ├── flask-hpa.yaml
│   ├── quiz-configmap.yaml
│   ├── quiz-secret.yaml
│   ├── kind-config.yml
│   └── install.sh
│
├── screenshot/
│   ├── arch.png
│   ├── hpabefor.png
│   └── afterhpa.png
│
├── Dockerfile
├── app.py
├── requirements.txt
└── README.md
```

---

# Prerequisites

- Docker
- kubectl
- KIND
- Git
- Docker Hub Account

---

# Step 1 - Create KIND Cluster

```bash
kind create cluster --config kubernetes/kind-config.yml
```

Verify the cluster.

```bash
kubectl cluster-info
```

---

# Step 2 - Create Namespace

```bash
kubectl apply -f kubernetes/namespace.yaml
```

Verify namespace.

```bash
kubectl get namespace
```

---

# Step 3 - Create Persistent Volume (PV)

Create a Persistent Volume for storing MySQL data.

```bash
kubectl apply -f kubernetes/mysql-pv.yaml
```

Verify PV.

```bash
kubectl get pv
```

---

# Step 4 - Create Persistent Volume Claim (PVC)

Create a Persistent Volume Claim to request storage from the PV.

```bash
kubectl apply -f kubernetes/mysql-pvc.yaml
```

Verify PVC.

```bash
kubectl get pvc -n quiz-app
```

---

# Step 5 - Create ConfigMap

Store Flask application configuration.

```bash
kubectl apply -f kubernetes/quiz-configmap.yaml
```

Verify ConfigMap.

```bash
kubectl get configmap -n quiz-app
```

---

# Step 6 - Create Secret

Store MySQL credentials securely.

```bash
kubectl apply -f kubernetes/quiz-secret.yaml
```

Verify Secret.

```bash
kubectl get secret -n quiz-app
```

---

# Step 7 - Deploy MySQL Database

Deploy the MySQL database with Persistent Storage.

```bash
kubectl apply -f kubernetes/mysql-deployment.yaml
```

Verify Deployment.

```bash
kubectl get deployment -n quiz-app
```

Verify Pod.

```bash
kubectl get pods -n quiz-app
```

---

# Step 8 - Create MySQL Service

Expose MySQL inside the cluster.

```bash
kubectl apply -f kubernetes/mysql-service.yaml
```

Verify Service.

```bash
kubectl get svc -n quiz-app
```

---

# Step 9 - Deploy Flask Application

Deploy the Flask Quiz Application.

```bash
kubectl apply -f kubernetes/flask-deployment.yaml
```

Verify Deployment.

```bash
kubectl get deployment -n quiz-app
```

Verify Pods.

```bash
kubectl get pods -n quiz-app
```

---

# Application Running (Before HPA)

Before enabling the Horizontal Pod Autoscaler, the Flask application was running with the fixed number of replicas defined in the Deployment. At this stage, Kubernetes does not automatically increase or decrease the number of Pods when the application receives high traffic.

<p align="center">
  <img src="screenshot/hpabefor.png" width="900">
</p>

---

# Step 10 - Install Metrics Server (Required for HPA)

Horizontal Pod Autoscaler requires the Kubernetes Metrics Server to collect CPU metrics.

### Install Metrics Server

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

---

### Edit Metrics Server Deployment

```bash
kubectl -n kube-system edit deployment metrics-server
```

Add the following arguments under **containers.args**.

```yaml
- --kubelet-insecure-tls
- --kubelet-preferred-address-types=InternalIP,Hostname,ExternalIP
```

Save and exit.

---

### Restart Metrics Server

```bash
kubectl rollout restart deployment metrics-server -n kube-system
```

---

### Verify Metrics Server

```bash
kubectl get pods -n kube-system
```

```bash
kubectl top nodes
```

```bash
kubectl top pods -n quiz-app
```

---

# Step 11 - Enable Horizontal Pod Autoscaler (HPA)

Deploy the Horizontal Pod Autoscaler.

```bash
kubectl apply -f kubernetes/flask-hpa.yaml
```

Verify HPA.

```bash
kubectl get hpa -n quiz-app
```

Watch HPA in real time.

```bash
kubectl get hpa -n quiz-app -w
```

---

# Step 12 - Create Flask Service

Expose the Flask application inside the Kubernetes cluster.

```bash
kubectl apply -f kubernetes/flask-service.yaml
```

Verify Service.

```bash
kubectl get svc -n quiz-app
```

---

# Application Running (After HPA)

After enabling the Horizontal Pod Autoscaler, CPU load was generated on the Flask application. Once the CPU utilization exceeded the configured threshold, Kubernetes automatically created additional Pods to distribute the traffic. This demonstrates automatic scaling based on application load, ensuring better performance and high availability.

<p align="center">
  <img src="screenshot/afterhpa.png" width="900">
</p>

The screenshot above shows that the number of running Pods increased automatically after applying load, confirming that the Horizontal Pod Autoscaler is working successfully.

---

# Verify Kubernetes Resources

Get all resources.

```bash
kubectl get all -n quiz-app
```

Persistent Volumes.

```bash
kubectl get pv
```

Persistent Volume Claims.

```bash
kubectl get pvc -n quiz-app
```

ConfigMaps.

```bash
kubectl get configmap -n quiz-app
```

Secrets.

```bash
kubectl get secret -n quiz-app
```

Deployments.

```bash
kubectl get deployment -n quiz-app
```

Pods.

```bash
kubectl get pods -n quiz-app
```

Services.

```bash
kubectl get svc -n quiz-app
```

Horizontal Pod Autoscaler.

```bash
kubectl get hpa -n quiz-app
```

---

# Technologies Used

- Python Flask
- MySQL
- Docker
- Kubernetes
- KIND
- kubectl
- ConfigMap
- Secret
- Persistent Volume (PV)
- Persistent Volume Claim (PVC)
- Deployment
- Service
- Metrics Server
- Horizontal Pod Autoscaler (HPA)

---

# Author

## Muhammad Shahid

**DevOps & Cloud Enthusiast**

If you found this project helpful, don't forget to ⭐ this repository.
