"""
SIH26189 - AI-Powered Criminal Network Analysis System
Synthetic Dataset Generator Script
Sponsoring Organization: Ministry of Home Affairs / NCRB

This script generates a multi-source synthetic dataset simulating investigative law enforcement data:
1. data/entities_master.csv
2. data/ground_truth_networks.json
3. data/firs_reports.csv
4. data/call_detail_records.csv
5. data/financial_transactions.csv
6. data/social_media_intel.csv
7. data/criminal_history_db.csv
"""

import os
import json
import random
import datetime
import pandas as pd
import numpy as np
from faker import Faker

# Fixed seed for perfect reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

fake = Faker('en_IN')
Faker.seed(RANDOM_SEED)

# Output directory setup
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------
# 1. GENERATE ENTITIES & HIDDEN NETWORKS
# ---------------------------------------------------------
NUM_ENTITIES = 75

# Fictional Towns / Cities for Indian context
TOWNS = [
    "Devgarh", "Anandpur", "Cyberabad", "Ratanpur", "Kalyanpur",
    "Vidyanagar", "Shivnagar", "Chandanpur", "Suryanagar", "Navgram",
    "Indrapuri", "Rajnagar", "Gopalpur", "Mayapur", "Vikramnagar"
]

VEHICLE_PREFIXES = ["MH-12", "DL-08", "KA-03", "UP-32", "TS-09", "HR-26", "RJ-14", "WB-02"]
ORGANIZATIONS = [
    "Apex Logistics Pvt Ltd", "Devgarh Traders", "BlueSky Exporters",
    "Golden Crown Holdings", "CyberTech Solutions", "Global Cargo Express",
    "Shiv Shakti Real Estate", "Star Line Communications"
]

# Define 4 Criminal Networks with specific roles
NETWORKS_DEF = {
    "NET_ALPHA": {
        "name": "Syndicate Alpha (Hawala & Crypto Money Laundering)",
        "members": ["ENT_001", "ENT_002", "ENT_003", "ENT_004", "ENT_005", "ENT_006", "ENT_007", "ENT_008"],
        "roles": {
            "ENT_001": "Kingpin / Ring Leader",
            "ENT_002": "Key Lieutenant",
            "ENT_003": "Hawala Broker",
            "ENT_004": "Financial Mule",
            "ENT_005": "Financial Mule",
            "ENT_006": "Shell Company Director",
            "ENT_007": "Bridge Connector (Hawala Conduit)",
            "ENT_008": "Operative"
        }
    },
    "NET_BETA": {
        "name": "Syndicate Beta (Narcotics & Contraband Smuggling)",
        "members": ["ENT_007", "ENT_009", "ENT_010", "ENT_011", "ENT_012", "ENT_013", "ENT_014", "ENT_015"],
        "roles": {
            "ENT_009": "Kingpin / Cartel Boss",
            "ENT_010": "Logistics Coordinator",
            "ENT_011": "Warehouse Manager",
            "ENT_012": "Enforcer",
            "ENT_013": "Couriers/Distributor",
            "ENT_014": "Couriers/Distributor",
            "ENT_007": "Bridge Connector (Money Handler)",
            "ENT_015": "Bridge Connector (Identity Supplier)"
        }
    },
    "NET_GAMMA": {
        "name": "Syndicate Gamma (Cyber Fraud & Phishing Ring)",
        "members": ["ENT_015", "ENT_016", "ENT_017", "ENT_018", "ENT_019", "ENT_020", "ENT_021", "ENT_022"],
        "roles": {
            "ENT_016": "Kingpin / Tech Lead",
            "ENT_017": "Phishing Kit Operator",
            "ENT_018": "Call Center Handler",
            "ENT_019": "SIM Card Extractor",
            "ENT_020": "Mule Account Manager",
            "ENT_021": "Cash Out Mule",
            "ENT_015": "Bridge Connector (Data Broker)",
            "ENT_022": "Bridge Connector (Extortion Financier)"
        }
    },
    "NET_DELTA": {
        "name": "Syndicate Delta (Illegal Firearms & Extortion Gang)",
        "members": ["ENT_022", "ENT_023", "ENT_024", "ENT_025", "ENT_026", "ENT_027"],
        "roles": {
            "ENT_023": "Gang Leader / Arms Supplier",
            "ENT_024": "Extortion Specialist",
            "ENT_025": "Shooter / Enforcer",
            "ENT_026": "Arms Courier",
            "ENT_027": "Hideout Caretaker",
            "ENT_022": "Bridge Connector (Financier)"
        }
    }
}

