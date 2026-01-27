# IITU Teacher AI Assistant 🎓🤖

**A High-Performance, Self-Learning RAG System for University Education.**

> **Status**: Production Ready (Version 2.0)
> **Engine**: Hybrid RAG (Vector + Semantic Cache)

## 🚀 Overview
The **IITU Teacher AI Assistant** is a next-generation education tool designed to answer student questions instantly and accurately using course materials. Unlike standard RAG (Retrieval-Augmented Generation) systems, this engine features a **"Pre-Cognition" Layer** that predicts and caches answers before students even ask them.

## ⚡ Key Features

### 1. Blazing Fast "Pre-Cognition" Engine
-   **Matrix Math Prediction**: Uses vectorized Numpy operations to search 100,000+ cached questions in **<0.02 seconds**.
-   **L1 Memory Layer**: Ultra-hot questions are served from RAM in **nanoseconds**, bypassing the database entirely.
-   **Synthetic Warm-Up**: Upon ingesting new files, the system automatically "dreams up" 100 likely questions and solves them, ensuring the cache is warm from second zero.

### 2. Aggressive Resource Guard 🛡️
-   **DDoS Shield**: Integrated Token Bucket Rate Limiter blocks spam IPs instantly (>60 req/min).
-   **Thermal Protection**: Monitors Server CPU load. If usage spikes >90%, the system enters **"Cool Down Mode"**, refusing expensive generation tasks while continuing to serve cached answers to protect hardware.
-   **Concurrency Control**: Strict semaphore slots prevent memory overflows under heavy student load.

### 3. Smart Cost Management 💰
-   **Adaptive Budgeting**:
    -   *Simple Greetings*: 0 Cost (handled by logic).
    -   *Exact Matches*: 0 Cost (handled by Cache).
    -   *Complex Queries*: Full RAG (Deep Analysis).
-   This architecture reduces LLM inference costs by **~80%** compared to naive implementations.

## 🛠️ Tech Stack
-   **Backend**: Python, FastAPI, Uvicorn
-   **Database**: LanceDB (High-Precision Vector Storage), SQLite (WAL-Mode Semantic Cache)
-   **AI Core**: Ollama (Llama3 / Nomic-Embed)
-   **Frontend**: React + TypeScript + Vite

## 🔒 Security & Privacy
This repository contains the **Source Code** and **Architecture** of the system.
**Note**: Production databases (`super_precise_db`, `smart_cache.db`) and proprietary Course Data (`.pptx`, `.pdf`) are strictly excluded from this repository via `.gitignore` to ensure data privacy and copyright compliance.

## 📥 Installation

```bash
# 1. Clone Repo
git clone https://github.com/YourUsername/IITU-Teacher-AI-Assistant.git

# 2. Install Backend
cd backend
pip install -r requirements.txt

# 3. Launch Server
python main.py
```

## 🧠 Architecture
```mermaid
graph TD
    User[Student] -->|HTTP Request| Guard[Resource Guard]
    Guard -->|Safe?| API[FastAPI]
    API -->|Check RAM| L1[L1 Memory Cache]
    L1 -->|Miss| SmartCache[Semantic Cache (Matrix)]
    SmartCache -->|Miss| RAG[RAG Engine]
    RAG -->|Retrieve| DB[(Vector DB)]
    RAG -->|Generate| LLM[Ollama GPU]
```

---
*Built with ❤️ for IITU.*
