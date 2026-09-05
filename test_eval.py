import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from data_loader import DataLoader
from nlp_extractor import NLPExtractor
from graph_engine import GraphEngine
from benchmark_evaluator import BenchmarkEvaluator
from pattern_detector import PatternDetector

def main():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    dl = DataLoader(data_dir)
    nlp = NLPExtractor(dl.entities)
    ge = GraphEngine(dl, nlp)
    be = BenchmarkEvaluator(dl, ge)
    results = be.evaluate()

    print("=== METRICS ===")
    for k, v in results["metrics"].items():
        print(f"  {k}: {v}")
    print("Confusion Matrix:", results["confusion_matrix"])

    # Inspect false negatives and civilians
    print("\n=== FALSE NEGATIVES (Criminals missed) ===")
    for item in results["sample_results"]:
        if item["verdict"] == "FALSE_NEGATIVE":
            eid = item["entity_id"]
            print(f"  {eid} ({item['name']}): score={item['threat_score']}, role={item['actual_role']}, status={dl.entities[eid]['criminal_status']}")

    print("\n=== TOP CIVILIANS (Highest civilian scores) ===")
    civs = [item for item in results["sample_results"] if not item["actual_criminal"]]
    civs = sorted(civs, key=lambda x: x["threat_score"], reverse=True)
    for c in civs[:5]:
        print(f"  {c['entity_id']} ({c['name']}): score={c['threat_score']}")

if __name__ == "__main__":
    main()
