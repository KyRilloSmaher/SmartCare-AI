# SmartCare-AI – Vector Database Strategy

## 1. Purpose

Vector databases enable:
- Semantic search
- Similarity detection
- AI-assisted safety analysis

They do NOT replace relational databases.

---

## 2. Source of Truth

- MSSQL is the system of record
- Vector DB is derived and rebuildable

---

## 3. Supported Vector Stores

| Environment | Vector DB |
|-----------|-----------|
| Local / Dev | FAISS |
| Production | Qdrant |

---

## 4. Interface-Based Design

All vector DB operations implement a shared interface:

- add()
- search()
- delete()
- health_check()

This allows seamless switching.

---

## 5. Embedding Lifecycle

1. Extract drug data from MSSQL
2. Build embedding text
3. Generate vector
4. Store vector + metadata
5. Link via drug_id

---

## 6. Sync Strategy

### Option A: Event-Based (Preferred)
- Drug created / updated
- Emit event
- Re-embed drug

### Option B: Scheduled Sync
- Nightly job
- Compare updated timestamps

---

## 7. Versioning & Rebuilds

Changing:
- Embedding model
- Text template
- Dimension

Requires:
Full vector rebuild


    Handled via background jobs.

---

## 8. Failure Handling

- Vector DB failure does not block core pharmacy features
- AI features can be disabled via feature flags

---

## 9. Summary

Vector databases enhance intelligence but never compromise safety.