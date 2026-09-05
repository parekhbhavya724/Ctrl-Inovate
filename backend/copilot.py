import networkx as nx
from typing import Dict, List, Any

class CaseCopilot:
    def __init__(self, data_loader, graph_engine, pattern_detector):
        self.dl = data_loader
        self.ge = graph_engine
        self.pd = pattern_detector

    def inspect_entity(self, eid: str) -> Dict[str, Any]:
        """Provides 360-degree forensic profile of any entity."""
        if eid not in self.dl.entities:
            return {"error": f"Entity {eid} not found"}

        ent = self.dl.entities[eid]
        threat_score = self.ge.threat_scores.get(eid, 0)
        role = self.ge.detected_roles.get(eid, "Civilian")
        community = self.ge.communities.get(eid, "Unknown")
        
        # Gather CDR contacts
        contacts = []
        for v in self.ge.G.neighbors(eid):
            edge_data = self.ge.G[eid][v]
            if edge_data.get("call_count", 0) > 0:
                contacts.append({
                    "contact_id": v,
                    "contact_name": self.dl.entities.get(v, {}).get("name", v),
                    "call_count": edge_data["call_count"],
                    "total_duration_sec": edge_data["total_call_duration"],
                    "threat_score": self.ge.threat_scores.get(v, 0)
                })
        contacts = sorted(contacts, key=lambda x: x["call_count"], reverse=True)

        # Gather transactions
        sent_txns = [t for t in self.dl.transactions if t["sender_id"] == eid]
        recv_txns = [t for t in self.dl.transactions if t["receiver_id"] == eid]

        # Gather FIR mentions
        firs_mentioned = []
        for fir in self.dl.firs:
            ext = self.ge.nlp.extract_from_fir(fir)
            if eid in ext["entities"]:
                firs_mentioned.append({
                    "fir_id": fir["fir_id"],
                    "date": fir["date"],
                    "incident_type": fir["incident_type"],
                    "police_station": fir["police_station"],
                    "narrative": fir["narrative_text"]
                })

        # Gather Social Posts
        posts = [p for p in self.dl.social_posts if p["author_entity_id"] == eid]

        return {
            "entity_id": eid,
            "profile": ent,
            "threat_score": threat_score,
            "detected_role": role,
            "community": community,
            "is_criminal": self.ge.is_criminal_pred.get(eid, False),
            "is_bridge": self.ge.is_bridge_pred.get(eid, False),
            "centrality_metrics": {
                "pagerank": round(self.ge.pagerank.get(eid, 0), 4),
                "betweenness": round(self.ge.betweenness_centrality.get(eid, 0), 4),
                "degree": round(self.ge.degree_centrality.get(eid, 0), 4)
            },
            "top_contacts": contacts[:10],
            "financial_summary": {
                "total_sent_inr": round(sum(t["amount"] for t in sent_txns), 2),
                "total_received_inr": round(sum(t["amount"] for t in recv_txns), 2),
                "sent_count": len(sent_txns),
                "received_count": len(recv_txns),
                "smurf_involved": any("SMURF" in t["transaction_id"] for t in sent_txns + recv_txns),
                "hawala_involved": any("HAW" in t["transaction_id"] for t in sent_txns + recv_txns)
            },
            "fir_involvements": firs_mentioned,
            "social_posts": posts
        }

    def find_shortest_conspiracy_path(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """Finds shortest communication/conspiracy path between two suspects."""
        if source_id not in self.ge.G or target_id not in self.ge.G:
            return {"error": "Invalid entities"}

        try:
            path = nx.shortest_path(self.ge.G, source=source_id, target=target_id, weight=None)
            path_details = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                data = self.ge.G[u][v]
                path_details.append({
                    "from_id": u,
                    "from_name": self.dl.entities.get(u, {}).get("name", u),
                    "to_id": v,
                    "to_name": self.dl.entities.get(v, {}).get("name", v),
                    "calls": data.get("call_count", 0),
                    "total_duration_sec": data.get("total_call_duration", 0),
                    "transactions_inr": data.get("txn_amount", 0.0),
                    "fir_co_mentions": data.get("fir_co_count", 0)
                })

            return {
                "path": path,
                "hops": len(path) - 1,
                "path_nodes": [
                    {
                        "id": nid,
                        "name": self.dl.entities.get(nid, {}).get("name", nid),
                        "role": self.ge.detected_roles.get(nid, "Civilian"),
                        "threat_score": self.ge.threat_scores.get(nid, 0)
                    }
                    for nid in path
                ],
                "links": path_details
            }
        except nx.NetworkXNoPath:
            return {"error": "No connection found between these two entities in the graph"}

    def query_copilot(self, prompt: str) -> Dict[str, Any]:
        """Processes natural language questions about the crime network."""
        p_lower = prompt.lower()

        # Check for shortest path query
        # e.g., "connect ENT_001 and ENT_023" or "path from Advik Maharaj to Deepa Yadav"
        found_eids = []
        for eid, ent in self.dl.entities.items():
            if eid.lower() in p_lower or ent["name"].lower() in p_lower:
                found_eids.append(eid)

        if len(found_eids) >= 2 and ("path" in p_lower or "connect" in p_lower or "link" in p_lower or "between" in p_lower):
            res = self.find_shortest_conspiracy_path(found_eids[0], found_eids[1])
            u_name = self.dl.entities[found_eids[0]]["name"]
            v_name = self.dl.entities[found_eids[1]]["name"]
            if "hops" in res:
                summary = f"Conspiracy link found between {u_name} and {v_name} across {res['hops']} hop(s):\n"
                for step in res["links"]:
                    summary += f"  • {step['from_name']} ({step['from_id']}) -> {step['to_name']} ({step['to_id']}) via {step['calls']} calls, ₹{step['transactions_inr']:,.2f} transfers, and {step['fir_co_mentions']} shared FIRs.\n"
                return {"response": summary, "structured_data": res}
            else:
                return {"response": f"No direct or indirect graph link found between {u_name} and {v_name}.", "structured_data": res}

        # Check for suspect profile query
        if len(found_eids) == 1:
            eid = found_eids[0]
            profile = self.inspect_entity(eid)
            p = profile["profile"]
            res_text = (
                f"### Investigative Summary: {p['name']} ({eid})\n\n"
                f"* **Threat Score**: {profile['threat_score']}/100 (Status: {profile['detected_role']})\n"
                f"* **Criminal Status**: {p['criminal_status']} ({len(p['prior_cases'])} prior case records)\n"
                f"* **Syndicate Cell**: {profile['community']}\n"
                f"* **Financial Trail**: Total Sent: ₹{profile['financial_summary']['total_sent_inr']:,.2f} | Total Received: ₹{profile['financial_summary']['total_received_inr']:,.2f}\n"
                f"* **Money Laundering Flags**: "
                f"{'⚠️ Smurfing Mule Ring Involved' if profile['financial_summary']['smurf_involved'] else 'No smurfing'}"
                f"{' | ⚠️ Hawala Routing Involved' if profile['financial_summary']['hawala_involved'] else ''}\n"
                f"* **Known Vehicles**: {p['vehicle_number'] or 'None registered'}\n"
                f"* **Known Phone**: {p['phone_number']}\n"
                f"* **Affiliated Front Company**: {p['known_organization'] or 'None recorded'}\n"
                f"* **Shared FIR Cases**: {len(profile['fir_involvements'])} police cases logged\n\n"
                f"**Top Communication Associates**:\n"
            )
            for c in profile["top_contacts"][:5]:
                res_text += f"  • **{c['contact_name']}** ({c['contact_id']}): {c['call_count']} calls ({c['total_duration_sec']}s total) [Threat: {c['threat_score']}]\n"
            return {"response": res_text, "structured_data": profile}

        # Check for kingpin query
        if "kingpin" in p_lower or "leader" in p_lower or "boss" in p_lower:
            kingpins = [eid for eid, r in self.ge.detected_roles.items() if "Kingpin" in r]
            res_text = "### Identified Syndicate Kingpins:\n\n"
            for k in kingpins:
                ent = self.dl.entities[k]
                res_text += (
                    f"👑 **{ent['name']} ({k})**\n"
                    f"  - Role: Kingpin / Syndicate Leader\n"
                    f"  - Threat Score: {self.ge.threat_scores.get(k, 0)}/100\n"
                    f"  - Centrality (PageRank): {self.ge.pagerank.get(k, 0):.4f}\n"
                    f"  - Affiliation: {ent['known_organization'] or 'Underground Network'}\n\n"
                )
            return {"response": res_text, "structured_data": {"kingpins": kingpins}}

        # Check for smurfing query
        if "smurf" in p_lower or "laundering" in p_lower or "mule" in p_lower:
            smurf_alerts = self.pd.detect_smurfing_rings()
            res_text = "### Automated Smurfing Detection Report:\n\n"
            for sa in smurf_alerts:
                res_text += (
                    f"🚨 **Target Beneficiary: {sa['beneficiary_name']} ({sa['beneficiary_id']})**\n"
                    f"  - Total Inflow: ₹{sa['total_laundered_inr']:,.2f} across {sa['transaction_count']} transactions (avg ₹{sa['average_amount_inr']:,.2f})\n"
                    f"  - Active Money Mules: {', '.join([m['name'] for m in sa['mule_senders']])}\n"
                    f"  - Summary: Structured UPI bursts specifically under the ₹50,000 threshold to evade automated AML triggers.\n\n"
                )
            return {"response": res_text, "structured_data": smurf_alerts}

        # General intelligence status
        stats = self.ge.get_network_json()["stats"]
        gen_text = (
            f"### NetSentinel Network Intelligence Status\n\n"
            f"The network contains **{stats['total_entities']} tracked entities** connected by **{stats['total_relationships']} cross-source relationships**.\n\n"
            f"• **Identified Criminal Operatives**: {stats['identified_criminals']} suspects\n"
            f"• **Identified Uninvolved Civilians**: {stats['identified_civilians']} individuals\n"
            f"• **Syndicate Kingpins**: {stats['identified_kingpins']} leaders\n"
            f"• **Cross-Network Bridges**: {stats['identified_bridges']} brokers\n\n"
            f"Try asking:\n"
            f"- *'Tell me about Advik Maharaj'*\n"
            f"- *'Who are the kingpins?'*\n"
            f"- *'Show me smurfing money laundering rings'*\n"
            f"- *'Connect Advik Maharaj and Deepa Yadav'*"
        )
        return {"response": gen_text, "structured_data": stats}

    def generate_dossier_markdown(self, eid: str) -> str:
        """Generates formal prosecution intelligence dossier in Markdown."""
        profile = self.inspect_entity(eid)
        p = profile["profile"]
        
        md = f"""# CONFIDENTIAL // LAW ENFORCEMENT INTELLIGENCE DOSSIER
**SUBJECT: {p['name'].upper()} ({eid})**  
**CLASSIFICATION: {profile['detected_role'].upper()}**  
**SYSTEM RISK THREAT SCORE: {profile['threat_score']}/100**  
**GENERATED ON: 2026-09-05**

---

### 1. IDENTITY & BIOGRAPHICAL DATA
* **Full Name**: {p['name']}
* **Entity ID**: {eid}
* **Age / Gender**: {p['age']} / {p['gender']}
* **Registered Mobile**: {p['phone_number']}
* **Last Known Address**: {p['address_location']}
* **Associated Vehicle Plate**: {p['vehicle_number'] or 'None Registered'}
* **Front / Shell Company**: {p['known_organization'] or 'None Officially Registered'}
* **Syndicate Cluster**: {profile['community']}

---

### 2. CRIMINAL RECORD & POLICE WATCHLIST STATUS
* **Current Legal Status**: {p['criminal_status']}
* **Recorded Prior Cases**: {len(p['prior_cases'])}
"""
        for c in p['prior_cases']:
            md += f"  - **{c['prior_case_id']}**: {c['offense_type']} (Date: {c['date']}, Status: {c['status']})\n"

        md += f"""
---

### 3. FINANCIAL FORENSIC ANALYSIS
* **Total Funds Transferred (Out)**: ₹{profile['financial_summary']['total_sent_inr']:,.2f}
* **Total Funds Received (In)**: ₹{profile['financial_summary']['total_received_inr']:,.2f}
* **Smurfing Activity**: {'FLAGGED (Direct recipient/sender of sub-50k structuring bursts)' if profile['financial_summary']['smurf_involved'] else 'No direct smurfing flagged'}
* **Hawala Activity**: {'FLAGGED (Involved in high-value unregulated cash/crypto transfers)' if profile['financial_summary']['hawala_involved'] else 'No high-value Hawala flagged'}

---

### 4. TOP SURVEILLANCE & COMMUNICATION ASSOCIATES
"""
        for c in profile["top_contacts"]:
            md += f"* **{c['contact_name']} ({c['contact_id']})**: {c['call_count']} calls ({c['total_duration_sec']}s total) | Threat Score: {c['threat_score']}/100\n"

        md += f"""
---

### 5. CO-IMPLICATED POLICE FIRS ({len(profile['fir_involvements'])})
"""
        for f in profile["fir_involvements"]:
            md += f"* **{f['fir_id']}** ({f['police_station']}, {f['date']}): *{f['incident_type']}*\n  _{f['narrative']}_\n\n"

        md += "\n---\n*PRODUCED BY NETSENTINEL CRIMINAL INTELLIGENCE SYSTEM FOR INVESTIGATIVE USE ONLY*"
        return md
