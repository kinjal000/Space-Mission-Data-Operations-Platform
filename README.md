# 🚀 Project Polaris — Space Mission Data Operations Platform

## 1. Project Overview

Project Polaris is an educational, full-stack Space Mission Management Portal and DevOps case study. It provides a lightweight Flask-based web console to register satellites, schedule missions, and record telemetry. The project is complemented by a monitoring and logging toolchain (Prometheus, Grafana, ELK) and DevOps automation examples (Docker, Jenkins, Terraform, Kubernetes, Vault).

---

## 2. Problem Statement

Teaching and demonstrating how a modern microservice-style application is deployed, monitored, logged, and secured in development and small-scale production environments is non-trivial.

Polaris provides a compact reference stack that demonstrates:

* Application metrics and monitoring
* Centralized logging and observability
* Secret management with Vault
* Containerization using Docker
* Infrastructure provisioning with Terraform
* Kubernetes deployment concepts

---

## 3. Objectives

* Provide a web UI to manage satellites, missions, and telemetry.
* Demonstrate Prometheus and Grafana monitoring.
* Demonstrate ELK Stack centralized logging.
* Demonstrate Vault-based secret management.
* Provide a containerized deployment environment.
* Showcase Infrastructure as Code and Kubernetes deployment.

---

## 4. Features

### Application Features

* User Authentication
* Satellite Management (CRUD)
* Mission Management (CRUD)
* Telemetry Logging
* Analytics Dashboard
* Chart.js Visualizations

### DevOps Features

* Docker Containerization
* Jenkins CI/CD Pipeline
* Terraform Infrastructure Provisioning
* Kubernetes Deployment
* Prometheus Monitoring
* Grafana Dashboards
* ELK Logging Stack
* HashiCorp Vault Integration

---

## 5. Technology Stack

| Category          | Technology                      |
| ----------------- | ------------------------------- |
| Backend           | Python 3.11, Flask              |
| Database          | SQLite                          |
| Monitoring        | Prometheus, Grafana             |
| Logging           | Elasticsearch, Logstash, Kibana |
| Secret Management | Vault                           |
| CI/CD             | Jenkins                         |
| Containerization  | Docker, Docker Compose          |
| Orchestration     | Kubernetes                      |
| IaC               | Terraform                       |
| Frontend          | HTML, CSS, JavaScript, Chart.js |

---

## 6. Architecture

### Application Flow

```text
User
 ↓
Flask Application
 ↓
SQLite Database
```

### Monitoring Flow

```text
Flask Metrics
 ↓
Prometheus
 ↓
Grafana
```

### Logging Flow

```text
Application Logs
 ↓
Logstash
 ↓
Elasticsearch
 ↓
Kibana
```

### Secret Management

```text
Vault
 ↓
Flask Application
```

---

## 7. Project Structure

```text
Space-Mission/
│
├── app.py
├── Dockerfile
├── docker-compose.yml
├── Jenkinsfile
├── requirements.txt
│
├── database/
│   ├── schema.sql
│   ├── sample_data.sql
│   └── polaris.db
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── satellites.html
│   ├── missions.html
│   ├── telemetry.html
│   └── analytics.html
│
├── static/
│
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
│
├── logging/
│   ├── logstash.conf
│   └── init-kibana.sh
│
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── kubernetes/
│   ├── deployment.yaml
│   └── service.yaml
│
├── vault/
│
└── README.md
```

---

## 8. DevOps Components

### Docker

Build the Flask application container.

```bash
docker build -t project-polaris .
```

---

### Jenkins

Pipeline stages:

```text
Build
 ↓
Test
 ↓
Docker Build
 ↓
Deploy
```

---

### Terraform

Infrastructure provisioning:

* VPC
* Security Groups
* EC2 Instance

---

### Kubernetes

Resources:

* Deployment
* Service

```yaml
replicas: 2
```

---

### Prometheus

Scrapes:

* Flask Application Metrics
* Node Exporter Metrics

---

### Grafana

Dashboard includes:

* Application Status
* CPU Usage
* Memory Usage
* Request Rate

---

### ELK Stack

Components:

* Elasticsearch
* Logstash
* Kibana

Log Flow:

```text
Flask App
 ↓
Logstash
 ↓
Elasticsearch
 ↓
Kibana
```

---

### Vault

Stores:

* secret_key
* db_path

---

## 9. Installation

### Clone Repository

```bash
git clone <repo-url>
cd Space-Mission
```

### Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 10. Run with Docker Compose

### Start Services

```bash
docker compose up --build -d
```

### Stop Services

```bash
docker compose down
```

---

## 11. Access URLs

| Service       | URL                   |
| ------------- | --------------------- |
| Flask App     | http://localhost:5006 |
| Prometheus    | http://localhost:9090 |
| Grafana       | http://localhost:3000 |
| Kibana        | http://localhost:5601 |
| Elasticsearch | http://localhost:9200 |
| Vault         | http://localhost:8200 |
| Jenkins       | http://localhost:8080 |

---

## 12. Monitoring

### Prometheus Targets

```bash
http://localhost:9090/targets
```

### Grafana Dashboard

Open:

```bash
http://localhost:3000
```

Dashboard:

* Flask Status
* CPU Usage
* Memory Usage
* Request Rate

---

## 13. Logging

### Verify Elasticsearch Indices

```bash
curl http://localhost:9200/_cat/indices?v
```

### View Logs

Open Kibana:

```bash
http://localhost:5601
```

Select:

```text
Polaris Logs
```

---

## 14. Secret Management

Vault stores:

* secret_key
* db_path

Access:

```bash
http://localhost:8200
```

---

## 15. Disaster Recovery

### Database Backup

```bash
cp database/polaris.db backups/polaris.db.backup
```

### Recovery Strategy

* Restore Database Backup
* Redeploy Containers
* Restart Services
* Kubernetes Self-Healing

### High Availability

```yaml
replicas: 2
```

If one pod fails:

```text
Pod 1 Down
 ↓
Pod 2 Running
 ↓
Application Available
```

---

## 16. Screenshots

### Login Page

![Login](docs/screenshots/login.png)

### Dashboard

![Dashboard](docs/screenshots/dashboard.png)

### Satellites

![Satellites](docs/screenshots/satellites.png)

### Missions

![Missions](docs/screenshots/missions.png)

### Telemetry

![Telemetry](docs/screenshots/telemetry.png)

### Grafana Dashboard

![Grafana](docs/screenshots/grafana-dashboard.png)

---

## 17. Future Enhancements

* PostgreSQL/MySQL Integration
* Production Vault Deployment
* JWT Authentication
* Alert Manager Integration
* Slack Notifications
* Kubernetes Health Checks
* Helm Charts
* Terraform Remote State

---

## 18. Author

**Project Polaris – Space Mission Data Operations Platform**

Developed as part of **DevOps Case Study 50**

**Author:** Kinjal Gawali

---

## Quick Start

```bash
docker compose up --build -d
```

### Open

* Flask: http://localhost:5006
* Prometheus: http://localhost:9090
* Grafana: http://localhost:3000
* Kibana: http://localhost:5601
* Vault: http://localhost:8200
* Jenkins: http://localhost:8080

```
```
