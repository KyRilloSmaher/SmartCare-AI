# SmartCare-AI: Feature Workflow Deep Dive

This document provides a comprehensive technical breakdown of the SmartCare-AI features, detailing the workflows, machine learning models, and system interactions.

---

## 1. System Overview
SmartCare-AI is a professional medical assistance platform that leverages computer vision, natural language processing (NLP), and vector search to provide insights into drugs, interactions, and medical queries.

---

## 2. Feature Deep Dives



### 2.1 Semantic Search (Neural Search Pipeline)
**Purpose**: Find relevant medical products or information using natural language queries rather than exact keyword matches.

#### **Workflow**:
1.  **Query Input**: User enters a query like "medication for high blood pressure".
2.  **Preprocessing**:
    -   **Text Cleaning**: Removes special characters and standardizes text.
    -   **Language Detection**: Determines the language of the query.
3.  **Embedding Generation**:
    -   The query is converted into a high-dimensional vector using the **intfloat/e5-small** model.
4.  **Medical Validation (Safety Layer)**:
    -   The system compares the query vector against a "Medical Reference Vector" (pre-computed from medical keywords).
    -   If the cosine similarity is below **0.8**, the system rejects the query as "Non-Medical" for safety and focus.
5.  **Vector Search**:
    -   The validated query vector is sent to the **Qdrant Vector Database**.
    -   Qdrant performs a **Cosine Similarity** search against the stored product embeddings.
6.  **Response**: Returns the top K most relevant medical products/entities.

**Models Used**:
-   **intfloat/e5-small (HuggingFace)**: Text embeddings.
-   **Qdrant**: Vector storage and search engine.

---

### 2.2 Drug Similarity (Neighbor Search)
**Purpose**: Find drugs that are chemically or therapeutically similar to a specific product.

#### **Workflow**:
1.  **Product Selection**: User provides a `product_id`.
2.  **Vector Retrieval**: The system fetches the pre-calculated embedding for that specific product from Qdrant.
3.  **Neighbor Search**:
    -   Uses the product's own vector as a query to find its "nearest neighbors" in the vector space.
4.  **Filtering**:
    -   Excludes the original product from results.
    -   Applies a similarity threshold to ensure only truly similar drugs are returned.
5.  **Response**: Returns a list of similar drugs with their similarity scores.

**Models Used**:
-   **intfloat/e5-small**: Underlying embedding model.
-   **Qdrant**: Nearest neighbor search.

---
### 2.3 Voice Search
**Purpose**: Allow users to perform semantic searches using their voice.

#### **Workflow**:
1.  **Audio Capture**: User records a query (e.g., "What can I take for a headache?").
2.  **Transcription**:
    -   The audio file is processed by the **Transcription Service**.
    -   Converts speech to a text string.
3.  **Semantic Search Integration**:
    -   The transcribed text is passed directly into the **Semantic Search Pipeline** (Cleaning -> Embedding -> Validation -> Qdrant Search).
4.  **Response**: Returns medical results based on the spoken query.

---

### 2.4 Drug Name Extraction (Computer Vision Pipeline)
**Purpose**: Automatically identify and extract active ingredient names from images of medicine packaging or prescriptions.

#### **Workflow**:
1.  **Image Upload**: The user uploads an image (JPG/PNG).
2.  **Object Detection (YOLOv8)**:
    -   The system uses a custom-trained **YOLOv8** model (`best (1).pt`) to scan the image.
    -   It identifies specific "Regions of Interest" (ROIs) where drug names or active ingredients are likely located.
3.  **Image Cropping**: For every detection above a certain confidence threshold, the system crops the original image to isolate the text area.
4.  **Optical Character Recognition (OCR)**:
    -   Each cropped ROI is sent to the **OCR.space API**.
    -   The API returns the raw text found within the crop.
5.  **Post-Processing**:
    -   The system cleans the extracted text (removes noise, standardizes casing).
    -   It deduplicates entries to provide a clean list of active ingredients.
6.  **Response**: Returns the bounding box coordinates (for UI highlighting) and the list of extracted ingredients.

**Models Used**:
-   **YOLOv8 (Ultralytics)**: Object detection.
-   **OCR.space API**: Text extraction.

---


### 2.5 Medical Chat Assistant (RAG & LLM)
**Purpose**: A conversational interface to answer medical questions, specifically about provided ingredients.

#### **Workflow**:
1.  **Multi-Modal Input**: Accepts text questions, a list of ingredients, and/or voice messages.
2.  **Voice Processing (Optional)**: If audio is provided, it is transcribed to text using the **Transcription Provider (Whisper-like)**.
3.  **Prompt Engineering**:
    -   The system constructs a robust "System Prompt" that forces the AI to act as a **Professional Medical Assistant**.
    -   It injects the **Active Ingredients** as context.
    -   It enforces a strict "Medical Only" policy: if the question isn't medical, the AI is instructed to refuse the answer.
4.  **LLM Inference**:
    -   The prompt is sent to an LLM (e.g., **GPT-4o/GPT-3.5 via OpenRouter**).
    -   The AI generates a structured response covering: Uses, Side Effects, Contraindications, Warnings, and Interactions.
5.  **Response**: The user receives a comprehensive medical briefing.

**Models Used**:
-   **GPT-4/OpenRouter**: LLM for reasoning and generation.
-   **Transcription Model**: Speech-to-text.

---



## 3. Data Synchronization (Sync Vector DB)
**Purpose**: Ensures the vector database (Qdrant) is always up-to-date with the main product database.

#### **Workflow**:
1.  **Fetch Products**: Retrieves all products from the relational database (SQLAlchemy).
2.  **Batch Embedding**:
    -   Groups products into batches.
    -   Combines product metadata (Name, Description, Active Ingredients) into a single text block per product.
    -   Generates embeddings for these blocks using **e5-small**.
3.  **Upsert**: Pushes the vectors and metadata payloads into **Qdrant**.

---

## 4. Summary of Key Models

| Feature | Primary Model | Purpose |
| :--- | :--- | :--- |
| **Drug Extraction** | YOLOv8 | ROI Detection on packaging |
| **Embeddings** | intfloat/e5-small | Text Vectorization |
| **Search/Similarity** | Cosine Similarity (Qdrant) | High-speed neural retrieval |
| **Chat** | GPT-4 / OpenRouter | Conversational Reasoning |
| **Transcription** | Whisper-based | Voice-to-Text Conversion |
| **OCR** | OCR.space | Image-to-Text Conversion |
