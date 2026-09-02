# SIH26189 — AI-Powered Criminal Network Analysis System
## Synthetic Multi-Source Law Enforcement Dataset Generator

**Sponsoring Body:** Ministry of Home Affairs / National Crime Records Bureau (NCRB) / Women Safety Division  
**Category:** Software | **Theme:** Blockchain & Cybersecurity  
**Local Execution:** 100% Offline / Local Data Generation & Analysis

---

## 📌 Dataset Overview

This project includes a Python synthetic data generator designed specifically for **SIH Problem Statement SIH26189**. Real NCRB law enforcement data is classified; this script generates a **100% fictional yet realistic Indian law enforcement multi-source dataset** containing embedded criminal syndicates, cross-network bridge connectors, structuring anomalies, and unstructured text FIR narratives.

The generated dataset is stored in the `./data/` folder and comprises 7 interconnected files:

| File Name | Record Count | Description |
|---|---|---|
| `entities_master.csv` | 75 records | Master entity profiles (names, phones, locations, vehicles, orgs) |
| `ground_truth_networks.json` | 75 mappings | Ground-truth labels mapping entity IDs to syndicates and roles |
| `firs_reports.csv` | 50 narratives | Unstructured police FIRs with embedded names, phones & vehicles |
| `call_detail_records.csv` | 450 CDR logs | Telecommunication logs with frequency biases matching network structure |
| `financial_transactions.csv` | 220 transactions | Banking, UPI & Crypto transfers with smurfing/structuring patterns |
| `social_media_intel.csv` | 50 posts | Coded social posts, aliases, and location check-ins |
| `criminal_history_db.csv` | 20 records | Prior criminal records and case statuses for key suspects |

---

## 🕸️ Hidden Criminal Network Architecture

The generator embeds **4 distinct criminal networks** with 27 total criminal entities and **3 cross-network bridge connectors**:

```
 ┌───────────────────────────┐           ┌───────────────────────────┐
 │        NET_ALPHA          │           │         NET_BETA          │
 │ (Hawala & Crypto Ring)    │           │(Narcotics & Trafficking)  │
 │  Leader: ENT_001          │           │  Leader: ENT_009          │
 └─────────────┬─────────────┘           └─────────────┬─────────────┘
               │                                       │
               └───────────► ENT_007 (Bridge) ◄────────┘
                      (Hawala Conduit for Drugs)
                                 │
                                 ▼
 ┌───────────────────────────┐           ┌───────────────────────────┐
 │        NET_GAMMA          │           │        NET_DELTA          │
 │ (Cyber Fraud & Phishing)  │           │ (Arms & Extortion Gang)   │
 │  Leader: ENT_016          │           │  Leader: ENT_023          │
 └─────────────┬─────────────┘           └─────────────┬─────────────┘
               │                                       │
               └───────────► ENT_022 (Bridge) ◄────────┘
                     (Extortion Ring Financier)
```

### 1. Syndicate Breakdown
- **`NET_ALPHA` (Hawala & Crypto Money Laundering - 8 Members):**
  - **Kingpin:** `ENT_001` (Directs shell companies & wire routing)
  - **Key Lieutenant:** `ENT_002`
  - **Hawala Broker:** `ENT_003`
  - **Mules:** `ENT_004`, `ENT_005`
  - **Shell Company Director:** `ENT_006`
  - **Operative:** `ENT_008`

- **`NET_BETA` (Narcotics & Contraband Smuggling - 8 Members):**
  - **Kingpin:** `ENT_009` (Cartel boss)
  - **Logistics Coordinator:** `ENT_010`
  - **Warehouse Manager:** `ENT_011`
  - **Enforcer:** `ENT_012`
  - **Distributors:** `ENT_013`, `ENT_014`

- **`NET_GAMMA` (Cyber Fraud & Phishing Ring - 8 Members):**
  - **Kingpin:** `ENT_016` (Tech lead)
  - **Phishing Kit Operator:** `ENT_017`
  - **Call Center Handler:** `ENT_018`
  - **SIM Extractor:** `ENT_019`
  - **Mule Managers:** `ENT_020`, `ENT_021`

