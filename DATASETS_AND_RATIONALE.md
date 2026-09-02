# Comprehensive Guide: Datasets & Investigative Rationale
## SIH Problem Statement SIH26189 — AI-Powered Criminal Network Analysis System
**Sponsoring Organization:** Ministry of Home Affairs / National Crime Records Bureau (NCRB) / Women Safety Division

---

## 📌 Executive Summary & Core Objective

In real-world police investigations, intelligence is fragmented across multiple specialized divisions—Cyber Cells, Anti-Narcotics, Financial Intelligence Units (FIU), Telecom Monitoring, and Local Police Stations. No single database holds the entire picture. 

To evaluate an **AI-Powered Criminal Network Analysis System**, we created a multi-modal, multi-source synthetic dataset simulating real law enforcement inputs. Every file in the dataset serves a specific role in testing **NLP Entity Extraction**, **Graph Construction**, **Network Analytics (Centrality/Clustering)**, and **Anomaly Detection**.

All dataset files reside locally in `./data/`. Below is the complete explanation of each dataset and its investigative rationale.

---

## 📂 Detailed Dataset Breakdown & Rationale

```
                                  ┌───────────────────────────────┐
                                  │      entities_master.csv      │
                                  │  (Master Entity Registry)     │
                                  └───────────────┬───────────────┘
                                                  │
         ┌────────────────────────┬───────────────┼───────────────┬────────────────────────┐
         │                        │               │               │                        │
         ▼                        ▼               ▼               ▼                        ▼
┌─────────────────┐      ┌─────────────────┐ ┌─────────┐ ┌─────────────────┐      ┌─────────────────┐
│ firs_reports.csv│      │ call_detail_... │ │ financial│ │ social_media_...│      │ criminal_histo..│
│(Unstructured)   │      │ (CDR Telecom)   │ │ (Trans. │ │ (OSINT Coded)   │      │ (Prior Records) │
└─────────────────┘      └─────────────────┘ └─────────┘ └─────────────────┘      └─────────────────┘
```

---

### 1. `entities_master.csv` & `ground_truth_networks.json`
* **File Type:** CSV (Master Profiles) & JSON (Ground-Truth Labels)
* **Record Count:** 75 Fictional Entities
* **Key Fields:** `entity_id`, `name`, `age`, `gender`, `phone_number`, `address_location`, `vehicle_number`, `known_organization`

#### 💡 Rationale & Investigative Purpose:
- **Central Node Registry:** Represents the master directory of individuals tracked by the system. In graph analysis, nodes require canonical attribute anchors (Phone, Name, Address, Vehicle) to perform **Entity Disambiguation & Entity Resolution** across multiple noisy datasets.
- **Ground-Truth Benchmarking (`ground_truth_networks.json`):** Maps every entity ID to its ground-truth network (`NET_ALPHA`, `NET_BETA`, `NET_GAMMA`, `NET_DELTA`), role (Kingpin, Lieutenant, Mule, Bridge), and criminal flag. This allows hackathon evaluators to programmatically compute Precision, Recall, and F1-Score for entity extraction and community detection algorithms.

---

### 2. `firs_reports.csv`
* **File Type:** CSV (Unstructured Police Narratives)
* **Record Count:** 50 Police FIR Narratives
* **Key Fields:** `fir_id`, `date`, `police_station`, `incident_type`, `narrative_text`

#### 💡 Rationale & Investigative Purpose:
- **Testing NLP & Named Entity Recognition (NER):** Real police FIRs are written as unstructured narrative text. Investigators cannot manually tag thousands of reports. This dataset tests the AI system's ability to automatically extract entities (`PERSON`, `ALIAS`, `PHONE`, `LOCATION`, `VEHICLE`, `ORGANIZATION`) from raw police text.
- **Uncovering Co-Occurrence Relationships:** If `ENT_001` and `ENT_002` are mentioned together in an FIR alongside vehicle `MH-12-AB-1234`, the NLP pipeline automatically constructs a co-presence edge (`SEEN_WITH`, `MENTIONED_IN_FIR`) in the knowledge graph.

---

### 3. `call_detail_records.csv` (CDRs)
* **File Type:** CSV (Telecommunication Call Logs)
* **Record Count:** 450 Call Records
* **Key Fields:** `call_id`, `caller_id`, `callee_id`, `timestamp`, `duration_seconds`, `cell_tower_location`

#### 💡 Rationale & Investigative Purpose:
- **Communication Network Mapping:** CDR logs form the backbone of modern criminal network analysis. By analyzing call frequency, call duration, and timing, the graph engine constructs weighted communication edges (`CO_CALLED`).
- **Evaluating Network Topology:** 
  - Members of the same syndicate have a **high call frequency bias** (65% of calls).
  - Cross-network "Bridge" entities connect separate syndicates (15% of calls).
  - Background noise calls (20%) test the system's ability to filter out everyday civilian calls from high-risk criminal communications.

