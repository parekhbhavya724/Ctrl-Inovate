"""
NetSentinel AI — Case Copilot
==============================
Generative AI investigative assistant powered by Gemini 2.5 Flash with
automatic Graph-RAG function calling.

Architecture
────────────
When GEMINI_API_KEY is set:
  • A Gemini 2.5 Flash agent is initialised with four Graph-RAG tool functions.
  • On each query, Gemini autonomously decides which tools to call, receives
    structured graph evidence, and synthesises an intelligence briefing.
  • The SDK's automatic function calling handles the tool dispatch loop.

When GEMINI_API_KEY is NOT set (or google-genai is unavailable):
  • The original rule-based NLU analysis runs as a graceful fallback.
  • All REST endpoints remain fully functional — zero breaking change.

Graph-RAG Tool Functions (exposed to Gemini)
────────────────────────────────────────────
  inspect_suspect(entity_id)
      Full 360° profile: identity, CDR contacts, financial records, FIRs.

  find_conspiracy_path(source_id, target_id)
      Multi-hop shortest-path traversal between two suspects.

  get_money_laundering_alerts()
      Retrieves all detected smurfing rings and hawala channels.

  query_syndicate_hierarchy(community_name)
      Returns the kingpin, bridges, brokers, and foot soldiers of a syndicate.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

import networkx as nx

logger = logging.getLogger(__name__)

# ── Optional Gemini SDK import ────────────────────────────────────────────────
try:
    from google import genai
    from google.genai import types as genai_types
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False
    logger.warning(
        "google-genai package not installed. "
        "Install with: pip install google-genai   "
        "Copilot will operate in rule-based fallback mode."
    )

GEMINI_MODEL = "gemini-2.5-flash"

_SYSTEM_INSTRUCTION = """You are NetSentinel, an elite AI criminal intelligence analyst embedded within a law-enforcement investigation platform.

Your role is to assist investigators by analysing a live criminal network graph containing entities, call detail records (CDRs), financial transactions, FIR police reports, and social-media intelligence.

