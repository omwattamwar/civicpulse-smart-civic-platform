# 🏛️ CivicPulse: AI-Powered Civic Complaint Management System

> **"Empowering Smart Cities Through AI-Driven Civic Intelligence."**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-19.2-blue.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-7.3-purple.svg)](https://vitejs.dev/)
[![Firebase](https://img.shields.io/badge/Firebase-12.10-orange.svg)](https://firebase.google.com/)
[![Python](https://img.shields.io/badge/Python-FastAPI-green.svg)](https://fastapi.tiangolo.com/)

<div align="center">
  <img src="assets/banner.png" alt="CivicPulse Banner" width="100%" />
</div>

<br/>

CivicPulse is an AI-powered Civic Complaint Management System that enables citizens to report civic issues, intelligently classifies complaints using Artificial Intelligence, prioritizes requests based on severity, routes them to the appropriate government department, and provides real-time complaint tracking with analytics dashboards for smarter urban governance.

---

## 📑 Table of Contents
<details>
<summary>Click to expand</summary>

1. [Project Overview](#-project-overview)
2. [Problem & Solution](#-problem--solution)
3. [Key Features](#-key-features)
4. [Technology Stack](#-technology-stack)
5. [System Architecture](#-system-architecture)
6. [Workflows & Diagrams](#-workflows--diagrams)
7. [Project Structure](#-project-structure)
8. [Installation & Setup](#-installation--setup)
9. [Screenshots](#-screenshots)
10. [Challenges & Learnings](#-challenges--learnings)
11. [Contributing](#-contributing)
12. [License](#-license)

</details>

---

## 🎯 Project Overview

CivicPulse acts as a digital bridge between citizens and municipal authorities. By leveraging **Natural Language Processing (Google Gemini)** and **Computer Vision (YOLOv8)**, it eliminates the manual triage of civic complaints (e.g., potholes, waste accumulation, water leakage), ensuring resources are deployed rapidly and efficiently.

### 🛑 Problem Statement
Municipal authorities struggle with a high volume of unstructured, miscategorized, and unverified civic complaints. This leads to slow response times, duplicate reports, and inefficient resource allocation.

### ✅ Solution
CivicPulse introduces an **automated AI triage system**. It uses Gemini for semantic text analysis and YOLOv8s for zero-shot image verification to accurately classify complaints, detect duplicates, and assign severity scores before they ever reach a human operator.

---

## ✨ Key Features

| Category | Features |
| :--- | :--- |
| **🔐 Authentication** | Role-Based Access Control (RBAC) for Citizens and Authorities. |
| **📝 Issue Reporting** | Complaint registration with Image Upload and Geo Location (Geoapify). |
| **🧠 AI Intelligence** | NLP Classification, Priority Detection, and Visual verification via YOLOv8. |
| **🏢 Management** | Automated Department Assignment and comprehensive Authority Dashboards. |
| **📊 Analytics** | Citizen Dashboards, Real-Time Tracking, and Power BI-style visualizations. |
| **🌐 UX/UI** | Dark Mode, Responsive Design, Multi-language support, and Real-Time Updates. |

---

## 🛠️ Technology Stack

<details>
<summary><strong>View Detailed Stack</strong></summary>

- **Frontend:** React 19, Vite, Tailwind CSS 4, React Router DOM, Recharts, Leaflet, i18next.
- **Backend/Database:** Firebase Authentication, Cloud Firestore, Cloudinary.
- **AI/ML:** Google Gemini 2.5 API (NLP), YOLOv8 (Computer Vision).
- **APIs:** Geoapify API, OpenStreetMap, IPAPI, Web Speech API.
- **Tools:** GitHub, npm, Vite, VS Code.

</details>

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[Citizen App] -->|Auth| B(Firebase Auth)
    A -->|Data| C[(Cloud Firestore)]
    A -->|Images| D[Cloudinary]
    
    C <--> E[Python FastAPI Microservice]
    E -->|Text Analysis| F[Google Gemini API]
    E -->|Vision Detection| G[YOLOv8 Model]
    
    H[Authority Dashboard] -->|Reads| C
```

---

## 🔄 Workflows & Diagrams

<details>
<summary><strong>1. Application Workflow</strong></summary>

```mermaid
flowchart LR
    Start([User Visits App]) --> Auth{Is Logged In?}
    Auth -- No --> Login[Login/Register]
    Auth -- Yes --> Role{Role?}
    Role -- Citizen --> CD[Citizen Dashboard]
    Role -- Authority --> AD[Authority Dashboard]
```
</details>

<details>
<summary><strong>2. Citizen Complaint Workflow</strong></summary>

```mermaid
sequenceDiagram
    participant Citizen
    participant App
    participant AI
    participant DB
    
    Citizen->>App: Submits Form (Text + Image + Location)
    App->>AI: Sends data for Triage
    AI-->>App: Returns Category & Priority
    App->>DB: Saves structured complaint
    DB-->>App: Confirmation
    App-->>Citizen: Complaint ID Generated
```
</details>

<details>
<summary><strong>3. Authority Workflow</strong></summary>

```mermaid
flowchart TD
    A[Authority Login] --> B[View Dashboard Analytics]
    B --> C[Filter Complaints by Department]
    C --> D[Select High-Priority Issue]
    D --> E[Update Status: In Progress]
    E --> F[Update Status: Resolved]
```
</details>

<details>
<summary><strong>4. Complaint Processing Flow</strong></summary>

```mermaid
stateDiagram-v2
    [*] --> Submitted
    Submitted --> AI_Triage
    AI_Triage --> Pending_Review
    Pending_Review --> In_Progress
    In_Progress --> Resolved
    In_Progress --> Rejected
    Resolved --> [*]
    Rejected --> [*]
```
</details>

<details>
<summary><strong>5. AI Classification Workflow</strong></summary>

```mermaid
flowchart TD
    Input[Raw Complaint Data] --> Split{Data Type}
    Split -->|Text| NLP[Gemini: Categorize & Summarize]
    Split -->|Image| CV[YOLOv8: Detect Objects]
    NLP --> Merge[Aggregate Confidence]
    CV --> Merge
    Merge --> Output[Final Severity Score]
```
</details>

<details>
<summary><strong>6. Authentication Flow</strong></summary>

```mermaid
sequenceDiagram
    participant User
    participant Firebase
    participant Firestore
    
    User->>Firebase: Email & Password
    Firebase-->>User: JWT Token
    User->>Firestore: Request User Profile (Role)
    Firestore-->>User: Role Data (Citizen/Authority)
```
</details>

<details>
<summary><strong>7. Database Relationship Diagram</strong></summary>

```mermaid
erDiagram
    USERS ||--o{ COMPLAINTS : submits
    USERS {
        string uid PK
        string role
        string email
    }
    COMPLAINTS ||--o{ NOTIFICATIONS : triggers
    COMPLAINTS {
        string id PK
        string title
        string status
        string ai_priority
    }
```
</details>

<details>
<summary><strong>8. Deployment Workflow</strong></summary>

```mermaid
flowchart LR
    Dev[Developer Commits Code] --> GitHub[GitHub Repository]
    GitHub -->|CI/CD Actions| Build[Vite Build]
    Build --> Deploy[Firebase Hosting / Vercel]
```
</details>

---

## 📂 Project Structure

```mermaid
graph TD
    Root[civicpulse-smart-civic-platform/]
    Root --> Src[src/]
    Root --> AI[ai-microservice/]
    Root --> Docs[docs/]
    Root --> Assets[assets/]
    
    Src --> Comps[components/]
    Src --> Pages[pages/]
    Src --> Context[context/]
    
    AI --> Main[main.py]
    AI --> Models[YOLO models]
```

---

## 🚀 Installation & Setup

> **Note:** Ensure you have Node.js 18+ and Python 3.10+ installed.

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/civicpulse-smart-civic-platform.git
cd civicpulse-smart-civic-platform
```

### 2. Frontend Setup
```bash
npm install
npm run dev
```

### 3. AI Microservice Setup
```bash
cd ai-microservice
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 4. Environment Variables
Create a `.env` file in the root directory. Refer to `docs/Environment_Variables.md` for the template configuration for Firebase, Gemini, and Geoapify.

---

## 📸 Screenshots

| Citizen Interface | Authority Interface | Issue Reporting |
| :---: | :---: | :---: |
| <img src="assets/citizen-dashboard.png" width="250"/> | <img src="assets/authority-dashboard.png" width="250"/> | <img src="assets/report-issue.png" width="250"/> |

---

## 💡 Challenges & Learnings

### Challenges Faced
- **AI Latency:** Balancing real-time UI updates with the processing time required by YOLOv8 and the Gemini API.
- **Geospatial Accuracy:** Handling edge cases where reverse geocoding APIs (Nominatim) returned inaccurate granular data.

### Learning Outcomes
- Mastered the integration of Python microservices with React frontends.
- Developed a deep understanding of Firebase security rules and role-based access architectures.

---

## 🤝 Contributing
Contributions are welcome! Please check out the [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) for more details.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

<div align="center">
  <i>Developed with ❤️ for smarter, cleaner cities.</i>
</div>
