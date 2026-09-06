import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


from data_loader import DataLoader
from nlp_extractor import NLPExtractor
from graph_engine import GraphEngine
from benchmark_evaluator import BenchmarkEvaluator
from pattern_detector import PatternDetector
from copilot import CaseCopilot

def main():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_dir):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    print("Loading data from:", data_dir)
    dl = DataLoader(data_dir)
    print(f"Entities: {len(dl.entities)}, CDRs: {len(dl.cdrs)}, Transactions: {len(dl.transactions)}, FIRs: {len(dl.firs)}")

    nlp = NLPExtractor(dl.entities)
    print("NLP Extractor initialized.")

    ge = GraphEngine(dl, nlp)
    print(f"Graph nodes: {ge.G.number_of_nodes()}, edges: {ge.G.number_of_edges()}")

    pd = PatternDetector(dl, ge)
    smurfs = pd.detect_smurfing_rings()
    print(f"Detected {len(smurfs)} smurfing rings.")

    be = BenchmarkEvaluator(dl, ge)
    results = be.evaluate()
    print("\n================ BENCHMARK RESULTS ================")
    for k, v in results["metrics"].items():
        print(f"  {k}: {v}")
    print("Confusion Matrix:", results["confusion_matrix"])
    print("====================================================\n")

    copilot = CaseCopilot(dl, ge, pd)
    ans = copilot.query_copilot("Who are the kingpins?")
    print("Copilot Kingpins Response:\n", ans["response"])

    # Test get_entity_raw_records
    print("\nTesting get_entity_raw_records for ENT_001...")
    records = copilot.get_entity_raw_records("ENT_001")
    assert "calls" in records and "transactions" in records and "firs" in records
    print(f"ENT_001 records: {len(records['calls'])} calls, {len(records['transactions'])} transactions, {len(records['firs'])} firs.")
    assert len(records["calls"]) > 0
    assert "other_party_name" in records["calls"][0] or "other_party" in records["calls"][0]
    assert "timestamp" in records["calls"][0]
    assert "duration" in records["calls"][0]
    assert len(records["transactions"]) > 0
    assert "other_party" in records["transactions"][0]
    assert "amount" in records["transactions"][0]
    assert "date" in records["transactions"][0]
    assert len(records["firs"]) > 0
    assert "fir_id" in records["firs"][0]
    assert "narrative_excerpt" in records["firs"][0]
    print("All raw records validations passed!")

if __name__ == "__main__":
    main()
