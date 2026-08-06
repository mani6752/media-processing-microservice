"""
Load test for the Media Processing Microservice.
"""

import argparse
import asyncio
import time
import httpx

BASE_URL = "http://localhost:8000"


async def run_one_job(client: httpx.AsyncClient, file_bytes: bytes, filename: str, index: int) -> dict:
    start = time.perf_counter()
    try:
        resp = await client.post(
            f"{BASE_URL}/upload/request-url",
            json={"filename": filename},
        )
        resp.raise_for_status()
        data = resp.json()
        job_id = data["job_id"]
        upload_url = data["upload_url"].replace("mock-s3", "localhost")

        put_resp = await client.put(upload_url, content=file_bytes)
        put_resp.raise_for_status()

        confirm_resp = await client.post(f"{BASE_URL}/upload/confirm/{job_id}")
        confirm_resp.raise_for_status()

        status = "pending"
        for _ in range(30):
            await asyncio.sleep(0.5)
            status_resp = await client.get(f"{BASE_URL}/upload/status/{job_id}")
            status_data = status_resp.json()
            status = status_data.get("status", "unknown")
            if status in ("completed", "failed"):
                break

        elapsed = time.perf_counter() - start
        return {"index": index, "job_id": job_id, "status": status, "elapsed": elapsed, "error": None}

    except Exception as e:
        elapsed = time.perf_counter() - start
        return {"index": index, "job_id": None, "status": "error", "elapsed": elapsed, "error": str(e)}


async def main(concurrency: int, filename: str):
    with open(filename, "rb") as f:
        file_bytes = f.read()

    async with httpx.AsyncClient(timeout=30.0) as client:
        overall_start = time.perf_counter()
        tasks = [run_one_job(client, file_bytes, filename, i) for i in range(concurrency)]
        results = await asyncio.gather(*tasks)
        overall_elapsed = time.perf_counter() - overall_start

    completed = [r for r in results if r["status"] == "completed"]
    failed = [r for r in results if r["status"] == "failed"]
    errored = [r for r in results if r["status"] == "error"]
    timed_out = [r for r in results if r["status"] not in ("completed", "failed", "error")]

    print(f"\n=== Load Test Results ({concurrency} concurrent jobs) ===")
    print(f"Total wall time: {overall_elapsed:.2f}s")
    print(f"Completed:  {len(completed)}")
    print(f"Failed:     {len(failed)}")
    print(f"Errored:    {len(errored)}")
    print(f"Timed out:  {len(timed_out)}")

    if completed:
        times = sorted(r["elapsed"] for r in completed)
        avg = sum(times) / len(times)
        p50 = times[len(times) // 2]
        p95 = times[int(len(times) * 0.95)] if len(times) > 1 else times[0]
        print(f"\nCompleted job timing:")
        print(f"  avg: {avg:.2f}s  p50: {p50:.2f}s  p95: {p95:.2f}s  min: {times[0]:.2f}s  max: {times[-1]:.2f}s")

    if errored:
        print("\nSample errors:")
        for r in errored[:5]:
            print(f"  [{r['index']}] {r['error']}")

    if failed:
        print(f"\n{len(failed)} job(s) reported status=failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--file", type=str, default="test.jpg")
    args = parser.parse_args()

    asyncio.run(main(args.concurrency, args.file))
