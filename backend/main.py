import os
import sys
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(BASE_DIR)

from data_loader import DataLoader
from nlp_extractor import NLPExtractor
from graph_engine import GraphEngine
from pattern_detector import PatternDetector
from benchmark_evaluator import BenchmarkEvaluator
from copilot import CaseCopilot

app = FastAPI(
    title="NetSentinel AI - Criminal Network Intelligence & Analytics",
    description="Automated multi-source criminal network detection, forensic analytics, and AI case copilot",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
DATA_DIR = os.path.join(PROJECT_DIR, "data")
dl = DataLoader(DATA_DIR)
nlp = NLPExtractor(dl.entities)
ge = GraphEngine(dl, nlp)
pd = PatternDetector(dl, ge)
be = BenchmarkEvaluator(dl, ge)
copilot = CaseCopilot(dl, ge, pd)

class CopilotQueryRequest(BaseModel):
    query: str

@app.get("/api/health")
def health_check():
    return {"status": "ONLINE", "version": "2.0.0", "entities_loaded": len(dl.entities)}

@app.get("/api/network")
def get_network(
    syndicate: str = Query(None, description="Filter by syndicate or community"),
    role: str = Query(None, description="Filter by role"),
    min_threat: float = Query(0.0, description="Minimum threat score"),
    criminal_only: bool = Query(False, description="Filter to criminals only")
):
    data = ge.get_network_json()
    nodes = data["nodes"]
    edges = data["edges"]

    # Filter nodes
    valid_ids = set()
    filtered_nodes = []
    for n in nodes:
        d = n["data"]
        if min_threat and d["threat_score"] < min_threat:
            continue
        if criminal_only and not d["is_criminal"]:
            continue
        if role and role.lower() not in d["role"].lower():
            continue
        if syndicate and syndicate.lower() not in d["community"].lower():
            continue
        valid_ids.add(d["id"])
        filtered_nodes.append(n)

    filtered_edges = [
        e for e in edges
        if e["data"]["source"] in valid_ids and e["data"]["target"] in valid_ids
    ]

    return {
        "nodes": filtered_nodes,
        "edges": filtered_edges,
        "stats": data["stats"],
        "filtered_count": len(filtered_nodes)
    }

@app.get("/api/entity/{eid}")
def get_entity_profile(eid: str):
    profile = copilot.inspect_entity(eid)
    if "error" in profile:
        return JSONResponse(status_code=404, content=profile)
    return profile

@app.get("/api/benchmark")
def get_benchmark():
    return be.evaluate()

@app.get("/api/alerts")
def get_alerts():
    return pd.get_all_alerts()

@app.get("/api/kingpins")
def get_kingpins():
    kingpin_eids = [eid for eid, r in ge.detected_roles.items() if "Kingpin" in r]
    details = []
    for k in kingpin_eids:
        ent = dl.entities[k]
        details.append({
            "entity_id": k,
            "name": ent["name"],
            "role": ge.detected_roles.get(k),
            "threat_score": ge.threat_scores.get(k),
            "syndicate": ge.communities.get(k),
            "phone": ent["phone_number"],
            "vehicle": ent["vehicle_number"],
            "organization": ent["known_organization"],
            "pagerank": round(ge.pagerank.get(k, 0), 4)
        })
    return {"kingpins": details}

@app.get("/api/bridges")
def get_bridges():
    bridge_eids = [eid for eid, b in ge.is_bridge_pred.items() if b]
    details = []
    for b in bridge_eids:
        ent = dl.entities[b]
        details.append({
            "entity_id": b,
            "name": ent["name"],
            "threat_score": ge.threat_scores.get(b),
            "betweenness": round(ge.betweenness_centrality.get(b, 0), 4),
            "connected_communities": list({ge.communities.get(n) for n in ge.G.neighbors(b) if ge.communities.get(n)}),
            "phone": ent["phone_number"],
            "vehicle": ent["vehicle_number"]
        })
    return {"bridges": details}

@app.get("/api/path")
def find_path(source: str = Query(..., description="Source Entity ID"), target: str = Query(..., description="Target Entity ID")):
    return copilot.find_shortest_conspiracy_path(source, target)

@app.post("/api/copilot/query")
def copilot_chat(req: CopilotQueryRequest):
    return copilot.query_copilot(req.query)

@app.get("/api/dossier/{eid}")
def download_dossier(eid: str):
    if eid not in dl.entities:
        return PlainTextResponse(f"Entity {eid} not found", status_code=404)
    dossier_text = copilot.generate_dossier_markdown(eid)
    return PlainTextResponse(dossier_text, media_type="text/markdown")

frontend_dir = os.path.join(PROJECT_DIR, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>NetSentinel AI Backend Online.</h1>")

if __name__ == "__main__":
    import os
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))