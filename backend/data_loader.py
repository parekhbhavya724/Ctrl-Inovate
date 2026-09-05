import csv
import json
import os
from typing import Dict, List, Any

class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.cdrs: List[Dict[str, Any]] = []
        self.transactions: List[Dict[str, Any]] = []
        self.criminal_records: List[Dict[str, Any]] = []
        self.firs: List[Dict[str, Any]] = []
        self.social_posts: List[Dict[str, Any]] = []
        self.ground_truth: Dict[str, Any] = {}
        
        self.load_all()

    def load_all(self):
        self._load_entities()
        self._load_criminal_records()
        self._load_cdrs()
        self._load_transactions()
        self._load_firs()
        self._load_social_posts()
        self._load_ground_truth()

    def _load_entities(self):
        path = os.path.join(self.data_dir, "entities.csv")
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                eid = row["entity_id"].strip()
                self.entities[eid] = {
                    "entity_id": eid,
                    "name": row.get("name", "").strip(),
                    "age": int(row["age"]) if row.get("age") else None,
                    "gender": row.get("gender", "").strip(),
                    "phone_number": row.get("phone_number", "").strip(),
                    "address_location": row.get("address_location", "").strip(),
                    "vehicle_number": row.get("vehicle_number", "").strip(),
                    "known_organization": row.get("known_organization", "").strip(),
                    "prior_cases": [],
                    "criminal_status": "Clean / No Record"
                }

    def _load_criminal_records(self):
        path = os.path.join(self.data_dir, "criminal_records.csv")
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.criminal_records.append(row)
                eid = row["entity_id"].strip()
                if eid in self.entities:
                    self.entities[eid]["prior_cases"].append({
                        "record_id": row.get("record_id"),
                        "prior_case_id": row.get("prior_case_id"),
                        "offense_type": row.get("offense_type"),
                        "date": row.get("date"),
                        "status": row.get("status")
                    })
                    self.entities[eid]["criminal_status"] = row.get("status")

    def _load_cdrs(self):
        path = os.path.join(self.data_dir, "cdrs.csv")
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["duration_seconds"] = int(row["duration_seconds"]) if row.get("duration_seconds") else 0
                self.cdrs.append(row)

    def _load_transactions(self):
        path = os.path.join(self.data_dir, "transactions.csv")
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["amount"] = float(row["amount"]) if row.get("amount") else 0.0
                self.transactions.append(row)

    def _load_firs(self):
        path = os.path.join(self.data_dir, "firs.csv")
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.firs.append(row)

    def _load_social_posts(self):
        path = os.path.join(self.data_dir, "social_media_posts.csv")
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.social_posts.append(row)

    def _load_ground_truth(self):
        path = os.path.join(self.data_dir, "ground_truth.json")
        if os.path.exists(path):
            with open(path, mode="r", encoding="utf-8") as f:
                self.ground_truth = json.load(f)
                for eid, data in self.ground_truth.items():
                    if eid in self.entities and not data.get("name"):
                        data["name"] = self.entities[eid]["name"]
