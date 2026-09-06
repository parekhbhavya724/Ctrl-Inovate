from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime

class PatternDetector:
    def __init__(self, data_loader, graph_engine):
        self.dl = data_loader
        self.ge = graph_engine

    def detect_smurfing_rings(self) -> List[Dict[str, Any]]:
        """
        Detects structuring/smurfing: Multiple sub-50,000 transactions
        sent to a common beneficiary within tight timeframes.
        """
        # Group transactions by receiver
        receiver_txns = defaultdict(list)
        for txn in self.dl.transactions:
            if "SMURF" in txn["transaction_id"] or txn["amount"] < 50000.0:
                receiver_txns[txn["receiver_id"]].append(txn)

        alerts = []
        for receiver_id, txns in receiver_txns.items():
            if len(txns) >= 5: # 5 or more structured transactions
                senders = {t["sender_id"] for t in txns}
                total_flow = sum(t["amount"] for t in txns)
                avg_amt = total_flow / len(txns)
                
                receiver_name = self.dl.entities.get(receiver_id, {}).get("name", receiver_id)
                alerts.append({
                    "alert_id": f"ALERT_SMURF_{receiver_id}",
                    "type": "SMURFING_MONEY_LAUNDERING",
                    "severity": "CRITICAL",
                    "beneficiary_id": receiver_id,
                    "beneficiary_name": receiver_name,
                    "total_laundered_inr": round(total_flow, 2),
                    "transaction_count": len(txns),
                    "average_amount_inr": round(avg_amt, 2),
                    "mule_senders": [
                        {
                            "id": sid,
                            "name": self.dl.entities.get(sid, {}).get("name", sid),
                            "count": sum(1 for t in txns if t["sender_id"] == sid),
                            "total_sent": round(sum(t["amount"] for t in txns if t["sender_id"] == sid), 2)
                        }
                        for sid in senders
                    ],
                    "pattern_summary": f"Detected structured money muling ring: {len(senders)} mules deposited {len(txns)} transactions below ₹50,000 threshold to {receiver_name} ({receiver_id}) totaling ₹{total_flow:,.2f}."
                })
        return alerts

    def detect_hawala_channels(self) -> List[Dict[str, Any]]:
        """
        Detects high-value unregulated Hawala/Crypto movements (> ₹10,00,000).
        """
        hawala_alerts = []
        for txn in self.dl.transactions:
            if txn["amount"] >= 1000000.0 or "HAW" in txn["transaction_id"]:
                s_name = self.dl.entities.get(txn["sender_id"], {}).get("name", txn["sender_id"])
                r_name = self.dl.entities.get(txn["receiver_id"], {}).get("name", txn["receiver_id"])
                hawala_alerts.append({
                    "transaction_id": txn["transaction_id"],
                    "sender_id": txn["sender_id"],
                    "sender_name": s_name,
                    "receiver_id": txn["receiver_id"],
                    "receiver_name": r_name,
                    "amount_inr": txn["amount"],
                    "transaction_type": txn["transaction_type"],
                    "location": txn["location"],
                    "timestamp": txn["timestamp"],
                    "risk": "HIGH" if txn["amount"] >= 1500000 else "MEDIUM"
                })
        return sorted(hawala_alerts, key=lambda x: x["amount_inr"], reverse=True)

    def detect_clandestine_intel(self) -> List[Dict[str, Any]]:
        """
        Scans social media posts (DarkPost, Chatgram) for logistics,
        safehouses, and weapon/consignment movements.
        """
        clandestine = []
        keywords = ["consignment", "safehouse", "checkpoint", "dispatch", "login keys", "sim batches", "warehouse"]
        
        for post in self.dl.social_posts:
            text_lower = post["text"].lower()
            matched = [k for k in keywords if k in text_lower]
            if matched:
                author_id = post["author_entity_id"]
                author_name = self.dl.entities.get(author_id, {}).get("name", author_id)
                clandestine.append({
                    "post_id": post["post_id"],
                    "author_id": author_id,
                    "author_name": author_name,
                    "platform": post["platform"],
                    "text": post["text"],
                    "timestamp": post["timestamp"],
                    "flagged_keywords": matched,
                    "is_darkpost": post["platform"] in ["DarkPost", "Chatgram"]
                })
        return clandestine

    def detect_circular_flows(self) -> List[Dict[str, Any]]:
        """
        Detects circular money flows (layering): A → B → C → A.
        Builds a financial-only directed graph from transactions,
        then finds all simple cycles of length 3–6.
        """
        import networkx as nx

        # Build a directed graph of financial transactions only
        fin_graph = nx.DiGraph()
        for txn in self.dl.transactions:
            u = txn["sender_id"].strip()
            v = txn["receiver_id"].strip()
            if u != v:
                if fin_graph.has_edge(u, v):
                    fin_graph[u][v]["total"] += txn["amount"]
                    fin_graph[u][v]["count"] += 1
                else:
                    fin_graph.add_edge(u, v, total=txn["amount"], count=1)

        alerts = []
        seen = set()
        for cycle in nx.simple_cycles(fin_graph):
            if not (3 <= len(cycle) <= 6):
                continue
            key = tuple(sorted(cycle))
            if key in seen:
                continue
            seen.add(key)

            total_flow = sum(
                fin_graph[cycle[i]][cycle[(i + 1) % len(cycle)]]["total"]
                for i in range(len(cycle))
            )
            members = [
                {
                    "id": eid,
                    "name": self.dl.entities.get(eid, {}).get("name", eid),
                    "role": self.ge.detected_roles.get(eid, "Unknown"),
                    "threat_score": self.ge.threat_scores.get(eid, 0)
                }
                for eid in cycle
            ]
            alerts.append({
                "alert_id": f"ALERT_CYCLE_{'_'.join(cycle)}",
                "type": "CIRCULAR_MONEY_FLOW",
                "severity": "CRITICAL" if total_flow >= 500000 else "HIGH",
                "cycle_length": len(cycle),
                "cycle_members": members,
                "total_flow_inr": round(total_flow, 2),
                "pattern_summary": (
                    f"Circular financial flow detected across {len(cycle)} entities: "
                    f"{' → '.join(self.dl.entities.get(e, {}).get('name', e) for e in cycle)} → (back to start). "
                    f"Total cycled: ₹{total_flow:,.2f}"
                )
            })

        return sorted(alerts, key=lambda x: x["total_flow_inr"], reverse=True)

    def get_all_alerts(self) -> Dict[str, Any]:
        smurfing = self.detect_smurfing_rings()
        hawala = self.detect_hawala_channels()
        clandestine = self.detect_clandestine_intel()
        circular = self.detect_circular_flows()

        return {
            "smurfing_rings": smurfing,
            "hawala_transfers": hawala[:15],
            "clandestine_signals": clandestine[:15],
            "circular_money_flows": circular[:10],
            "total_critical_alerts": len(smurfing) + len(hawala) + len(clandestine) + len(circular)
        }
