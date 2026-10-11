# tds-vercel-latency

A small serverless endpoint on Vercel that reports latency stats per region
from a sample telemetry file (`api/q-vercel-latency.json`).

## Usage

```bash
curl -X POST https://tds-vercel-latency.vercel.app/api/latency \
  -H "Content-Type: application/json" \
  -d '{"regions": ["apac", "emea"], "threshold_ms": 167}'
```

Response:

```json
{
  "regions": [
    {"region": "apac", "avg_latency": 172.05, "p95_latency": 214.92, "avg_uptime": 98.335, "breaches": 6},
    {"region": "emea", "avg_latency": 178.51, "p95_latency": 217.47, "avg_uptime": 98.508, "breaches": 7}
  ]
}
```

- `avg_latency` – mean latency (ms)
- `p95_latency` – 95th percentile latency (ms)
- `avg_uptime` – mean uptime (%)
- `breaches` – number of pings slower than `threshold_ms`

CORS is open (`Access-Control-Allow-Origin: *`), so it can be called from any dashboard.

## Deploy

```bash
vercel --prod
```

No extra packages needed, it only uses the Python standard library.
