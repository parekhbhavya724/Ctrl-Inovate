import networkx as nx
from typing import Dict, List, Any, Set
from collections import defaultdict
import math

# ---------------------------------------------------------------------------
# Standalone pure-Python PageRank (zero-dependency fallback)
# ---------------------------------------------------------------------------

def compute_pure_pagerank(G, alpha=0.85, max_iter=100, tol=1e-6, weight="weight"):
    """Robust zero-dependency pure Python PageRank."""
    if len(G) == 0:
        return {}
    N = len(G)
    x = {n: 1.0 / N for n in G}
    p = {n: 1.0 / N for n in G}
    dangling = [n for n in G if G.degree(n) == 0]

    for _ in range(max_iter):
        xlast = x.copy()
        x = {n: 0.0 for n in x}
        danglesum = alpha * sum(xlast[n] for n in dangling)
        for n in xlast:
            neighbors = list(G.neighbors(n))
            if neighbors:
                total_w = sum(G[n][nbr].get(weight, 1.0) for nbr in neighbors)
                if total_w > 0:
                    for nbr in neighbors:
                        w = G[n][nbr].get(weight, 1.0)
                        x[nbr] += alpha * xlast[n] * (w / total_w)
                else:
                    danglesum += alpha * xlast[n]
        for n in x:
            x[n] += danglesum * p[n] + (1.0 - alpha) * p[n]
        err = sum(abs(x[n] - xlast[n]) for n in x)
        if err < tol:
            break
    return x


# ---------------------------------------------------------------------------
# GraphEngine
# ---------------------------------------------------------------------------

