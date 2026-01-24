# SmartCare-AI – API Contracts

## Base URL
    /api/v1


---

## 1. Semantic Search

### Endpoint
    POST /semantic-search



### Request
```json
{
  "query": "medicine for headache without stomach pain",
  "top_k": 5
}
```
Response
```json

[
  {
    "drug_id": 101,
    "score": 0.92
  }
]
```

## 2. Similar Drug Recommendation
### Endpoint

    GET /similar-drugs/{drug_id}?top_k=5

Response
```json
[
  {
    "drug_id": 88,
    "score": 0.87
  }
]
```

## 3. Contraindication Check
### Endpoint

    POST /contraindications/check
Request
```json
{
  "new_drug_id": 101,
  "previous_drug_ids": [22, 45]
}
```

Response
```json
 
{
  "safe": false,
  "warnings": [
    {
      "type": "RULE",
      "message": "Warfarin + Aspirin increases bleeding risk"
    }
  ]
}
```

## 4. Health Check
### Endpoint

    GET /health
Response
```json
{
  "status": "ok"
}
```

### 5. Error Format
```json
{
  "stauts_code" : 401
  "error_code": "SERVICE_DISABLED",
  "message": "AI semantic search is currently disabled"
}
```

## 6. API Guarantees

* Versioned APIs

* Backward compatibility

* No medical prescriptions

* AI results are advisory