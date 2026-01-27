import asyncio
import httpx
import time
import statistics
import concurrent.futures

BASE_URL = "http://localhost:8000"

async def lone_chat_request(client, course_id, message):
    start = time.time()
    try:
        response = await client.post(
            f"{BASE_URL}/api/chat",
            json={"message": message, "course_id": course_id, "is_voice": False},
            timeout=30.0
        )
        latency = time.time() - start
        return response.status_code, latency
    except Exception as e:
        return 500, time.time() - start

async def run_stress_test(concurrency=10, total_requests=50):
    print(f"🚀 Starting Stress Test: {total_requests} requests, {concurrency} concurrent...")
    
    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(total_requests):
            tasks.append(lone_chat_request(client, f"stress_course_{i%3}", "Test message for stress testing"))
        
        # Run in batches to simulate real concurrency
        results = []
        for i in range(0, len(tasks), concurrency):
            batch = tasks[i : i + concurrency]
            results.extend(await asyncio.gather(*batch))
            
        return results

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(run_stress_test())
    
    status_codes = [r[0] for r in results]
    latencies = [r[1] for r in results]
    
    print("\n📊 STRESS TEST RESULTS")
    print(f"Total Requests: {len(results)}")
    print(f"Success Rate: {(status_codes.count(200)/len(results))*100:.1f}%")
    print(f"Rate Limited (429): {status_codes.count(429)}")
    print(f"Server Busy (503): {status_codes.count(503)}")
    print(f"Avg Latency: {statistics.mean(latencies):.4f}s")
    print(f"95th Percentile: {statistics.quantiles(latencies, n=20)[18]:.4f}s")
    print(f"Max Latency: {max(latencies):.4f}s")
