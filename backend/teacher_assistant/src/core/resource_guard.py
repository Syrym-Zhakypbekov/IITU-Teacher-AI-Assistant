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
        
        # Cool Down Mode
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

    def acquire_slot(self) -> bool:
        """Concurrency control."""
        with self.lock:
            if self.active_requests >= self.max_concurrent:
                return False
            self.active_requests += 1
            return True

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