---

### 4. `financial_transactions.csv`
* **File Type:** CSV (Banking & Crypto Transaction Ledgers)
* **Record Count:** 220 Transaction Records
* **Key Fields:** `transaction_id`, `sender_id`, `receiver_id`, `amount`, `timestamp`, `transaction_type`, `location`

#### 💡 Rationale & Investigative Purpose:
- **Money Trail & Hawala Tracking:** Criminal syndicates are driven by financial gain. Following the money reveals ringleaders who never make direct phone calls or commit physical crimes.
- **Embedded Anomaly Patterns:**
  - **Financial Structuring ("Smurfing"):** Embedded bursts of 4–7 small UPI transfers (e.g., ₹48,200, ₹49,100, ₹47,800) executed within minutes to stay under the ₹50,000 Financial Intelligence Unit (FIU) mandatory reporting threshold.
  - **Multi-Hop Hawala Transfers:** Large transfers (₹1.5 Lakhs – ₹25 Lakhs) routed through financial mules (`ENT_004`, `ENT_005`) to Kingpin accounts (`ENT_001`, `ENT_016`).

---

### 5. `social_media_intel.csv`
* **File Type:** CSV (OSINT & Coded Social Feeds)
* **Record Count:** 50 Social Media Posts
* **Key Fields:** `post_id`, `author_entity_id`, `timestamp`, `platform`, `text`

#### 💡 Rationale & Investigative Purpose:
- **Open-Source Intelligence (OSINT) Integration:** Modern gangs communicate via encrypted or social platforms using coded language, alias handles, and location check-ins.
- **Coded Sentiment & Alias Disambiguation:** Tests the AI's ability to match social handles (`@Vikram_Devgarh`) with physical entity profiles, and detect suspicious keywords (e.g., *"Package arrived at warehouse"*, *"Transfer settled on UPI"*, *"Consignment moving across highway"*).

---

### 6. `criminal_history_db.csv`
* **File Type:** CSV (Prior Police Records Database)
* **Record Count:** 20 Offense Records
* **Key Fields:** `record_id`, `entity_id`, `prior_case_id`, `offense_type`, `date`, `status`

#### 💡 Rationale & Investigative Purpose:
- **Threat Matrix Matrix & Risk Scoring:** Not all network nodes carry equal risk. A node with active CDR traffic AND a prior conviction under the NDPS Act or Arms Act receives an elevated threat score (e.g., 92/100).
- **Recidivism & Modus Operandi Tracking:** Connects past legal outcomes (`Convicted (Bail)`, `Absconding / Wanted`, `Pending Trial`) to current investigation graphs.

---

## 🎯 Ground-Truth Criminal Networks & Analytics Validation

The dataset embeds **4 hidden criminal syndicates** and **3 cross-network bridge connectors** to validate graph analytics algorithms:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        GROUND-TRUTH SYNDICATE STRUCTURE                                │
├──────────────┬──────────────────────────────────────────┬─────────┬────────────────────┤
│ Network ID   │ Description & Domain                     │ Size    │ Kingpin / Leader   │
├──────────────┼──────────────────────────────────────────┼─────────┼────────────────────┤
│ NET_ALPHA    │ Hawala & Crypto Money Laundering Ring    │ 8 Nodes │ ENT_001            │
│ NET_BETA     │ Narcotics & Contraband Smuggling Cartel  │ 8 Nodes │ ENT_009            │
│ NET_GAMMA    │ Cyber Fraud & Phishing Syndicate         │ 8 Nodes │ ENT_016            │
│ NET_DELTA    │ Illegal Firearms & Extortion Gang        │ 6 Nodes │ ENT_023            │
└──────────────┴──────────────────────────────────────────┴─────────┴────────────────────┘
```

### 🌉 Cross-Network Bridge Connectors (High Betweenness Centrality):
1. **`ENT_007` (Hawala Conduit):** Belongs to both `NET_ALPHA` (Hawala) & `NET_BETA` (Narcotics). Launders drug proceeds through Hawala wire transfers.
2. **`ENT_015` (Identity Supplier):** Belongs to both `NET_BETA` (Narcotics) & `NET_GAMMA` (Cyber Fraud). Supplies forged IDs stolen from narcotics victims to cyber phishing rings.
3. **`ENT_022` (Extortion Financier):** Belongs to both `NET_GAMMA` (Cyber Fraud) & `NET_DELTA` (Firearms Gang). Uses cyber fraud proceeds to fund illegal arms procurement for extortion gangs.

---

## 🛡️ Ethics, Privacy & Compliance Note

- **100% Synthetic & Fictional:** All names, phone numbers, addresses, vehicle registrations, and narratives are purely generated using random seeds (`Faker en_IN`). No real individuals, organizations, or real-world cases are referenced.
- **Strict Offline/Local Execution:** The generation script (`generate_dataset.py`) runs 100% locally on your machine. No data is transmitted to external servers or remote git repositories.