Operational rules:
1. Always call the appropriate tool(s) before answering — never fabricate data.
2. Cite specific IDs (entity IDs like ENT_001, transaction IDs, FIR IDs, call IDs) in every response.
3. Structure responses as concise intelligence briefings with clear sections.
4. Flag money laundering, syndicate leadership, cross-network bridges, and clandestine communications.
5. When multiple tools are relevant, call them all to provide a comprehensive briefing.
6. Use ₹ for Indian Rupee amounts.
7. Classify threat levels as CRITICAL (score ≥ 75), HIGH (50-74), MODERATE (29-49), LOW (< 29).
"""


# ─────────────────────────────────────────────────────────────────────────────
# CaseCopilot
# ─────────────────────────────────────────────────────────────────────────────

class CaseCopilot:
    def __init__(self, data_loader, graph_engine, pattern_detector):
        self.dl = data_loader
        self.ge = graph_engine
        self.pd = pattern_detector

        # Gemini client (None when key absent or SDK unavailable)
        self._gemini_client: Optional[Any] = None
        self._gemini_available: bool = False
        self._init_gemini_client()

    # ------------------------------------------------------------------
    # Gemini client initialisation
    # ------------------------------------------------------------------

    def _init_gemini_client(self):
        """Initialise Gemini client if API key is available; else fall back silently."""
        if not _GENAI_AVAILABLE:
            return

        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            logger.info(
                "GEMINI_API_KEY not set — copilot running in rule-based fallback mode."
            )
            return

        try:
            self._gemini_client = genai.Client(api_key=api_key)
            self._gemini_available = True
            logger.info("Gemini 2.5 Flash copilot initialised successfully.")
        except Exception as exc:
            logger.error("Failed to initialise Gemini client: %s", exc)

    # ------------------------------------------------------------------
    # ── Graph-RAG Tool Functions ──────────────────────────────────────
    # These are plain Python functions passed directly to the Gemini SDK.
    # The SDK auto-generates their JSON schema from docstrings + type hints.
    # ------------------------------------------------------------------

    def inspect_suspect(self, entity_id: str) -> str:
        """
        Fetches the full 360-degree forensic profile of a suspect or entity.

        Returns identity details, threat score, detected criminal role, top
        CDR communication contacts, complete financial summary (sent/received
        amounts, smurfing/hawala flags), all FIR police case involvements, and
        the entity's syndicate community assignment.

        Args:
            entity_id: The entity ID to inspect, e.g. 'ENT_001'.

        Returns:
            JSON string containing the full profile.
        """
        profile = self.inspect_entity(entity_id)
        return json.dumps(profile, indent=2, default=str)

    def find_conspiracy_path(self, source_id: str, target_id: str) -> str:
        """
        Finds the shortest multi-hop conspiracy path between two suspects
        in the criminal network graph.

        Traverses all edge types (CDR calls, financial transactions, FIR
        co-occurrences, social media interactions). Returns the path nodes,
        hop count, and per-hop relationship details (call counts, transaction
        amounts, FIR co-mentions).

        Args:
            source_id: Starting entity ID, e.g. 'ENT_001'.
            target_id: Target entity ID, e.g. 'ENT_023'.

        Returns:
            JSON string with the path, hop count, and link-level evidence.
        """
        result = self.find_shortest_conspiracy_path(source_id, target_id)
        return json.dumps(result, indent=2, default=str)

    def get_money_laundering_alerts(self) -> str:
        """
        Retrieves all detected money laundering alerts from the pattern
        detector, including smurfing (structuring) rings and hawala
        high-value unregulated transfer channels.

        Smurfing rings: multiple mules depositing sub-₹50,000 amounts to a
        common beneficiary to evade AML triggers.

        Hawala alerts: high-value (≥ ₹10,00,000) unregulated cash or crypto
        transfers flagged by transaction ID prefix 'HAW'.

        Returns:
            JSON string with smurfing_rings and hawala_transfers arrays.
        """
        alerts = self.pd.get_all_alerts()
        return json.dumps(alerts, indent=2, default=str)

    def query_syndicate_hierarchy(self, community_name: str) -> str:
        """
        Returns the full syndicate hierarchy for a given community or
        criminal network name: its kingpin/ring leader, cross-network
        bridge connectors, financial brokers, and foot soldiers.

        Accepts community names like 'COMMUNITY_1', 'NET_ALPHA', partial
        matches, or the word 'all' to return all syndicates.

        Args:
            community_name: Community identifier or partial name, e.g.
                            'COMMUNITY_1', 'NET_BETA', or 'all'.

        Returns:
            JSON string with the syndicate hierarchy.
        """
        result = self._build_syndicate_hierarchy(community_name)
        return json.dumps(result, indent=2, default=str)

    def _build_syndicate_hierarchy(self, community_name: str) -> Dict[str, Any]:
        """Internal: builds syndicate hierarchy dict for a community."""
        query = community_name.lower().strip()

        # Collect all communities present in the graph
        all_communities: Dict[str, List[str]] = {}
        for eid, comm in self.ge.communities.items():
            all_communities.setdefault(comm, []).append(eid)

        # Determine which communities to include
        if query == "all":
            target_comms = all_communities
        else:
            target_comms = {
                comm: members
                for comm, members in all_communities.items()
                if query in comm.lower()
            }
            if not target_comms:
                # Fuzzy fallback: return all
                target_comms = all_communities

        syndicates = []
        for comm, members in sorted(target_comms.items()):
            criminal_members = [m for m in members if self.ge.is_criminal_pred.get(m, False)]
            if not criminal_members:
                continue

            hierarchy: Dict[str, Any] = {"community": comm, "members": []}
            kingpin = None
            bridges = []
            brokers = []
            foot_soldiers = []

            for eid in criminal_members:
                role = self.ge.detected_roles.get(eid, "")
                ent = self.dl.entities.get(eid, {})
                entry = {
                    "entity_id": eid,
                    "name": ent.get("name", eid),
                    "role": role,
                    "threat_score": self.ge.threat_scores.get(eid, 0),
                    "pagerank": round(self.ge.pagerank.get(eid, 0), 4),
                    "criminal_status": ent.get("criminal_status", "Unknown"),
                    "phone": ent.get("phone_number", ""),
                    "organization": ent.get("known_organization", ""),
                }
                if "Kingpin" in role:
                    kingpin = entry
                elif "Bridge" in role:
                    bridges.append(entry)
                elif "Hawala" in role or "Financial Mule" in role:
                    brokers.append(entry)
                else:
                    foot_soldiers.append(entry)

            hierarchy["kingpin"] = kingpin
            hierarchy["bridges"] = bridges
            hierarchy["brokers"] = brokers
            hierarchy["foot_soldiers"] = foot_soldiers
            hierarchy["total_criminal_members"] = len(criminal_members)
            syndicates.append(hierarchy)

        return {"syndicates": syndicates, "total_syndicates": len(syndicates)}

    # ------------------------------------------------------------------
    # ── Main Copilot Query Endpoint ───────────────────────────────────
    # ------------------------------------------------------------------

    def query_copilot(self, prompt: str) -> Dict[str, Any]:
        """
        Processes a natural language investigative question.
        Routes through Gemini 2.5 Flash (with tool calling) when available;
        falls back to rule-based analysis otherwise.
        """
        if self._gemini_available and self._gemini_client is not None:
            return self._query_gemini(prompt)
        return self._query_rule_based(prompt)

    # ------------------------------------------------------------------
    # Gemini agent (automatic function calling)
    # ------------------------------------------------------------------

    def _query_gemini(self, prompt: str) -> Dict[str, Any]:
        """
        Sends the prompt to Gemini 2.5 Flash with the four Graph-RAG tools.
        The SDK automatically dispatches tool calls and returns the final text.
        """
        tools = [
            self.inspect_suspect,
            self.find_conspiracy_path,
            self.get_money_laundering_alerts,
            self.query_syndicate_hierarchy,
        ]

        try:
            response = self._gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    system_instruction=_SYSTEM_INSTRUCTION,
                    tools=tools,
                    temperature=0.2,         # Low temperature for factual analysis
                    max_output_tokens=8192,
                ),
            )

            # Extract the final text response
            response_text = response.text or ""

            # Collect any tool calls made (for structured_data passthrough)
            tool_calls_made = []
            if hasattr(response, "candidates") and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, "content") and candidate.content:
                        for part in candidate.content.parts:
                            if hasattr(part, "function_call") and part.function_call:
                                tool_calls_made.append({
                                    "tool": part.function_call.name,
                                    "args": dict(part.function_call.args or {})
                                })

            return {
                "response": response_text,
                "mode": "gemini_agent",
                "model": GEMINI_MODEL,
                "tools_called": tool_calls_made,
                "structured_data": None,
            }

        except Exception as exc:
            logger.error("Gemini query failed: %s — falling back to rule-based.", exc)
            result = self._query_rule_based(prompt)
            result["mode"] = "rule_based_fallback"
            result["fallback_reason"] = str(exc)
            return result

    # ------------------------------------------------------------------
    # Rule-based fallback (original NLU logic, fully preserved)
    # ------------------------------------------------------------------

    def _query_rule_based(self, prompt: str) -> Dict[str, Any]:
        """Original rule-based NLU analysis — preserved as graceful fallback."""
        p_lower = prompt.lower()

        # ── Entity mentions ───────────────────────────────────────────
        found_eids = []
        for eid, ent in self.dl.entities.items():
            if eid.lower() in p_lower or ent["name"].lower() in p_lower:
                found_eids.append(eid)

        # ── Multi-entity path query ───────────────────────────────────
        if len(found_eids) >= 2 and any(
            k in p_lower for k in ("path", "connect", "link", "between", "connection")
        ):
            res = self.find_shortest_conspiracy_path(found_eids[0], found_eids[1])
            u_name = self.dl.entities[found_eids[0]]["name"]
            v_name = self.dl.entities[found_eids[1]]["name"]
            if "hops" in res:
                summary = f"Conspiracy link found between **{u_name}** and **{v_name}** across {res['hops']} hop(s):\n"
                for step in res["links"]:
                    summary += (
                        f"  • {step['from_name']} ({step['from_id']}) → "
                        f"{step['to_name']} ({step['to_id']}) via "
                        f"{step['calls']} calls, ₹{step['transactions_inr']:,.2f} transfers, "
                        f"{step['fir_co_mentions']} shared FIRs.\n"
                    )
                return {"response": summary, "mode": "rule_based", "structured_data": res}
            else:
                return {
                    "response": f"No direct or indirect graph link found between {u_name} and {v_name}.",
                    "mode": "rule_based",
                    "structured_data": res,
                }

        # ── Single entity profile query ───────────────────────────────
        if len(found_eids) == 1:
            eid = found_eids[0]
            profile = self.inspect_entity(eid)
            p = profile["profile"]
            res_text = (
                f"### Investigative Summary: {p['name']} ({eid})\n\n"
                f"* **Threat Score**: {profile['threat_score']}/100 — {profile['detected_role']}\n"
                f"* **Criminal Status**: {p['criminal_status']} ({len(p['prior_cases'])} prior cases)\n"
                f"* **Syndicate Cell**: {profile['community']}\n"
                f"* **Financial Trail**: Sent ₹{profile['financial_summary']['total_sent_inr']:,.2f} | "
                f"Received ₹{profile['financial_summary']['total_received_inr']:,.2f}\n"
                f"* **Money Laundering Flags**: "
                f"{'⚠️ Smurfing Involved' if profile['financial_summary']['smurf_involved'] else 'None'}"
                f"{' | ⚠️ Hawala Routing' if profile['financial_summary']['hawala_involved'] else ''}\n"
                f"* **Phone**: {p['phone_number']} | **Vehicle**: {p['vehicle_number'] or 'None'}\n"
                f"* **Front Organisation**: {p['known_organization'] or 'None recorded'}\n"
                f"* **FIR Cases**: {len(profile['fir_involvements'])} police cases logged\n\n"
                "**Top Communication Associates:**\n"
            )
            for c in profile["top_contacts"][:5]:
                res_text += (
                    f"  • **{c['contact_name']}** ({c['contact_id']}): "
                    f"{c['call_count']} calls ({c['total_duration_sec']}s) "
                    f"[Threat: {c['threat_score']}]\n"
                )
            return {"response": res_text, "mode": "rule_based", "structured_data": profile}

        # ── Kingpin query ─────────────────────────────────────────────
        if any(k in p_lower for k in ("kingpin", "leader", "boss", "ringleader")):
            kingpins = [eid for eid, r in self.ge.detected_roles.items() if "Kingpin" in r]
            res_text = "### Identified Syndicate Kingpins:\n\n"
            for k in kingpins:
                ent = self.dl.entities[k]
                res_text += (
                    f"👑 **{ent['name']} ({k})**\n"
                    f"  - Threat Score: {self.ge.threat_scores.get(k, 0)}/100\n"
                    f"  - Centrality (PageRank): {self.ge.pagerank.get(k, 0):.4f}\n"
                    f"  - Community: {self.ge.communities.get(k)}\n"
                    f"  - Affiliation: {ent['known_organization'] or 'Underground Network'}\n\n"
                )
            return {"response": res_text, "mode": "rule_based", "structured_data": {"kingpins": kingpins}}

        # ── Syndicate / community query ───────────────────────────────
        if any(k in p_lower for k in ("syndicate", "community", "hierarchy", "network")):
            hierarchy = self._build_syndicate_hierarchy("all")
            res_text = "### Criminal Syndicate Hierarchy:\n\n"
            for syn in hierarchy["syndicates"]:
                kp = syn["kingpin"]
                kp_str = f"{kp['name']} ({kp['entity_id']})" if kp else "Not identified"
                bridge_names = ", ".join(f"{b['name']} ({b['entity_id']})" for b in syn["bridges"]) or "None"
                res_text += (
                    f"**{syn['community']}** — {syn['total_criminal_members']} criminal members\n"
                    f"  👑 Kingpin: {kp_str}\n"
                    f"  🔗 Bridges: {bridge_names}\n\n"
                )
            return {"response": res_text, "mode": "rule_based", "structured_data": hierarchy}

        # ── Smurfing / money laundering query ────────────────────────
        if any(k in p_lower for k in ("smurf", "laundering", "mule", "hawala", "money")):
            smurf_alerts = self.pd.detect_smurfing_rings()
            res_text = "### Automated Smurfing Detection Report:\n\n"
            for sa in smurf_alerts:
                mule_names = ", ".join(m["name"] for m in sa["mule_senders"])
                res_text += (
                    f"🚨 **Target: {sa['beneficiary_name']} ({sa['beneficiary_id']})**\n"
                    f"  - Total Inflow: ₹{sa['total_laundered_inr']:,.2f} across "
                    f"{sa['transaction_count']} transactions\n"
                    f"  - Active Mules: {mule_names}\n"
                    f"  - Pattern: Structured UPI bursts under ₹50,000 AML threshold.\n\n"
                )
            return {"response": res_text, "mode": "rule_based", "structured_data": smurf_alerts}

        # ── Bridge / conduit query ────────────────────────────────────
        if any(k in p_lower for k in ("bridge", "conduit", "connector", "cross-network")):
            bridges = [eid for eid, b in self.ge.is_bridge_pred.items() if b]
            res_text = "### Cross-Network Bridge Connectors:\n\n"
            for b in bridges:
                ent = self.dl.entities[b]
                comms = list({self.ge.communities.get(n) for n in self.ge.G.neighbors(b) if self.ge.communities.get(n)})
                res_text += (
                    f"🔗 **{ent['name']} ({b})**\n"
                    f"  - Threat Score: {self.ge.threat_scores.get(b, 0)}/100\n"
                    f"  - Betweenness: {self.ge.betweenness_centrality.get(b, 0):.4f}\n"
                    f"  - Bridges communities: {', '.join(comms[:4])}\n\n"
                )
            return {"response": res_text, "mode": "rule_based", "structured_data": {"bridges": bridges}}

        # ── General status overview ───────────────────────────────────
        stats = self.ge.get_network_json()["stats"]
        gen_text = (
            f"### NetSentinel Network Intelligence Status\n\n"
            f"The network contains **{stats['total_entities']} tracked entities** "
            f"connected by **{stats['total_relationships']} cross-source relationships**.\n\n"
            f"• **Identified Criminal Operatives**: {stats['identified_criminals']} suspects\n"
            f"• **Identified Uninvolved Civilians**: {stats['identified_civilians']} individuals\n"
            f"• **Syndicate Kingpins**: {stats['identified_kingpins']} leaders\n"
            f"• **Cross-Network Bridges**: {stats['identified_bridges']} brokers\n\n"
            "**Try asking:**\n"
            "- *'Tell me about Advik Maharaj'*\n"
            "- *'Who are the kingpins?'*\n"
            "- *'Show me smurfing money laundering rings'*\n"
            "- *'Find connection between Advik Maharaj and Deepa Yadav'*\n"
            "- *'Summarise the NET_BETA syndicate hierarchy'*"
        )
        return {"response": gen_text, "mode": "rule_based", "structured_data": stats}

    # ------------------------------------------------------------------
    # ── Core analytical methods (used by tools + REST endpoints) ──────
    # ------------------------------------------------------------------

    def inspect_entity(self, eid: str) -> Dict[str, Any]:
        """Provides 360-degree forensic profile of any entity."""
        if eid not in self.dl.entities:
            return {"error": f"Entity {eid} not found"}

        ent = self.dl.entities[eid]
        threat_score = self.ge.threat_scores.get(eid, 0)
        role = self.ge.detected_roles.get(eid, "Civilian")
        community = self.ge.communities.get(eid, "Unknown")

        # CDR contacts
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

        # Transactions
        sent_txns = [t for t in self.dl.transactions if t["sender_id"] == eid]
        recv_txns = [t for t in self.dl.transactions if t["receiver_id"] == eid]

        # FIR mentions
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

        # Social posts
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

    def get_entity_raw_records(self, eid: str) -> Dict[str, Any]:
        """Returns raw individual records (calls, transactions, FIRs) for an entity."""
        target_eid = eid
        if target_eid not in self.dl.entities and target_eid.upper() in self.dl.entities:
            target_eid = target_eid.upper()

        if target_eid not in self.dl.entities:
            return {"error": f"Entity {eid} not found"}

        ent = self.dl.entities[target_eid]
        ent_name = ent.get("name", "")

        calls = []
        for c in self.dl.cdrs:
            caller = str(c.get("caller_id", "")).strip()
            callee = str(c.get("callee_id", "")).strip()
            if caller == target_eid or callee == target_eid:
                is_caller = (caller == target_eid)
                other_id = callee if is_caller else caller
                other_name = self.dl.entities.get(other_id, {}).get("name", other_id)
                dur = c.get("duration_seconds", 0)
                calls.append({
                    "call_id": c.get("call_id"),
                    "other_party": other_name,
                    "other_party_id": other_id,
                    "other_party_name": other_name,
                    "timestamp": c.get("timestamp"),
                    "duration": dur,
                    "duration_seconds": dur,
                    "caller_id": caller,
                    "callee_id": callee,
                    "role": "caller" if is_caller else "receiver",
                    "direction": "outgoing" if is_caller else "incoming",
                    "cell_tower_location": c.get("cell_tower_location", "")
                })

        transactions = []
        for t in self.dl.transactions:
            sender = str(t.get("sender_id", "")).strip()
            receiver = str(t.get("receiver_id", "")).strip()
            if sender == target_eid or receiver == target_eid:
                is_sender = (sender == target_eid)
                other_id = receiver if is_sender else sender
                other_name = self.dl.entities.get(other_id, {}).get("name", other_id)
                amt = t.get("amount", 0.0)
                timestamp = t.get("timestamp")
                transactions.append({
                    "transaction_id": t.get("transaction_id"),
                    "other_party": other_name,
                    "other_party_id": other_id,
                    "other_party_name": other_name,
                    "amount": amt,
                    "date": timestamp,
                    "timestamp": timestamp,
                    "sender_id": sender,
                    "receiver_id": receiver,
                    "role": "sender" if is_sender else "receiver",
                    "direction": "outgoing" if is_sender else "incoming",
                    "transaction_type": t.get("transaction_type", ""),
                    "location": t.get("location", "")
                })

        firs = []
        for fir in self.dl.firs:
            ext = self.ge.nlp.extract_from_fir(fir)
            narrative = fir.get("narrative_text", "")
            if (target_eid in ext["entities"]
                    or target_eid.lower() in narrative.lower()
                    or (ent_name and ent_name.lower() in narrative.lower())):
                co_entities = [
                    {
                        "entity_id": oid,
                        "name": self.dl.entities.get(oid, {}).get("name", oid)
                    }
                    for oid in ext["entities"] if oid != target_eid
                ]
                firs.append({
                    "fir_id": fir.get("fir_id"),
                    "narrative_excerpt": narrative,
                    "narrative": narrative,
                    "narrative_text": narrative,
                    "date": fir.get("date"),
                    "police_station": fir.get("police_station"),
                    "incident_type": fir.get("incident_type"),
                    "co_occurring_entities": co_entities
                })

        return {
            "entity_id": target_eid,
            "calls": calls,
            "transactions": transactions,
            "firs": firs
        }

    def find_shortest_conspiracy_path(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """Finds shortest communication/conspiracy path between two suspects."""
        if source_id not in self.ge.G or target_id not in self.ge.G:
            return {"error": "Invalid entities"}

        try:
            path = nx.shortest_path(self.ge.G, source=source_id, target=target_id, weight=None)
            path_details = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
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

    def generate_dossier_markdown(self, eid: str) -> str:
        """Generates formal prosecution intelligence dossier in Markdown."""
        profile = self.inspect_entity(eid)
        p = profile["profile"]

        md = f"""# CONFIDENTIAL // LAW ENFORCEMENT INTELLIGENCE DOSSIER
**SUBJECT: {p['name'].upper()} ({eid})**  
**CLASSIFICATION: {profile['detected_role'].upper()}**  
**SYSTEM RISK THREAT SCORE: {profile['threat_score']}/100**  
**GENERATED ON: 2026-09-06**

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