- **`NET_DELTA` (Illegal Firearms & Extortion Gang - 6 Members):**
  - **Gang Leader:** `ENT_023` (Arms supplier)
  - **Extortion Specialist:** `ENT_024`
  - **Enforcer/Shooter:** `ENT_025`
  - **Arms Courier:** `ENT_026`
  - **Hideout Caretaker:** `ENT_027`

### 2. Overlapping Bridge Connectors (High Betweenness Centrality)
- **`ENT_007` (Hawala Conduit):** Belongs to both `NET_ALPHA` & `NET_BETA`. Routes narcotics money through Hawala channels.
- **`ENT_015` (Identity Supplier):** Belongs to both `NET_BETA` & `NET_GAMMA`. Supplies stolen IDs from narcotics victims to cyber fraud rings.
- **`ENT_022` (Extortion Financier):** Belongs to both `NET_GAMMA` & `NET_DELTA`. Uses cyber fraud proceeds to finance arms procurement for extortion gangs.

---

## 🔍 Data Schemas

### 1. `entities_master.csv`
- `entity_id`: Unique identifier (`ENT_001` to `ENT_075`).
- `name`: Fictional Indian name.
- `age`: Age (22–65).
- `gender`: Male / Female.
- `phone_number`: Indian format (`+91 98xxx xxxxx`).
- `address_location`: Fictional Indian town & street (`Devgarh`, `Anandpur`, `Cyberabad`, etc.).
- `vehicle_number`: Indian vehicle registration (`MH-12-AB-1234`, `DL-08-CD-9102`).
- `known_organization`: Fictional corporate front or logistics firm.

### 2. `firs_reports.csv`
- `fir_id`: Unique FIR reference (`FIR_2026_001`).
- `date`: Incident date (`YYYY-MM-DD`).
- `police_station`: Police jurisdiction name.
- `incident_type`: Crime category.
- `narrative_text`: 2-5 sentence narrative naturally embedding names, phone numbers, vehicle numbers, locations, and organization names for NLP entity extraction testing.

### 3. `call_detail_records.csv`
- `call_id`: Call record reference (`CDR_0001`).
- `caller_id` / `callee_id`: Entity IDs involved in call.
- `timestamp`: Call timestamp.
- `duration_seconds`: Call duration in seconds.
- `cell_tower_location`: Cell tower identifier (`TOWER_DEVGARH_CENTRAL`).

### 4. `financial_transactions.csv`
- `transaction_id`: Transaction reference (`TXN_SMURF_...` or `TXN_HAW_...`).
- `sender_id` / `receiver_id`: Entity IDs.
- `amount`: Transfer amount in ₹.
- `timestamp`: Transaction time.
- `transaction_type`: `UPI`, `Cash Deposit`, `RTGS/NEFT`, `Crypto Transfer`.
- `location`: Transaction location.

### 5. `social_media_intel.csv`
- `post_id`: Post reference (`POST_001`).
- `author_entity_id`: Entity ID.
- `timestamp`: Post timestamp.
- `platform`: `Chatgram`, `X-Feed`, `DarkPost`, `InstaNet`.
- `text`: Post text containing coded slang, aliases, and check-in points.

### 6. `criminal_history_db.csv`
- `record_id`: Criminal database key (`CRIM_REC_001`).
- `entity_id`: Entity ID.
- `prior_case_id`: Court case number (`CASE_2022_412`).
- `offense_type`: IPC/NDPS/Arms Act section.
- `date`: Filing date.
- `status`: Case outcome status.

---

## ⚡ How to Generate / Regenerate Data

To run or tweak the synthetic dataset generator script:

```bash
python generate_dataset.py
```

### Script Customization Options
- To change entity counts or call density, edit constants in `generate_dataset.py`:
  - `NUM_ENTITIES = 75`
  - `NUM_FIRS = 50`
  - `NUM_CDRS = 450`
  - `NUM_TXNS = 220`
  - `RANDOM_SEED = 42` (ensures exact reproducible output)