# Collect all criminal entity IDs
criminal_ids = set()
for net_info in NETWORKS_DEF.values():
    criminal_ids.update(net_info["members"])

# Generate Entities Master
entities = []
ground_truth = {}

for i in range(1, NUM_ENTITIES + 1):
    entity_id = f"ENT_{i:03d}"
    
    # Generate realistic Indian name
    gender = random.choice(["Male", "Female"])
    name = fake.name_male() if gender == "Male" else fake.name_female()
    age = random.randint(22, 65)
    
    # Phone format: +91 98xxx xxxxx or +91 97xxx xxxxx
    phone_prefix = random.choice(["98", "97", "99", "96", "95", "91", "88", "70"])
    phone_number = f"+91 {phone_prefix}{random.randint(100, 999)} {random.randint(10000, 99999)}"
    
    city = random.choice(TOWNS)
    address = f"{random.randint(1, 150)}, {fake.street_name()}, {city}"
    
    # Optional vehicle & company
    has_vehicle = random.random() > 0.35
    vehicle_number = f"{random.choice(VEHICLE_PREFIXES)}-{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}-{random.randint(1000, 9999)}" if has_vehicle else ""
    
    has_org = random.random() > 0.60
    organization = random.choice(ORGANIZATIONS) if has_org else ""
    
    # Check network membership
    member_of_nets = []
    roles_in_nets = {}
    for net_key, net_val in NETWORKS_DEF.items():
        if entity_id in net_val["members"]:
            member_of_nets.append(net_key)
            roles_in_nets[net_key] = net_val["roles"].get(entity_id, "Operative")
            
    is_criminal = len(member_of_nets) > 0
    is_bridge = len(member_of_nets) > 1
    
    primary_role = "Uninvolved Civilian"
    if is_bridge:
        primary_role = "Cross-Network Bridge Connector"
    elif is_criminal:
        primary_role = roles_in_nets[member_of_nets[0]]

    entities.append({
        "entity_id": entity_id,
        "name": name,
        "age": age,
        "gender": gender,
        "phone_number": phone_number,
        "address_location": address,
        "vehicle_number": vehicle_number,
        "known_organization": organization
    })
    
    ground_truth[entity_id] = {
        "name": name,
        "is_criminal": is_criminal,
        "is_bridge": is_bridge,
        "networks": member_of_nets,
        "primary_role": primary_role,
        "network_roles": roles_in_nets
    }

df_entities = pd.DataFrame(entities)
df_entities.to_csv(os.path.join(OUTPUT_DIR, "entities_master.csv"), index=False)

with open(os.path.join(OUTPUT_DIR, "ground_truth_networks.json"), "w") as f:
    json.dump(ground_truth, f, indent=2)

print(f"[+] Master Entities generated: {len(df_entities)} records.")
print(f"[+] Ground Truth Networks saved with {len(criminal_ids)} criminal entities across 4 networks.")


# ---------------------------------------------------------
# 2. GENERATE FIR REPORTS (Unstructured Text Narratives)
# ---------------------------------------------------------
NUM_FIRS = 50

POLICE_STATIONS = [
    "Cyber Crime PS, Cyberabad", "Devgarh Central PS", "Ratanpur Crime Branch",
    "Anandpur Sector-4 PS", "Kalyanpur Anti-Narcotics Cell", "Special Task Force HQ, Indrapuri",
    "Suryanagar Crime Investigation Unit", "Vidyanagar North PS"
]

INCIDENT_TYPES = [
    "Cyber Fraud & Phishing", "Hawala Money Laundering", "Narcotics Smuggling",
    "Extortion & Threats", "Illegal Firearms Possession", "Vehicle Theft & Smuggling",
    "Organized Retail Fraud", "Identity Theft & Fake SIMs"
]

fir_entries = []
start_date = datetime.date(2026, 1, 1)

