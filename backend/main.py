from fastapi import FastAPI, BackgroundTasks, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import contextlib

from teacher_assistant.src.core.models import ChatRequest, ChatResponse
from teacher_assistant.src.core.resource_guard import ResourceGuard
from teacher_assistant.src.infrastructure.database import VectorDatabase
from teacher_assistant.src.infrastructure.ollama_client import OllamaClient
from teacher_assistant.src.use_cases.rag_engine import RAGService
from teacher_assistant.src.use_cases.ingestion import IngestionService

# --- CONFIGURATION ---
DB_PATH = "./super_precise_db"
API_TITLE = "IITU Teacher Assistant AI"
API_VERSION = "2.0.0 (SmartCache/ResourceGuard)"

# --- LIFESPAN MANAGER (Startup/Shutdown) ---
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"\n🚀 {API_TITLE} Starting...")
    print(f"✅ Resource Guard: Active (Limit: 50 slots, Overheat: 90%)")
    print(f"✅ Smart Cache: Active (Matrix/L1)")
    yield
    # Shutdown
    print(f"🛑 {API_TITLE} Shutting down...")

# --- APP SETUP ---
app = FastAPI(title=API_TITLE, version=API_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DEPENDENCIES ---
db = VectorDatabase(db_path=DB_PATH)
llm = OllamaClient()
guard = ResourceGuard(max_concurrent=50, max_cpu_percent=90.0)

# Services
rag_service = RAGService(db, llm)
ingestion_service = IngestionService(db, llm, rag_service)

# --- ENDPOINTS ---
@app.get("/health")
async def health():
    """System Vital Signs."""
    is_healthy, msg = guard.check_health()
    return {
        "status": "online" if is_healthy else "degraded",
        "health_message": msg,
        "version": API_VERSION,
        "database_docs": db.count()
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, raw_request: Request):
    """
    Core Chat Interface.
    Protected by ResourceGuard (DDoS & Overheat).
    Optimized by SmartCache (Matrix & L1).
    """
    client_ip = raw_request.client.host if raw_request.client else "unknown"
    
    # 1. DDoS Guard
    if not guard.check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate Limit Exceeded. Slow down.")

    # 2. Concurrency Slot
    if not guard.acquire_slot():
         raise HTTPException(status_code=503, detail="Server Busy. Try again later.")
    
    try:
        # 3. Overheat Check
        is_healthy, _ = guard.check_health()
        force_cache = not is_healthy
        
        # 4. Process Request
        response = rag_service.answer_question(request.message, force_cache_only=force_cache)
        
        if force_cache and response.status == "cached":
             response.response += "\n\n(Generated from cache while system is cooling down ❄️)"
             
        return response
    finally:
        guard.release_slot()

@app.post("/api/ingest")
async def ingest(background_tasks: BackgroundTasks):
    """
    Ingest & Warm-Up.
    scans 'doc_dir', indexes content, and auto-generates 100 likely questions.
    """
    doc_dir = r"C:\Users\syrym\Downloads\IITU-Teacher-AI-Assistant\Управление разработкой программного обеспечения и реинжиниринг"
    background_tasks.add_task(ingestion_service.process_directory, doc_dir)
    return {"message": "Ingestion & Synthetic Warm-Up started in background."}

if __name__ == "__main__":
    print("💎 LAUNCHING PRODUCTION SERVER 💎")
    uvicorn.run(app, host="0.0.0.0", port=8000)
