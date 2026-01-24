# SmartCare-AI – System Architecture

## 1. Overview

SmartCare-AI is an AI microservice designed to support an Online Pharmacy platform.
It provides intelligent, assistive capabilities while maintaining strict medical
safety boundaries.

The AI system is **advisory only** and never replaces pharmacists or medical professionals.

---

## 2. Core Responsibilities

The AI service is responsible for:

1. Semantic Drug Search (search by meaning)
2. Drug Similarity & Recommendation
3. Contraindication & Drug Interaction Detection

---

## 3. High-Level System Architecture

        Flutter App
        ↓
        .NET Backend (Auth, Orders, Drugs, Users)
        ↓
        SmartCare-AI (Flask)
        ↓
        Vector DB (FAISS / Qdrant)


### Key Principles
- MSSQL is the **system of record**
- Vector DB is **derived data**
- AI logic is isolated in a dedicated service
- Deterministic rules override AI output

---

## 4. AI Request Lifecycle

All AI requests follow the same invariant flow:

API Layer
→ Service Layer
→ Pipeline Layer
→ Domain Rules
→ Vector Search / AI Models
→ Ranking
→ Response

---

## 5. Internal AI Pipeline Design

### 5.1 API Layer
Responsibilities:
- Request validation
- Authentication & rate limiting
- API versioning

No business or AI logic exists here.

---

### 5.2 Service Layer
Responsibilities:
- Use-case orchestration
- Feature flag checks
- Error handling

---

### 5.3 Pipeline Layer (Core Intelligence)

Pipelines enforce **order**, **safety**, and **explainability**.

---

## 6. Pipeline Definitions

### 6.1 Semantic Search Pipeline

User Query
        → Text Cleaning
        → Embedding
        → Vector Search
        → Relevance Filter
        → Safety Filter
        → Ranking
        → Response


---

### 6.2 Similarity & Recommendation Pipeline

Drug ID
    → Fetch Existing Embedding
    → Vector Similarity Search
    → Exclude Same Drug
    → Safety Filter
    → Ranking

---

### 6.3 Contraindication Pipeline (Safety-Critical)

New Drug
    → Deterministic Rule Engine (Hard Stop)
    → Drug Class Overlap
    → AI Semantic Risk Scan
    → Explainability Builder
    → Response

---

## 7. Decision Priority Model

| Priority | Source | Can Block |
|--------|--------|-----------|
| 1 | Deterministic Medical Rules | ✅ Yes |
| 2 | Drug Class Overlap | ⚠️ Warning |
| 3 | AI Semantic Risk Detection | ⚠️ Warning |
| 4 | AI / LLM Explanation | ❌ No |

AI output **never overrides** medical rules.

---

## 8. Embedding Strategy

- Embeddings are versioned
- Each vector includes metadata:
  - drug_id
  - embedding_version
- Changing embedding version requires full reindexing

---

## 9. Vector Database Strategy

- FAISS: Local development & testing
- Qdrant: Production

Vector DB is **stateless** and **rebuildable**.

---

## 10. Safety Guarantees

- AI does not prescribe medication
- AI does not make final medical decisions
- All warnings are explainable
- Pharmacist override is always available

---

## 11. Observability & Auditing

All AI decisions are logged:
- Input
- Output
- Warnings
- Overrides

This supports audits and regulatory review.

---

## 12. Non-Goals

- AI diagnosis
- AI prescription
- Autonomous medical decisions

---

## 13. Summary

SmartCare-AI is designed to be:
- Safe
- Explainable
- Replaceable
- Scalable

Medical safety always comes before AI intelligence.