# Pre-select pairs of suspects for narrative coherence
fir_templates = [
    "On {date}, complainant reported a financial fraud incident at {ps}. Investigation revealed that suspect {name1} (Phone: {phone1}) operating from {loc} facilitated illegal wire transfers. Suspect was spotted driving vehicle {veh1} along with associate {name2} (Phone: {phone2}). Further intelligence links them to {org}.",
    "Police raid conducted near {loc} under {ps} jurisdiction following an anonymous tip. Officers intercepted vehicle {veh1} driven by {name1}. Search yielded suspicious contraband and documents belonging to {org}. Phone records show frequent contact between {name1} ({phone1}) and {name2} ({phone2}) prior to the trip.",
    "A formal FIR was registered regarding extortion calls received by local businessmen in {loc}. The caller identified himself under an alias connected to {name1}. Intercept analysis identified accomplice {name2} using vehicle {veh2} to collect cash packages. Bank statements reveal funds routed to {org}.",
    "Investigative audit by {ps} exposed a cyber phishing syndicate operating in {loc}. Key operative {name1} (Phone: {phone1}) acquired fraudulent SIM cards with assistance from {name2}. Money trail traced multiple UPI transactions to account registered under {org}.",
    "Special task force operation at {loc} seized unauthorized firearms and ammunition. Suspect {name1} was detained at the scene. Interrogation transcript indicates firearms were supplied by {name2} (Phone: {phone2}) using transport registered under vehicle {veh1}.",
    "Surveillance unit at {ps} logged suspicious meeting at {loc} involving known subject {name1} and associate {name2}. Vehicle {veh1} was parked nearby. Intelligence report indicates discussion centered on money laundering operations via {org}."
]

for i in range(1, NUM_FIRS + 1):
    fir_id = f"FIR_2026_{i:03d}"
    incident_date = start_date + datetime.timedelta(days=random.randint(0, 220))
    ps = random.choice(POLICE_STATIONS)
    inc_type = random.choice(INCIDENT_TYPES)
    
    # 70% chance to involve criminal network entities
    if random.random() < 0.70:
        suspect1 = df_entities[df_entities["entity_id"].isin(criminal_ids)].sample(1).iloc[0]
        suspect2 = df_entities[df_entities["entity_id"].isin(criminal_ids)].sample(1).iloc[0]
    else:
        suspect1 = df_entities.sample(1).iloc[0]
        suspect2 = df_entities.sample(1).iloc[0]
        
    template = random.choice(fir_templates)
    loc = suspect1["address_location"].split(", ")[-1]
    veh1 = suspect1["vehicle_number"] if suspect1["vehicle_number"] else "MH-12-XX-9999"
    veh2 = suspect2["vehicle_number"] if suspect2["vehicle_number"] else "DL-08-YY-8888"
    org = suspect1["known_organization"] if suspect1["known_organization"] else "Apex Logistics"
    
    narrative = template.format(
        date=incident_date.strftime("%d-%b-%Y"),
        ps=ps,
        name1=suspect1["name"],
        phone1=suspect1["phone_number"],
        loc=loc,
        veh1=veh1,
        name2=suspect2["name"],
        phone2=suspect2["phone_number"],
        veh2=veh2,
        org=org
    )
    
    fir_entries.append({
        "fir_id": fir_id,
        "date": incident_date.strftime("%Y-%m-%d"),
        "police_station": ps,
        "incident_type": inc_type,
        "narrative_text": narrative
    })

df_firs = pd.DataFrame(fir_entries)
df_firs.to_csv(os.path.join(OUTPUT_DIR, "firs_reports.csv"), index=False)
print(f"[+] FIR Reports generated: {len(df_firs)} records.")


# ---------------------------------------------------------
# 3. GENERATE CALL DETAIL RECORDS (CDRs)
# ---------------------------------------------------------
NUM_CDRS = 450
TOWERS = [
    "TOWER_DEVGARH_CENTRAL", "TOWER_ANANDPUR_NORTH", "TOWER_CYBERABAD_HUB",
    "TOWER_RATANPUR_HIGHWAY", "TOWER_KALYANPUR_EAST", "TOWER_INDRAPURI_STATION"
]

cdr_entries = []
base_time = datetime.datetime(2026, 5, 1, 8, 0, 0)

for i in range(1, NUM_CDRS + 1):
    call_time = base_time + datetime.timedelta(minutes=random.randint(1, 150000))
    duration = random.randint(15, 1400)
    tower = random.choice(TOWERS)
    
    roll = random.random()
    if roll < 0.65:
        # Intra-network call (High frequency between same network members)
        net_choice = random.choice(list(NETWORKS_DEF.keys()))
        members = NETWORKS_DEF[net_choice]["members"]
        caller_id, callee_id = random.sample(members, 2)
    elif roll < 0.85:
        # Cross-network / Bridge call (Involves bridge entity ENT_007, ENT_015, or ENT_022)
        bridge_id = random.choice(["ENT_007", "ENT_015", "ENT_022"])
        other_id = random.choice(list(criminal_ids - {bridge_id}))
        caller_id, callee_id = (bridge_id, other_id) if random.random() > 0.5 else (other_id, bridge_id)
    else:
        # Random noise call between any entities
        caller_id, callee_id = random.sample(list(df_entities["entity_id"]), 2)
        
    cdr_entries.append({
        "call_id": f"CDR_{i:04d}",
        "caller_id": caller_id,
        "callee_id": callee_id,
        "timestamp": call_time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds": duration,
        "cell_tower_location": tower
    })

