# Project Polaris – Space Mission Data Operations Platform

Project Polaris is a lightweight, educational Space Mission Management Portal and DevOps case study. The application simulates space research operations monitoring satellites, space missions, and telemetry data, while keeping a clean, modular structure that's easy to digest and explain.

---

## Technology Stack

- **Backend**: Python 3 (Flask Framework)
- **Database**: SQLite3
- **Frontend**: Responsive HTML5, Vanilla CSS3 (Custom Glassmorphism styling with CSS variables), and JavaScript
- **Visualizations**: Chart.js (Loaded via CDN)
- **DevOps Integrations**: Docker, Jenkinsfile, Terraform, Kubernetes

---

## Key Features

1. **Operations Dashboard**: View critical KPIs (Total Satellites, Active Missions, Telemetry logs count, Mission Success Rate), recent operations activity feeds, and mission stage status cards.
2. **Theme Controls (Light/Dark Mode)**: Persistence theme toggle in the navigation bar using browser local storage state. Uses space-accented HSL/HEX colors.
3. **Satellite Management**: Full CRUD operations (Add, View, Edit, Delete) for satellite assets.
4. **Space Mission Coordination**: CRUD operations for scheduling space voyages, target bodies, and tracking statuses (Planning, Active, Completed, Failed).
5. **Telemetry Logs**: Record diagnostic telemetry records (temperature, battery levels, signal strength) linked directly to registered satellites.
6. **Analytics Portal**: Lightweight visual charts analyzing satellite active distribution and mission lifecycle counts.

---

## Credentials (Hardcoded Admin)

For academic evaluation simplicity, use the following credentials to access the console:
- **Username**: `admin`
- **Password**: `admin123`

---

## Installation & Local Execution

### Prerequisites
- Python 3.8+ installed on your machine.

### Setup Instructions
1. Navigate to the project root directory:
   ```bash
   cd Space-Mission
   ```

2. (Optional but recommended) Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required library dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask application:
   ```bash
   python3 app.py
   ```

5. Open your web browser and navigate to:
   ```text
   http://127.0.0.1:5006/
   ```
   *Note: On initial startup, the application automatically creates and populates the SQLite database (`database/polaris.db`) with schemas and mock data.*

---

## Docker Steps

A ready-to-use `Dockerfile` is included to bundle and run the platform in a isolated container environment.

1. **Build the image**:
   ```bash
   docker build -t project-polaris:latest .
   ```

2. **Launch the container**:
   ```bash
   docker run -d -p 5006:5006 --name polaris-app project-polaris:latest
   ```

3. Open your browser at `http://localhost:5006` to access the application.

---

## Jenkins Pipeline Overview

The declarative `Jenkinsfile` at the root of the project defines a build pipeline:
- **Build**: Compiles the application files and builds the Docker image.
- **Test**: Conducts static syntax compilation verification using the `py_compile` module.
- **Deploy**: A placeholder stage that logs successful staging or cluster shipping events.

---

## Terraform (AWS Infrastructure)

The configurations inside the `terraform/` directory lay out standard infrastructure provisioning on AWS:
- **VPC** & **Subnet**: Configures custom network bounds (`10.0.0.0/16` and a public subnet `10.0.1.0/24`).
- **Internet Gateway** & **Route Table**: Routes public web traffic safely.
- **Security Groups**: Restricts ingress rules to SSH (22), HTTP (80), and Flask Custom (5006) traffic.
- **EC2 Instance**: Deploys a virtual `t2.micro` Linux server pre-configured with Docker services.

### Running Terraform:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

---

## Kubernetes Deployment

The resources in the `kubernetes/` folder show container scheduling onto cluster namespaces:
- **deployment.yaml**: Schedules the app on `replicas: 2` to ensure high availability. Limits compute capacity to 500m CPU / 512Mi RAM.
- **service.yaml**: Provisions a `NodePort` mapping node traffic from port `30080` to containers running on port `5006`.

### Deploying on Kubernetes:
```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```
Verify the pods are running:
```bash
kubectl get pods
```
