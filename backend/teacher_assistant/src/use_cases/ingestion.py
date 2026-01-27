import os
import pdfplumber
from pptx import Presentation
from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..infrastructure.database import VectorDatabase
from ..infrastructure.ollama_client import OllamaClient

class IngestionService:
    def __init__(self, db: VectorDatabase, llm: OllamaClient, rag_service=None):
        self.db = db
        self.llm = llm
        self.rag_service = rag_service
        # OPTIMIZED: Larger chunks for better context preservation
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,      # Full paragraphs
            chunk_overlap=100    # Better continuity
        )

    def process_directory(self, directory: str):
        from tqdm import tqdm
        all_chunks = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.pdf', '.pptx', '.docx')):
                    path = os.path.join(root, file)
                    print(f"📄 {file}")
                    chunks = self._parse_file(path)
                    all_chunks.extend(chunks)
        
        if not all_chunks:
            print("⚠️ No chunks found!")
            return

        print(f"🧠 Embedding {len(all_chunks)} chunks on GPU...")
        
        batch_size = 50  # Smaller batches for stability
        for i in tqdm(range(0, len(all_chunks), batch_size), desc="GPU Indexing"):
            batch = all_chunks[i : i + batch_size]
            texts = [c['content'] for c in batch]
            try:
                vectors = self.llm.get_embeddings_batch(texts)
                for j, v in enumerate(vectors):
                    batch[j]['vector'] = v
            except Exception as e:
                print(f"⚠️ Batch failed, using single: {e}")
                for c in batch:
                    c['vector'] = self.llm.get_embedding(c['content'])
            
        self.db.insert_chunks(all_chunks)
        print(f"✅ Indexed {len(all_chunks)} chunks (800 chars each)")
        
        # TRIGGER SYNTHETIC WARMING
        if self.rag_service:
            self._warm_up_cache(all_chunks)

    def _warm_up_cache(self, chunks):
        print("\n🚀 STARTING SYNTHETIC CACHE WARM-UP (Auto-Prediction)...")
        import random
        from tqdm import tqdm
        
        # Pick 20 random chunks to generate questions from (to get ~100 questions)
        # Ideally we'd pick 'dense' chunks, but random is fine for coverage
        samples = random.sample(chunks, min(len(chunks), 20))
        
        generated_qs = []
        
        print("Phase 1: Dreaming up questions...")
        for chunk in tqdm(samples, desc="Generating Qs"):
            text = chunk['content'][:1000]
            prompt = (
                f"TEXT: {text}\n\n"
                "TASK: Generate 5 specific student questions about this text.\n"
                "FORMAT: Just the questions, one per line."
            )
            try:
                # Use simple chat for speed
                resp = self.llm.chat("You are a question generator.", prompt)
                qs = [q.strip() for q in resp.split('\n') if '?' in q]
                generated_qs.extend(qs)
            except Exception as e:
                print(f"Gen error: {e}")
                
        print(f"Phase 2: Answering & Caching {len(generated_qs)} questions...")
        for q in tqdm(generated_qs, desc="Warming Cache"):
            if len(q) < 5: continue
            try:
                # answering automatically SAVES to cache
                self.rag_service.answer_question(q)
            except Exception as e:
                pass
                
        print(f"✅ CACHE WARMED: {len(generated_qs)} predictions ready.")

    def _parse_file(self, path: str):
        ext = os.path.splitext(path)[1].lower()
        fname = os.path.basename(path)
        # Clean filename for embedding (remove extension and numbers)
        import re
        clean_name = fname
        for e in [".pptx", ".docx", ".pdf"]:
            clean_name = clean_name.replace(e, "")
        clean_name = re.sub(r'^\d+\s*[-–]\s*', '', clean_name).strip()
        
        blocks = []
        try:
            if ext == ".pptx":
                prs = Presentation(path)
                for i, slide in enumerate(prs.slides):
                    # Get slide title if available
                    title = ""
                    for shape in slide.shapes:
                        if shape.has_text_frame and shape.text_frame.paragraphs:
                            title = shape.text_frame.paragraphs[0].text[:50]
                            break
                    text = " ".join([s.text for s in slide.shapes if hasattr(s, "text")])
                    if text.strip():
                        loc = f"Slide {i+1}" + (f": {title}" if title else "")
                        blocks.append({"text": text, "loc": loc})
            elif ext == ".pdf":
                with pdfplumber.open(path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text:
                            blocks.append({"text": text, "loc": f"Page {i+1}"})
            elif ext == ".docx":
                doc = Document(path)
                # Group paragraphs for better context
                current_text = ""
                for i, p in enumerate(doc.paragraphs):
                    if p.text.strip():
                        current_text += p.text + " "
                        if len(current_text) > 500:  # Group small paragraphs
                            blocks.append({"text": current_text, "loc": f"Section {len(blocks)+1}"})
                            current_text = ""
                if current_text.strip():
                    blocks.append({"text": current_text, "loc": f"Section {len(blocks)+1}"})
        except Exception as e:
            print(f"⚠️ Error parsing {fname}: {e}")

        final_chunks = []
        for b in blocks:
            splits = self.splitter.split_text(b['text'])
            for s in splits:
                # EMBED filename in content for FTS precision
                enriched_content = f"[{clean_name}] {s}"
                final_chunks.append({
                    "content": enriched_content,
                    "source": fname,
                    "location": b['loc']
                })
        return final_chunks