df_cdrs = pd.DataFrame(cdr_entries)
df_cdrs.to_csv(os.path.join(OUTPUT_DIR, "call_detail_records.csv"), index=False)
print(f"[+] Call Detail Records (CDRs) generated: {len(df_cdrs)} records.")


# ---------------------------------------------------------
# 4. GENERATE FINANCIAL TRANSACTIONS
# ---------------------------------------------------------
NUM_TXNS = 220
TXN_TYPES = ["UPI", "Cash Deposit", "RTGS/NEFT", "Crypto Transfer", "IMPS Wire"]

txn_entries = []
txn_time = datetime.datetime(2026, 3, 1, 10, 0, 0)

# A. Structuring Pattern (Smurfing): Multiple transactions under ₹50,000 to avoid alerts
smurf_mules = ["ENT_004", "ENT_005", "ENT_020", "ENT_021"]
kingpins = ["ENT_001", "ENT_016"]

for j in range(12):
    mule = random.choice(smurf_mules)
    boss = random.choice(kingpins)
    base_burst_time = txn_time + datetime.timedelta(days=random.randint(1, 100))
    for k in range(random.randint(4, 7)):
        amt = random.randint(47000, 49800) # Under ₹50,000 limit
        burst_time = base_burst_time + datetime.timedelta(minutes=random.randint(2, 25))
        txn_entries.append({
            "transaction_id": f"TXN_SMURF_{j}_{k:02d}",
            "sender_id": mule,
            "receiver_id": boss,
            "amount": amt,
            "timestamp": burst_time.strftime("%Y-%m-%d %H:%M:%S"),
            "transaction_type": "UPI",
            "location": random.choice(TOWERS).replace("TOWER_", "")
        })

# B. Hawala / Large Criminal Transfers
for j in range(40):
    sender = random.choice(list(criminal_ids))
    receiver = random.choice(list(criminal_ids - {sender}))
    amt = random.randint(150000, 2500000)
    cur_time = txn_time + datetime.timedelta(minutes=random.randint(1, 200000))
    txn_entries.append({
        "transaction_id": f"TXN_HAW_{j:03d}",
        "sender_id": sender,
        "receiver_id": receiver,
        "amount": amt,
        "timestamp": cur_time.strftime("%Y-%m-%d %H:%M:%S"),
        "transaction_type": random.choice(["Cash Deposit", "RTGS/NEFT", "Crypto Transfer"]),
        "location": random.choice(TOWERS).replace("TOWER_", "")
    })

# C. Normal Civilian Noise Transactions
for j in range(NUM_TXNS - len(txn_entries)):
    sender, receiver = random.sample(list(df_entities["entity_id"]), 2)
    amt = random.randint(350, 18500)
    cur_time = txn_time + datetime.timedelta(minutes=random.randint(1, 200000))
    txn_entries.append({
        "transaction_id": f"TXN_NORM_{j:04d}",
        "sender_id": sender,
        "receiver_id": receiver,
        "amount": amt,
        "timestamp": cur_time.strftime("%Y-%m-%d %H:%M:%S"),
        "transaction_type": random.choice(["UPI", "IMPS Wire"]),
        "location": random.choice(TOWERS).replace("TOWER_", "")
    })

df_txns = pd.DataFrame(txn_entries)
df_txns.to_csv(os.path.join(OUTPUT_DIR, "financial_transactions.csv"), index=False)
print(f"[+] Financial Transactions generated: {len(df_txns)} records.")


# ---------------------------------------------------------
# 5. GENERATE SOCIAL MEDIA INTEL
# ---------------------------------------------------------
NUM_POSTS = 50
PLATFORMS = ["Chatgram", "X-Feed", "DarkPost", "InstaNet"]

CODED_POST_TEMPLATES = [
    "Package arrived at {loc} warehouse. Awaiting signal from {boss_alias} to dispatch.",
    "Transfer settled on UPI. Confirm receipt for consignment #8821.",
    "Meeting scheduled at {loc} tonight with team. Bring vehicle {veh}.",
    "New SIM batches ready. Contact @{alias} for login keys.",
    "Cash collected from Devgarh outlet. Heading to safehouse.",
    "Big consignment moving across highway checkpoint at 02:00."
]

