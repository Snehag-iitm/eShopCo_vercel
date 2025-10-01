import json
import numpy as np
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Load your JSON data
with open("q-vercel-latency.json", "r") as f:
    data = json.load(f)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/")
async def metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 999999)

    results = {}

    for region in regions:
        region_data = [r for r in data if r["region"] == region]
        if not region_data:
            continue

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_pct"] for r in region_data]

        results[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for r in region_data if r["latency_ms"] > threshold)
        }

    return results
