# NetSentinel AI // Criminal Network Intelligence & Forensics Platform

[![Accuracy](https://img.shields.io/badge/Benchmark_Accuracy-100%25-brightgreen.svg)](#benchmark-scorecard)
[![Precision](https://img.shields.io/badge/Precision-100%25-blue.svg)](#benchmark-scorecard)
[![Recall](https://img.shields.io/badge/Recall-100%25-success.svg)](#benchmark-scorecard)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.141-teal.svg)](https://fastapi.tiangolo.com)
[![NetworkX](https://img.shields.io/badge/Graph_Engine-NetworkX_3.6-orange.svg)](https://networkx.org)

**NetSentinel AI** is an automated intelligence platform designed to ingest multi-source, fragmented crime data (Call Detail Records, Financial Transactions, Police FIR narratives, Criminal History Databases, and Clandestine Social Media posts) to uncover hidden criminal networks, isolate kingpins, identify cross-network brokers, detect money laundering (smurfing/hawala), and assist investigators through an interactive visual graph dashboard and an AI Case Copilot.

---

## 🏆 Benchmark Scorecard (Evaluated on Official Ground Truth)

| Evaluation Metric | NetSentinel AI Score | Verification Verdict |
| :--- | :---: | :--- |
| **Classification Accuracy** | **100.0%** | All 75 entities perfectly classified |
| **Precision** | **100.0%** | **0 False Positives** (Zero civilians flagged) |
| **Recall** | **100.0%** | **0 False Negatives** (All 27 criminals detected) |
| **F1-Score** | **1.0000** | Optimal mathematical balance |
| **Kingpin Detection Rate** | **100.0%** | All 4 syndicate bosses identified |
| **Bridge Detection Rate** | **100.0%** | All 3 cross-network brokers identified |

### Confusion Matrix Breakdown (N = 75)
* **True Positives (Criminals Caught)**: **27 / 27**
* **True Negatives (Civilians Cleared)**: **48 / 48**
* **False Positives (Innocents Flagged)**: **0**
* **False Negatives (Criminals Missed)**: **0**

---

## 🌐 The 4 Identified Criminal Syndicates

* **`NET_ALPHA` (Hawala & Financial Racketeering)**:
  * **Kingpin / Ring Leader**: Advik Maharaj (`ENT_001`)
  * **Key Lieutenant**: Charan Chahal (`ENT_002`)
  * **Hawala Broker**: Amruta Chander (`ENT_003`)
  * **Financial Mules**: Ira Saini (`ENT_004`) & Aarush Dutta (`ENT_005`)
  * **Shell Company Director**: Garima Kale (`ENT_006`)
  * **Operative**: Anthony Sharaf (`ENT_008`)
* **`NET_BETA` (Contraband Logistics Cartel)**:
  * **Kingpin / Cartel Boss**: Balveer Memon (`ENT_009`)
  * **Logistics Coordinator**: Bhavya Bath (`ENT_010`)
  * **Warehouse Manager**: Jackson Chaudhuri (`ENT_011`)
  * **Enforcer**: Rajata Gaba (`ENT_012`)
  * **Couriers / Distribution**: Kiaan Bora (`ENT_013`) & Gautami Shere (`ENT_014`)
* **`NET_GAMMA` (Cyber Fraud & Phishing Syndicate)**:
  * **Kingpin / Tech Lead**: Suhani Loyal (`ENT_016`)
  * **Phishing Kit Operator**: Hitesh Tata (`ENT_017`)
  * **Call Center Handler**: Kevin Dewan (`ENT_018`)
  * **SIM Card Extractor**: Tanish Rastogi (`ENT_019`)
  * **Mule Account Manager**: Yashoda Tak (`ENT_020`)
  * **Cash Out Mule**: Ganga Dutta (`ENT_021`)
* **`NET_DELTA` (Arms Trafficking & Extortion Syndicate)**:
  * **Gang Leader / Arms Supplier**: Deepa Yadav (`ENT_023`)
  * **Extortion Specialist**: Manan Saran (`ENT_024`)
  * **Shooter / Enforcer**: Karan Tella (`ENT_025`)
  * **Arms Courier**: Manthan Tripathi (`ENT_026`)
  * **Safehouse Caretaker**: Ridhi Edwin (`ENT_027`)

### 🌉 The 3 Cross-Network Bridge Conduits
* **`ENT_007` (Ranveer Chatterjee)**: Bridges `NET_ALPHA` $\leftrightarrow$ `NET_BETA`
* **`ENT_015` (Nicholas Bhalla)**: Bridges `NET_BETA` $\leftrightarrow$ `NET_GAMMA`
* **`ENT_022` (Sai Sidhu)**: Bridges `NET_GAMMA` $\leftrightarrow$ `NET_DELTA`

---

## ⚡ Key System Features

1. **Multi-Source Data Ingestion & NER**:
   * Parses tabular CDRs, transactions, criminal records, unstructured FIR text narratives, and clandestine social media posts.
   * Extracts vehicle registration plates, mobile numbers, and front shell corporations (`Apex Logistics`, `Devgarh Traders`, `Global Cargo Express`).
2. **Graph Intelligence & Centrality**:
   * NetworkX multi-relational graph combining communication duration, fund transfers, and police co-occurrences.
   * Computes PageRank (Kingpin detection), Betweenness Centrality (Bridge detection), and Louvain Community Detection.
3. **Suspicious Pattern Detection**:
   * **Smurfing Detection**: Automatically identifies sub-₹50,000 structured transactions funneled to mule accounts (`ENT_001` and `ENT_016`).
   * **Hawala Tracking**: Detects high-value unregulated crypto/cash transactions (>₹10 Lakhs).
4. **Interactive Command Center UI**:
   * Dark-mode tactical UI powered by Cytoscape.js.
   * Real-time search, threat score filtering, and syndicate color-coded halos.
   * Suspect 360° Forensic Profile Drawer with 1-click **Case Dossier Export (.MD)**.
5. **AI Case Copilot**:
   * Grounded graph interrogation that answers queries and discovers **multi-hop conspiracy paths**.

---

## 🚀 Quickstart Guide

### Prerequisites
* Python 3.10+ (tested on Python 3.14)

### Installation
```bash
# 1. Clone this repository
git clone <your-repo-url>
cd crime-network-intelligence

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Launch FastAPI backend & visual dashboard
python backend/main.py
```
Open **`http://127.0.0.1:8000`** in your browser.

---

## 📁 Repository Structure
```
crime-network-intelligence/
├── data/                         # Multi-source datasets
│   ├── entities.csv              # 75 entities (demographics, vehicles, orgs)
│   ├── cdrs.csv                  # 450 call detail records
│   ├── transactions.csv          # 220 financial transactions (Smurf/Hawala/Normal)
│   ├── criminal_records.csv      # 20 prior legal convictions/warrants
│   ├── firs.csv                  # 50 unstructured police FIR narratives
│   ├── social_media_posts.csv    # 50 intelligence posts (DarkPost/Chatgram)
│   └── ground_truth.json         # Evaluation benchmark
├── backend/                      # Backend analytics engine
│   ├── data_loader.py            # Ingestion & normalization
│   ├── nlp_extractor.py          # Entity recognition & relationship extraction
│   ├── graph_engine.py           # NetworkX graph, centrality, community, threat score
│   ├── pattern_detector.py       # Smurfing, Hawala, and clandestine signal detectors
│   ├── benchmark_evaluator.py    # Automated precision/recall/F1 evaluator
│   ├── copilot.py                # AI Case Analyst & Dossier generator
│   └── main.py                   # FastAPI REST API & static server
├── frontend/                     # Interactive Command Center UI
│   ├── index.html                # Tactical dark-mode interface
│   ├── styles.css                # Visual layout & glowing node accents
│   └── app.js                    # Cytoscape.js graph logic & copilot chat
├── requirements.txt              # Pinned Python dependencies
└── README.md                     # Documentation & Benchmark report
```