social_entries = []
post_time = datetime.datetime(2026, 4, 1, 12, 0, 0)

for i in range(1, NUM_POSTS + 1):
    author = random.choice(list(criminal_ids)) if random.random() < 0.75 else random.choice(list(df_entities["entity_id"]))
    author_info = df_entities[df_entities["entity_id"] == author].iloc[0]
    
    cur_time = post_time + datetime.timedelta(minutes=random.randint(1, 150000))
    platform = random.choice(PLATFORMS)
    
    boss_name = df_entities[df_entities["entity_id"] == "ENT_001"].iloc[0]["name"].split()[0]
    loc = author_info["address_location"].split(", ")[-1]
    veh = author_info["vehicle_number"] if author_info["vehicle_number"] else "MH-12-AB-1234"
    
    template = random.choice(CODED_POST_TEMPLATES)
    text = template.format(loc=loc, boss_alias=boss_name, alias=author_info["name"].replace(" ", "_"), veh=veh)
    
    social_entries.append({
        "post_id": f"POST_{i:03d}",
        "author_entity_id": author,
        "timestamp": cur_time.strftime("%Y-%m-%d %H:%M:%S"),
        "platform": platform,
        "text": text
    })

df_social = pd.DataFrame(social_entries)
df_social.to_csv(os.path.join(OUTPUT_DIR, "social_media_intel.csv"), index=False)
print(f"[+] Social Media Intelligence generated: {len(df_social)} records.")


# ---------------------------------------------------------
# 6. GENERATE CRIMINAL HISTORY DB
# ---------------------------------------------------------
prior_records = []
OFFENSES = [
    "Section 420 IPC (Cheating & Fraud)", "Section 307 IPC (Attempted Extortion)",
    "NDPS Act Section 21 (Narcotics Smuggling)", "Arms Act Section 25 (Unlawful Arms)",
    "IT Act Section 66D (Cyber Impersonation)", "Section 120B IPC (Criminal Conspiracy)"
]
STATUSES = ["Convicted (Bail)", "Pending Trial", "Acquitted", "Absconding / Wanted"]

# Select subset of criminals to have prior police records
record_entities = random.sample(list(criminal_ids), 20)

for idx, entity_id in enumerate(record_entities, 1):
    prior_date = datetime.date(2018, 1, 1) + datetime.timedelta(days=random.randint(0, 2500))
    prior_records.append({
        "record_id": f"CRIM_REC_{idx:03d}",
        "entity_id": entity_id,
        "prior_case_id": f"CASE_{prior_date.year}_{random.randint(100, 999)}",
        "offense_type": random.choice(OFFENSES),
        "date": prior_date.strftime("%Y-%m-%d"),
        "status": random.choice(STATUSES)
    })

df_history = pd.DataFrame(prior_records)
df_history.to_csv(os.path.join(OUTPUT_DIR, "criminal_history_db.csv"), index=False)
print(f"[+] Criminal History DB generated: {len(df_history)} records.")


# ---------------------------------------------------------
# SUMMARY REPORT PRINT
# ---------------------------------------------------------
print("\n" + "="*65)
print("       SYNTHETIC DATASET GENERATION COMPLETE SUMMARY")
print("="*65)
print(f"Total Master Entities       : {len(df_entities)} (Fictional Indian Profiles)")
print(f"Criminal Network Entities  : {len(criminal_ids)} (Mapped across 4 Syndicates)")
print(f"Civilian Noise Entities     : {len(df_entities) - len(criminal_ids)}")
print(f"FIR Unstructured Narratives : {len(df_firs)}")
print(f"Call Detail Records (CDRs)  : {len(df_cdrs)}")
print(f"Financial Transactions      : {len(df_txns)}")
print(f"Social Media Posts          : {len(df_social)}")
print(f"Criminal History Records    : {len(df_history)}")
print("-" * 65)
print("GROUND TRUTH CRIMINAL NETWORK BREAKDOWN:")
for net_id, net_data in NETWORKS_DEF.items():
    print(f"  * {net_id} ({net_data['name']}): {len(net_data['members'])} members")
print("CROSS-NETWORK BRIDGE CONNECTORS:")
print("  * ENT_007: Hawala Conduit between NET_ALPHA & NET_BETA")
print("  * ENT_015: Identity Supplier between NET_BETA & NET_GAMMA")
print("  * ENT_022: Extortion Financier between NET_ALPHA & NET_DELTA")
print("="*65)
print(f"[OK] Files successfully written to directory: {OUTPUT_DIR}")
