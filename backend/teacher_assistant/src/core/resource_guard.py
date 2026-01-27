import time
import threading
from typing import Tuple, Dict
import logging

try:
    import psutil
except ImportError:
    psutil = None

class ResourceGuard:
    """
    PROTECTION LAYER:
    1. DDoS Shield (Rate Limiting)
    2. Overheating Guard (CPU Load Throttling)
    3. Concurrency Control (Slot Management)
    """
    def __init__(self, max_concurrent=50, max_cpu_percent=90.0):
        self.max_concurrent = max_concurrent
        self.max_cpu_percent = max_cpu_percent
        self.active_requests = 0
        self.lock = threading.Lock()
        
        # Rate Limiting (IP based) - Token Bucket equivalent
        self.ip_requests: Dict[str, list] = {} 
        self.rate_limit_window = 60 # 1 minute
        self.max_requests_per_min = 60 # 1 req/sec per IP average
        
        # Queue System
        self.pending_queue = [] # List of ticket_ids
        self.avg_processing_time = 2.0 # seconds
        self.processed_count_window = 0
        self.cool_down_until = 0

    def check_health(self) -> Tuple[bool, str]:
        """
        Returns (is_healthy, message). 
        If unhealthy (Overheating), system should switch to CACHE-ONLY mode.
        """
        
        # 1. Check Cool Down Timer
        if time.time() < self.cool_down_until:
             return False, "System in Cool Down Mode (Overheating Protection)"

        # 2. Check CPU Load (if psutil available)
        if psutil:
            # interval=None is non-blocking (returns last interval stats)
            # We use a small Blocking call elsewhere or just rely on instant check
            # For API speed, we don't want to block 1s. 
            # psutil.cpu_percent() without interval returns immediately since last call.
            cpu_usage = psutil.cpu_percent(interval=None)
            
            if cpu_usage > self.max_cpu_percent:
                self.cool_down_until = time.time() + 10 # Cool down for 10s
                return False, f"CPU Overheating ({cpu_usage}%). Engaged Cool Down."
        
        return True, "Healthy"

    def get_queue_status(self, ticket_id: str) -> Dict:
        with self.lock:
            try:
                pos = self.pending_queue.index(ticket_id)
                return {
                    "status": "queued",
                    "position": pos + 1,
                    "wait_time": (pos + 1) * self.avg_processing_time
                }
            except ValueError:
                return {"status": "unknown", "position": -1, "wait_time": 0}

    def join_queue(self) -> str:
        """User joins the waiting line. Returns a ticket ID."""
        import uuid
        ticket_id = str(uuid.uuid4())
        with self.lock:
            self.pending_queue.append(ticket_id)
        return ticket_id

    def leave_queue(self, ticket_id: str):
        with self.lock:
            if ticket_id in self.pending_queue:
                self.pending_queue.remove(ticket_id)

    def acquire_slot(self, ticket_id: str = None) -> Tuple[bool, str]:
        """
        Concurrency control with Queue Awareness.
        Returns: (Success, Message)
        """
        with self.lock:
            # If system is full
            if self.active_requests >= self.max_concurrent:
                return False, "System Busy"

            # If there is a queue, ONLY the head of the queue can enter
            if self.pending_queue:
                if not ticket_id: 
                    # Newcomer trying to skip line? No.
                    return False, "Queue Required"
                
                if ticket_id != self.pending_queue[0]:
                    # User is in queue but not first
                    return False, "Wait Your Turn"
                
                # User is first! Let them in.
                self.pending_queue.pop(0)

            # Grant Access
            self.active_requests += 1
            return True, "Access Granted"

    def release_slot(self):
        with self.lock:
            self.active_requests = max(0, self.active_requests - 1)

    def check_rate_limit(self, ip: str) -> bool:
        """
        Check if IP has exceeded rate limit.
        Returns True if allowed, False if blocked.
        """
        now = time.time()
        with self.lock:
            if ip not in self.ip_requests:
                self.ip_requests[ip] = []
            
            # Filter out old requests (Window slide)
            # Efficiency: If list gets too long, this protects memory
            self.ip_requests[ip] = [t for t in self.ip_requests[ip] if now - t < self.rate_limit_window]
            
            if len(self.ip_requests[ip]) >= self.max_requests_per_min:
                return False # Block
            
            self.ip_requests[ip].append(now)
            return True
