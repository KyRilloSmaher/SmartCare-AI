# SmartCare-AI

SmartCare-AI is an AI microservice designed to support an Online Pharmacy platform.
It provides **semantic search**, **drug similarity recommendations**, and
**contraindication detection**, while strictly respecting medical safety boundaries.

> ⚠️ SmartCare-AI is **advisory only**.  
> It does **not** prescribe medication or make autonomous medical decisions.

---

## 📌 Project Goals

SmartCare-AI exists to:

- Improve drug discovery using **semantic search**
- Recommend **similar or alternative drugs**
- Detect **potential contraindications** between medications
- Integrate safely with a **Flutter + .NET + MSSQL** pharmacy system
- Scale from local development to production

---

## 🏗️ High-Level Architecture

    Flutter App
    ↓
    .NET Backend (Auth, Orders, Drugs)
    ↓
    SmartCare-AI (FlaskAPI)
    ↓
    Vector DB (FAISS / Qdrant)


### Key Principles
- MSSQL is the **system of record**
- Vector databases store **derived data**
- Deterministic medical rules override AI
- AI assists — it never decides

---

## 🧠 AI Capabilities

### 1. Semantic Drug Search
Search drugs by **meaning**, not keywords.

Example:
> "medicine for headache without stomach pain"

---

### 2. Drug Similarity & Recommendation
Find drugs with similar:
- Active ingredients
- Drug class
- Indications

---

### 3. Contraindication Detection (Safety-Critical)
Detect risks between:
- Newly selected drug
- Previously purchased drugs

Uses:
- Deterministic medical rules (hard stop)
- AI-assisted semantic risk analysis (warnings)

---

## 🔁 AI Request Pipeline (Summary)

All AI requests follow the same pipeline:

API Layer
→ Service Layer
→ Pipeline Layer
→ Domain Rules
→ Vector Search / AI Models
→ Ranking
→ Auditing
→ Response



*Detailed pipelines are documented in*

    Docs/architecture.md



---

## 📂 Project Structure (Simplified)

    SmartCare-AI/
    ├── App/
    │ ├── api/ # FastAPI routes (versioned)
    │ ├── services/ # Use-case orchestration
    │ ├── services/pipelines/ # Core AI pipelines
    │ ├── domain/ # Medical domain & rules
    │ ├── repositories/ # MSSQL & Vector DB access
    │ ├── ML/ # Embeddings & inference
    │ ├── schemas/ # Pydantic models
    │ ├── observability/ # Auditing & tracing
    │ └── utils/ # Helpers & logging
    │
    ├── Jobs/ # Background & sync jobs
    ├── Docs/ # Architecture & API docs
    ├── EDA/ # Notebooks & experiments
    └── Infra/ # Deployment & infra configs


---

## 🧪 Development Environment Setup

### 1️⃣ Prerequisites

- Python **3.11+**
- pip / virtualenv
- MSSQL (local or remote)
- Git

Optional:
- Docker (recommended for Qdrant)

---

### 2️⃣ Clone the Repository

    git clone <repo-url>
    cd SmartCare-AI

3️⃣ Create Virtual Environment

    python -m venv venv
    source venv/bin/activate   # Windows: venv\Scripts\activate
4️⃣ Install Dependencies
```bash
Copy code
pip install -r requirements.txt
```
5️⃣ Environment Variables
```bash
Create a .env file using the example:
cp .env.example .env
```

Configure:

    Database connection

    Vector DB selection

    Feature flags

    API keys (if used)

6️⃣ Run the Service
```bash
Copy code
python run.py
```
Service will start at:

    http://localhost:8000
### Health check:

    GET /api/v1/health

# 🔌 Vector Database Strategy
### Environment	Vector DB
    Local / Dev	FAISS
    Production  Qdrant

Switching is controlled via configuration only.

Vector DBs:

    Are rebuildable

    Do not contain source data

    Sync from MSSQL

More details:

```bash
Docs/vector_strategy.md
```
### 🔐 Safety & Compliance
Contraindication Decision Priority
Priority	Source	Can Block
1	Deterministic Medical Rules	✅ Yes
2	Drug Class Overlap	⚠️ Warning
3	AI Semantic Risk	⚠️ Warning
4	AI Explanation	❌ No

### Guarantees
    AI does not prescribe

    AI does not override rules

    All warnings are explainable

    Pharmacist override is always possible

🧪 Testing
Run tests with:

## pytest
``` bash
Tests include:

Semantic search

Recommendations

Contraindications

Sync jobs
```

🔄 Background Jobs
Located in:

    Jobs/
Common jobs:

rebuild_embeddings.py

sync_drugs.py

cleanup_vectors.py

These jobs keep vector data synchronized with MSSQL.

📚 Documentation
File	Purpose
Docs/architecture.md	System & pipeline design
Docs/api_contracts.md	API request/response
Docs/vector_strategy.md	Vector DB & sync

🚧 Non-Goals (Important)
SmartCare-AI explicitly does NOT:

Diagnose diseases

Prescribe medication

Replace pharmacists or doctors

Act autonomously

🤝 Contribution Guidelines
Follow existing architecture

Never bypass domain rules

Keep AI explainable

Add tests for all pipelines

Update Docs when changing behavior

🧠 Final Note
SmartCare-AI is built with one core philosophy:

Medical safety comes before AI intelligence.