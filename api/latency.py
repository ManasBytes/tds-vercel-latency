import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# latency pings for each region, loaded once when the function starts
DATA_FILE = Path(__file__).parent / "q-vercel-latency.json"
records = json.loads(DATA_FILE.read_text())


def p95(values):
    # 95th percentile with linear interpolation (same as numpy.percentile)
    values = sorted(values)
    pos = (len(values) - 1) * 0.95
    i = int(pos)
    if i + 1 < len(values):
        return values[i] + (pos - i) * (values[i + 1] - values[i])
    return values[i]


def stats_for(region, threshold):
    rows = [r for r in records if r["region"] == region]
    if not rows:
        return {"region": region, "error": "no data for this region"}

    latency = [r["latency_ms"] for r in rows]
    uptime = [r["uptime_pct"] for r in rows]

    return {
        "region": region,
        "avg_latency": round(sum(latency) / len(latency), 2),
        "p95_latency": round(p95(latency), 2),
        "avg_uptime": round(sum(uptime) / len(uptime), 3),
        "breaches": sum(1 for ms in latency if ms > threshold),
    }


class handler(BaseHTTPRequestHandler):
    def reply(self, status, body=None):
        self.send_response(status)
        # allow dashboards on any site to call this
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if body is not None:
            self.wfile.write(json.dumps(body).encode())

    def do_OPTIONS(self):
        # browsers send this before the real POST
        self.reply(204)

    def do_POST(self):
        try:
            size = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(size) or b"{}")
            regions = payload.get("regions", [])
            threshold = float(payload.get("threshold_ms", 180))
        except (ValueError, AttributeError):
            return self.reply(400, {"error": "expected JSON like {\"regions\": [\"apac\"], \"threshold_ms\": 180}"})

        self.reply(200, {"regions": [stats_for(r, threshold) for r in regions]})

    def do_GET(self):
        self.reply(200, {"message": "send a POST with {\"regions\": [...], \"threshold_ms\": 180}"})
