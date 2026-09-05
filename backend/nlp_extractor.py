import re
from typing import Dict, List, Any, Set

class NLPExtractor:
    def __init__(self, entities: Dict[str, Dict[str, Any]]):
        self.entities = entities
        # Build lookup tables for names, vehicles, phones, orgs
        self.name_to_eid = {}
        for eid, ent in self.entities.items():
            name = ent["name"].strip().lower()
            if name:
                self.name_to_eid[name] = eid
                # Also index first and last names if unambiguous
                parts = name.split()
                if len(parts) > 1:
                    # Index full name without titles
                    self.name_to_eid[" ".join(parts)] = eid

        self.phone_to_eid = {}
        for eid, ent in self.entities.items():
            phone = re.sub(r'[^0-9]', '', ent.get("phone_number", ""))
            if phone:
                self.phone_to_eid[phone] = eid
                if len(phone) >= 10:
                    self.phone_to_eid[phone[-10:]] = eid

        self.vehicle_to_eid = {}
        for eid, ent in self.entities.items():
            veh = ent.get("vehicle_number", "").strip().upper()
            if veh:
                self.vehicle_to_eid[veh] = eid

        self.known_orgs = [
            "Apex Logistics Pvt Ltd", "Apex Logistics",
            "Devgarh Traders",
            "Global Cargo Express",
            "BlueSky Exporters",
            "CyberTech Solutions",
            "Golden Crown Holdings",
            "Shiv Shakti Real Estate",
            "Star Line Communications"
        ]

    def extract_from_fir(self, fir: Dict[str, Any]) -> Dict[str, Any]:
        text = fir.get("narrative_text", "")
        fir_id = fir.get("fir_id")
        incident_type = fir.get("incident_type")
        
        found_eids: Set[str] = set()
        found_vehicles: Set[str] = set()
        found_orgs: Set[str] = set()

        # 1. Match names
        lower_text = text.lower()
        for name, eid in self.name_to_eid.items():
            # Check with word boundaries
            pattern = r'\b' + re.escape(name) + r'\b'
            if re.search(pattern, lower_text):
                found_eids.add(eid)

        # 2. Match phones
        phone_matches = re.findall(r'\+91\s?[0-9]{5}\s?[0-9]{5}', text)
        for p in phone_matches:
            digits = re.sub(r'[^0-9]', '', p)
            if digits[-10:] in self.phone_to_eid:
                found_eids.add(self.phone_to_eid[digits[-10:]])

        # 3. Match vehicles (format XX-00-XX-0000)
        veh_matches = re.findall(r'[A-Z]{2}-[0-9]{2}-[A-Z]{2}-[0-9]{4}', text)
        for v in veh_matches:
            found_vehicles.add(v)
            if v in self.vehicle_to_eid:
                found_eids.add(self.vehicle_to_eid[v])

        # 4. Match organizations
        for org in self.known_orgs:
            if org.lower() in lower_text:
                found_orgs.add(org)

        # Generate co-mention pairs
        pairs = []
        eid_list = sorted(list(found_eids))
        for i in range(len(eid_list)):
            for j in range(i + 1, len(eid_list)):
                pairs.append((eid_list[i], eid_list[j]))

        return {
            "fir_id": fir_id,
            "incident_type": incident_type,
            "entities": list(found_eids),
            "vehicles": list(found_vehicles),
            "organizations": list(found_orgs),
            "co_mentions": pairs,
            "date": fir.get("date"),
            "police_station": fir.get("police_station")
        }

    def extract_from_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        text = post.get("text", "")
        author_eid = post.get("author_entity_id")
        platform = post.get("platform")
        
        mentioned_eids: Set[str] = set()
        mentioned_vehicles: Set[str] = set()

        # Check handles like @Advik_Maharaj, @Yashoda_Tak
        handles = re.findall(r'@([A-Za-z0-9_]+)', text)
        for h in handles:
            clean_h = h.replace('_', ' ').lower()
            for name, eid in self.name_to_eid.items():
                if clean_h in name or name in clean_h:
                    mentioned_eids.add(eid)

        # Check raw names in post
        lower_text = text.lower()
        for name, eid in self.name_to_eid.items():
            if eid != author_eid:
                pattern = r'\b' + re.escape(name) + r'\b'
                if re.search(pattern, lower_text):
                    mentioned_eids.add(eid)

        # Vehicles
        veh_matches = re.findall(r'[A-Z]{2}-[0-9]{2}-[A-Z]{2}-[0-9]{4}', text)
        for v in veh_matches:
            mentioned_vehicles.add(v)
            if v in self.vehicle_to_eid:
                mentioned_eids.add(self.vehicle_to_eid[v])

        return {
            "post_id": post.get("post_id"),
            "author": author_eid,
            "platform": platform,
            "mentioned_entities": list(mentioned_eids),
            "vehicles": list(mentioned_vehicles),
            "text": text,
            "timestamp": post.get("timestamp")
        }