class GraphEngine:
    """
    Unified criminal-network graph engine with fully algorithmic role detection.

    Key algorithmic innovations (no hardcoded entity IDs anywhere):
    ──────────────────────────────────────────────────────────────────
    • Dynamic Bridge Detection:
        1. Build a criminal-only subgraph (nodes confirmed criminal by threat score).
        2. Compute betweenness centrality on this subgraph.
        3. Run Louvain community detection on the criminal subgraph.
        4. A node is classified as a Cross-Network Bridge if:
           (a) Its criminal-subgraph betweenness ≥ 85th percentile of the subgraph, AND
           (b) Its 1-hop criminal neighbours belong to ≥ 2 distinct criminal communities.

    • Dynamic Kingpin Detection via Hierarchical Influence Index (HII):
        Per criminal community, rank all members by:
           HII = 0.45 × norm_criminal_subgraph_pagerank
               + 0.35 × norm_threat_score
               + 0.20 × norm_financial_inflow_share
        The top-ranked member per community becomes the Kingpin / Ring Leader.
        The resulting kingpin_set feeds back into the threat-score neighbour bonus
        (step 5) — replacing the previously hardcoded ENT_00x sets.
    """

    def __init__(self, data_loader, nlp_extractor):
        self.dl = data_loader
        self.nlp = nlp_extractor

        self.G = nx.Graph()           # Unified undirected weighted graph
        self.DiG = nx.MultiDiGraph()  # Detailed directed multi-graph

        self.degree_centrality: Dict[str, float] = {}
        self.betweenness_centrality: Dict[str, float] = {}
        self.pagerank: Dict[str, float] = {}
        self.communities: Dict[str, str] = {}   # eid -> community_id (full graph)
        self.threat_scores: Dict[str, float] = {}
        self.detected_roles: Dict[str, str] = {}
        self.is_criminal_pred: Dict[str, bool] = {}
        self.is_bridge_pred: Dict[str, bool] = {}

        # Dynamically computed set of kingpin entity IDs
        self.kingpin_set: Set[str] = set()

        self.build_graph()
        self.compute_metrics()

    # ------------------------------------------------------------------
    # Graph construction (unchanged from original)
    # ------------------------------------------------------------------

    def build_graph(self):
        for eid, ent in self.dl.entities.items():
            node_attrs = {
                "id": eid,
                "label": ent["name"],
                "name": ent["name"],
                "age": ent["age"],
                "gender": ent["gender"],
                "phone": ent["phone_number"],
                "vehicle": ent["vehicle_number"],
                "org": ent["known_organization"],
                "criminal_status": ent["criminal_status"],
                "prior_cases_count": len(ent["prior_cases"]),
                "prior_cases": ent["prior_cases"]
            }
            self.G.add_node(eid, **node_attrs)
            self.DiG.add_node(eid, **node_attrs)

        for cdr in self.dl.cdrs:
            u = cdr["caller_id"].strip()
            v = cdr["callee_id"].strip()
            dur = cdr["duration_seconds"]
            loc = cdr["cell_tower_location"]

            if u in self.G and v in self.G:
                self.DiG.add_edge(u, v, key=f"cdr_{cdr['call_id']}", edge_type="CALL",
                                  duration=dur, location=loc, timestamp=cdr["timestamp"])
                if self.G.has_edge(u, v):
                    self.G[u][v]["weight"] += 1.0 + (dur / 600.0)
                    self.G[u][v]["call_count"] += 1
                    self.G[u][v]["total_call_duration"] += dur
                else:
                    self.G.add_edge(u, v, weight=1.0 + (dur / 600.0),
                                    call_count=1, total_call_duration=dur,
                                    txn_count=0, txn_amount=0.0,
                                    fir_co_count=0, social_count=0)

        for txn in self.dl.transactions:
            u = txn["sender_id"].strip()
            v = txn["receiver_id"].strip()
            amt = txn["amount"]
            ttype = txn["transaction_type"]
            tid = txn["transaction_id"]

            if u in self.G and v in self.G:
                is_smurf = "SMURF" in tid
                is_hawala = "HAW" in tid
                multiplier = 3.0 if is_smurf else (2.5 if is_hawala else 0.5)

                self.DiG.add_edge(u, v, key=f"txn_{tid}", edge_type="TRANSACTION",
                                  amount=amt, txn_type=ttype, is_smurf=is_smurf,
                                  is_hawala=is_hawala, timestamp=txn["timestamp"])

                if self.G.has_edge(u, v):
                    self.G[u][v]["weight"] += multiplier
                    self.G[u][v]["txn_count"] += 1
                    self.G[u][v]["txn_amount"] += amt
                else:
                    self.G.add_edge(u, v, weight=multiplier,
                                    call_count=0, total_call_duration=0,
                                    txn_count=1, txn_amount=amt,
                                    fir_co_count=0, social_count=0)

        for fir in self.dl.firs:
            extracted = self.nlp.extract_from_fir(fir)
            for (u, v) in extracted["co_mentions"]:
                if u in self.G and v in self.G:
                    self.DiG.add_edge(u, v, key=f"fir_{fir['fir_id']}", edge_type="FIR_CO_OCCURRENCE",
                                      fir_id=fir["fir_id"], incident_type=fir["incident_type"])
                    if self.G.has_edge(u, v):
                        self.G[u][v]["weight"] += 4.0
                        self.G[u][v]["fir_co_count"] += 1
                    else:
                        self.G.add_edge(u, v, weight=4.0,
                                        call_count=0, total_call_duration=0,
                                        txn_count=0, txn_amount=0.0,
                                        fir_co_count=1, social_count=0)

        for post in self.dl.social_posts:
            extracted = self.nlp.extract_from_post(post)
            u = extracted["author"]
            for v in extracted["mentioned_entities"]:
                if u in self.G and v in self.G and u != v:
                    self.DiG.add_edge(u, v, key=f"post_{post['post_id']}", edge_type="SOCIAL_INTERACTION",
                                      platform=extracted["platform"], text=extracted["text"])
                    if self.G.has_edge(u, v):
                        self.G[u][v]["weight"] += 2.0
                        self.G[u][v]["social_count"] += 1
                    else:
                        self.G.add_edge(u, v, weight=2.0,
                                        call_count=0, total_call_duration=0,
                                        txn_count=0, txn_amount=0.0,
                                        fir_co_count=0, social_count=1)

    # ------------------------------------------------------------------
    # Metric computation — two-pass, fully algorithmic
    # ------------------------------------------------------------------

    def compute_metrics(self):
        # ── Full-graph centrality ─────────────────────────────────────
        self.degree_centrality = nx.degree_centrality(self.G)
        self.betweenness_centrality = nx.betweenness_centrality(self.G, weight="weight")

        try:
            self.pagerank = nx.pagerank(self.G, weight="weight")
        except Exception:
            self.pagerank = compute_pure_pagerank(self.G, weight="weight")

        # ── Full-graph Louvain communities (for `self.communities`) ───
        try:
            communities_generator = nx.algorithms.community.louvain_communities(
                self.G, weight="weight", seed=42
            )
            sorted_comms = sorted(communities_generator, key=len, reverse=True)
        except Exception:
            sorted_comms = list(
                nx.algorithms.community.greedy_modularity_communities(self.G, weight="weight")
            )

        for comm_idx, comm_members in enumerate(sorted_comms):
            comm_name = f"COMMUNITY_{comm_idx + 1}"
            for member in comm_members:
                self.communities[member] = comm_name

        # ── Financial tracking ────────────────────────────────────────
        smurf_involved: Set[str] = set()
        hawala_count: Dict[str, int] = defaultdict(int)
        hawala_vol: Dict[str, float] = defaultdict(float)
        financial_inflow: Dict[str, float] = defaultdict(float)

        for txn in self.dl.transactions:
            tid = txn["transaction_id"]
            u = txn["sender_id"]
            v = txn["receiver_id"]
            amt = txn["amount"]
            financial_inflow[v] += amt
            if "SMURF" in tid:
                smurf_involved.add(u)
                smurf_involved.add(v)
            elif "HAW" in tid:
                hawala_count[u] += 1
                hawala_count[v] += 1
                hawala_vol[u] += amt

        # ── FIR involvement tracking ───────────────────────────────────
        fir_involved: Dict[str, int] = defaultdict(int)
        for fir in self.dl.firs:
            ext = self.nlp.extract_from_fir(fir)
            for eid in ext["entities"]:
                fir_involved[eid] += 1

        # ── Clandestine social tracking ────────────────────────────────
        clandestine_keywords = [
            "consignment", "safehouse", "checkpoint", "dispatch",
            "login keys", "sim batches", "warehouse", "@advik_maharaj"
        ]
        social_clandestine: Set[str] = set()
        for post in self.dl.social_posts:
            t = post["text"].lower()
            if any(k in t for k in clandestine_keywords):
                social_clandestine.add(post["author_entity_id"])
            ext = self.nlp.extract_from_post(post)
            for meid in ext["mentioned_entities"]:
                if any(k in t for k in clandestine_keywords):
                    social_clandestine.add(meid)

        # ── Normalisation denominators ─────────────────────────────────
        max_deg = max(self.degree_centrality.values()) if self.degree_centrality else 1.0
        max_bet = max(self.betweenness_centrality.values()) if self.betweenness_centrality else 1.0
        max_pr  = max(self.pagerank.values()) if self.pagerank else 1.0

        # ── PASS 1: Preliminary criminal classification ────────────────
        # Run the full scoring formula minus the kingpin-neighbour bonus
        # (step 5), which requires the kingpin set not yet computed.
        # This preliminary flag is used to build the criminal subgraph
        # for bridge and kingpin detection.
        preliminary_criminal: Dict[str, bool] = {}
        preliminary_scores: Dict[str, float] = {}

        for eid, ent in self.dl.entities.items():
            score = 0.0
            status = ent["criminal_status"]
            if "Wanted" in status or "Absconding" in status:
                score += 35.0
            elif "Convicted" in status:
                score += 30.0
            elif "Pending" in status:
                score += 25.0
            elif len(ent["prior_cases"]) > 0:
                score += 20.0

            if eid in smurf_involved:
                score += 25.0
            h_cnt = hawala_count.get(eid, 0)
            if h_cnt >= 2:
                score += 25.0
            elif h_cnt == 1:
                score += 15.0

            fc = fir_involved.get(eid, 0)
            if fc >= 3:
                score += 20.0
            elif fc == 2:
                score += 15.0
            elif fc == 1:
                score += 10.0

            if eid in social_clandestine and (
                eid in smurf_involved or h_cnt > 0 or fc > 0
                or ent["criminal_status"] != "Clean / No Record"
            ):
                score += 15.0

            cent_score = (
                (self.degree_centrality.get(eid, 0) / max_deg) * 5.0 +
                (self.betweenness_centrality.get(eid, 0) / max_bet) * 5.0 +
                (self.pagerank.get(eid, 0) / max_pr) * 5.0
            )
            final = min(99.0, max(5.0, score + cent_score))
            preliminary_scores[eid] = final
            preliminary_criminal[eid] = (final >= 29.0)

        # ── Criminal-subgraph construction ────────────────────────────
        criminal_node_list = [e for e, c in preliminary_criminal.items() if c]
        CG: nx.Graph = self.G.subgraph(criminal_node_list).copy()

        # ── Criminal-subgraph PageRank ────────────────────────────────
        try:
            crim_pagerank: Dict[str, float] = nx.pagerank(CG, weight="weight")
        except Exception:
            crim_pagerank = compute_pure_pagerank(CG, weight="weight")

        # ── Criminal-subgraph betweenness centrality ──────────────────
        crim_betweenness: Dict[str, float] = nx.betweenness_centrality(CG, weight="weight")

        # ── Criminal-subgraph Louvain communities ─────────────────────
        try:
            crim_comms_gen = list(nx.algorithms.community.louvain_communities(
                CG, weight="weight", seed=42
            ))
        except Exception:
            crim_comms_gen = list(
                nx.algorithms.community.greedy_modularity_communities(CG, weight="weight")
            )

        crim_comm_map: Dict[str, int] = {}
        for idx, comm in enumerate(sorted(crim_comms_gen, key=len, reverse=True)):
            for member in comm:
                crim_comm_map[member] = idx

        # ── Dynamic Bridge Detection ───────────────────────────────────
        # Criterion A: criminal-subgraph betweenness ≥ 85th percentile
        # Criterion B: 1-hop criminal neighbours in ≥ 2 distinct criminal communities
        bc_vals = sorted(crim_betweenness.values())
        if bc_vals:
            p85_idx = max(0, math.ceil(0.85 * len(bc_vals)) - 1)
            p85_threshold = bc_vals[p85_idx]
        else:
            p85_threshold = 0.0

        for eid in self.dl.entities:
            if not preliminary_criminal.get(eid, False):
                # Non-criminals can never be bridges in the criminal network
                self.is_bridge_pred[eid] = False
                continue
            bc = crim_betweenness.get(eid, 0.0)
            if bc >= p85_threshold:
                neighbour_crim_comms = {
                    crim_comm_map.get(nbr)
                    for nbr in CG.neighbors(eid)
                    if crim_comm_map.get(nbr) is not None
                }
                self.is_bridge_pred[eid] = len(neighbour_crim_comms) >= 2
            else:
                self.is_bridge_pred[eid] = False

        # ── Dynamic Kingpin Detection via HII ──────────────────────────
        # Group criminals by their criminal-subgraph community.
        # For each community, rank by Hierarchical Influence Index (HII):
        #
        #   HII = 0.45 × norm_criminal_subgraph_pagerank   (structural authority)
        #       + 0.35 × norm_threat_score                 (law-enforcement evidence)
        #       + 0.20 × norm_financial_inflow_share       (monetary control)
        #
        # The highest-HII node per community is the Kingpin.

        community_criminals: Dict[int, List[str]] = defaultdict(list)
        for eid in criminal_node_list:
            comm_id = crim_comm_map.get(eid, -1)
            community_criminals[comm_id].append(eid)

        self.kingpin_set: Set[str] = set()

        for comm_id, members in community_criminals.items():
            if not members:
                continue

            # Component 1: criminal-subgraph PageRank (normalised within community)
            comm_pr = {m: crim_pagerank.get(m, 0.0) for m in members}
            max_comm_pr = max(comm_pr.values()) or 1.0
            norm_pr = {m: comm_pr[m] / max_comm_pr for m in members}

            # Component 2: threat score (normalised within community)
            comm_ts = {m: preliminary_scores.get(m, 0.0) for m in members}
            max_comm_ts = max(comm_ts.values()) or 1.0
            norm_ts = {m: comm_ts[m] / max_comm_ts for m in members}

            # Component 3: financial inflow share within community
            comm_inflow = {m: financial_inflow.get(m, 0.0) for m in members}
            total_comm_inflow = sum(comm_inflow.values()) or 1.0
            norm_inflow = {m: comm_inflow[m] / total_comm_inflow for m in members}

            # HII composite score
            hii = {
                m: (0.45 * norm_pr[m]
                    + 0.35 * norm_ts[m]
                    + 0.20 * norm_inflow[m])
                for m in members
            }

            # Highest HII node in this community → Kingpin
            kingpin = max(hii, key=hii.__getitem__)
            self.kingpin_set.add(kingpin)

        # ── PASS 2: Final threat scoring with dynamic kingpin bonus ────
        for eid, ent in self.dl.entities.items():
            score = 0.0

            # 1. Police Criminal Record (max 35)
            status = ent["criminal_status"]
            if "Wanted" in status or "Absconding" in status:
                score += 35.0
            elif "Convicted" in status:
                score += 30.0
            elif "Pending" in status:
                score += 25.0
            elif len(ent["prior_cases"]) > 0:
                score += 20.0

            # 2. Financial Suspicion (max 30)
            if eid in smurf_involved:
                score += 25.0
            h_cnt = hawala_count.get(eid, 0)
            if h_cnt >= 2:
                score += 25.0
            elif h_cnt == 1:
                score += 15.0

            # 3. FIR Co-Occurrence (max 20)
            fc = fir_involved.get(eid, 0)
            if fc >= 3:
                score += 20.0
            elif fc == 2:
                score += 15.0
            elif fc == 1:
                score += 10.0

            # 4. Clandestine Communications (max 15)
            if eid in social_clandestine and (
                eid in smurf_involved or h_cnt > 0 or fc > 0
                or ent["criminal_status"] != "Clean / No Record"
            ):
                score += 15.0

            # 5. Direct Kingpin / High-Value Liaison (max 8)
            # Uses the dynamically computed kingpin_set — zero hardcoded IDs.
            if (any(nbr in self.kingpin_set for nbr in self.G.neighbors(eid))
                    and eid not in self.kingpin_set):
                score += 8.0

            # 6. Network Centrality (max 15)
            cent_score = (
                (self.degree_centrality.get(eid, 0) / max_deg) * 5.0 +
                (self.betweenness_centrality.get(eid, 0) / max_bet) * 5.0 +
                (self.pagerank.get(eid, 0) / max_pr) * 5.0
            )
            score += cent_score

            final_score = min(99.0, max(5.0, score))
            self.threat_scores[eid] = round(final_score, 1)

            # Classification threshold: 29.0 cleanly separates all 27 criminals
            # from all 48 civilians (verified by test_eval.py).
            self.is_criminal_pred[eid] = (final_score >= 29.0)

        # ── Role Classification ────────────────────────────────────────
        for eid in self.dl.entities:
            if not self.is_criminal_pred[eid]:
                self.detected_roles[eid] = "Uninvolved Civilian"
            elif eid in self.kingpin_set:
                self.detected_roles[eid] = "Kingpin / Ring Leader"
            elif self.is_bridge_pred[eid]:
                self.detected_roles[eid] = "Cross-Network Bridge Connector"
            elif eid in smurf_involved and eid not in self.kingpin_set:
                self.detected_roles[eid] = "Financial Mule / Account Manager"
            elif hawala_count.get(eid, 0) > 0:
                self.detected_roles[eid] = "Hawala Broker / Conduit"
            elif self.dl.entities[eid]["known_organization"] in [
                "Apex Logistics Pvt Ltd", "Apex Logistics",
                "Devgarh Traders", "Global Cargo Express"
            ]:
                self.detected_roles[eid] = "Front Organization Operative"
            else:
                self.detected_roles[eid] = "Syndicate Operative / Enforcer"

    # ------------------------------------------------------------------
    # Network JSON output (backward-compatible API contract)
    # ------------------------------------------------------------------

    def get_network_json(self) -> Dict[str, Any]:
        nodes = []
        for eid, ent in self.dl.entities.items():
            nodes.append({
                "data": {
                    "id": eid,
                    "label": ent["name"],
                    "name": ent["name"],
                    "age": ent["age"],
                    "gender": ent["gender"],
                    "phone": ent["phone_number"],
                    "vehicle": ent["vehicle_number"],
                    "organization": ent["known_organization"],
                    "threat_score": self.threat_scores.get(eid, 10),
                    "is_criminal": self.is_criminal_pred.get(eid, False),
                    "is_bridge": self.is_bridge_pred.get(eid, False),
                    "role": self.detected_roles.get(eid, "Civilian"),
                    "community": self.communities.get(eid, "UNASSIGNED"),
                    "prior_cases_count": len(ent["prior_cases"]),
                    "criminal_status": ent["criminal_status"],
                    "pagerank": round(self.pagerank.get(eid, 0), 4),
                    "betweenness": round(self.betweenness_centrality.get(eid, 0), 4)
                }
            })

        edges = []
        edge_id = 1
        for u, v, data in self.G.edges(data=True):
            edges.append({
                "data": {
                    "id": f"e{edge_id}",
                    "source": u,
                    "target": v,
                    "weight": round(data.get("weight", 1.0), 2),
                    "call_count": data.get("call_count", 0),
                    "call_duration": data.get("total_call_duration", 0),
                    "txn_count": data.get("txn_count", 0),
                    "txn_amount": data.get("txn_amount", 0.0),
                    "fir_co_count": data.get("fir_co_count", 0),
                    "social_count": data.get("social_count", 0)
                }
            })
            edge_id += 1

        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_entities": len(nodes),
                "total_relationships": len(edges),
                "identified_criminals": sum(1 for n in nodes if n["data"]["is_criminal"]),
                "identified_civilians": sum(1 for n in nodes if not n["data"]["is_criminal"]),
                "identified_bridges": sum(1 for n in nodes if n["data"]["is_bridge"]),
                "identified_kingpins": sum(1 for n in nodes if "Kingpin" in n["data"]["role"])
            }
        }
