from typing import Dict, Any


class BenchmarkEvaluator:
    """
    Evaluates the GraphEngine's predictions against ground-truth labels.

    Criminal/civilian classification metrics (accuracy, precision, recall, F1)
    are computed against ground_truth.json.

    Kingpin and bridge detection rates are computed dynamically by comparing
    the graph engine's detected sets against the ground-truth roles — no
    hardcoded entity ID sets anywhere in this evaluator.
    """

    def __init__(self, data_loader, graph_engine):
        self.dl = data_loader
        self.ge = graph_engine
        self.gt = data_loader.ground_truth

    def evaluate(self) -> Dict[str, Any]:
        tp = tn = fp = fn = 0
        predictions_table = []

        for eid, gt_data in self.gt.items():
            actual_criminal = gt_data["is_criminal"]
            predicted_criminal = self.ge.is_criminal_pred.get(eid, False)

            if actual_criminal and predicted_criminal:
                tp += 1
                verdict = "TRUE_POSITIVE"
            elif not actual_criminal and not predicted_criminal:
                tn += 1
                verdict = "TRUE_NEGATIVE"
            elif not actual_criminal and predicted_criminal:
                fp += 1
                verdict = "FALSE_POSITIVE"
            else:
                fn += 1
                verdict = "FALSE_NEGATIVE"

            predictions_table.append({
                "entity_id": eid,
                "name": gt_data.get("name") or self.dl.entities.get(eid, {}).get("name", eid),
                "actual_criminal": actual_criminal,
                "predicted_criminal": predicted_criminal,
                "threat_score": self.ge.threat_scores.get(eid, 0),
                "actual_role": gt_data.get("primary_role"),
                "predicted_role": self.ge.detected_roles.get(eid),
                "verdict": verdict
            })

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        accuracy  = (tp + tn) / len(self.gt) if len(self.gt) > 0 else 0.0
        f1        = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # ── Dynamic Kingpin evaluation ────────────────────────────────
        # GT kingpins: any entity whose ground-truth primary_role contains "Kingpin"
        gt_kingpins = {
            eid for eid, d in self.gt.items()
            if "Kingpin" in d.get("primary_role", "")
        }
        pred_kingpins = {
            eid for eid, r in self.ge.detected_roles.items()
            if "Kingpin" in r
        }
        kingpin_tp = len(gt_kingpins & pred_kingpins)
        kingpin_recall = kingpin_tp / len(gt_kingpins) if gt_kingpins else 0.0

        # ── Dynamic Bridge evaluation ─────────────────────────────────
        # GT bridges: any entity whose ground-truth is_bridge == true
        gt_bridges = {
            eid for eid, d in self.gt.items()
            if d.get("is_bridge", False)
        }
        pred_bridges = {
            eid for eid, b in self.ge.is_bridge_pred.items() if b
        }
        bridge_tp = len(gt_bridges & pred_bridges)
        bridge_recall = bridge_tp / len(gt_bridges) if gt_bridges else 0.0

        return {
            "metrics": {
                "accuracy_percent": round(accuracy * 100, 2),
                "precision_percent": round(precision * 100, 2),
                "recall_percent": round(recall * 100, 2),
                "f1_score": round(f1, 4),
                "kingpin_detection_rate": round(kingpin_recall * 100, 2),
                "bridge_detection_rate": round(bridge_recall * 100, 2),
            },
            "confusion_matrix": {
                "true_positives": tp,
                "true_negatives": tn,
                "false_positives": fp,
                "false_negatives": fn,
                "total_eval_samples": len(self.gt)
            },
            "ground_truth_targets": {
                "total_criminals": sum(1 for d in self.gt.values() if d["is_criminal"]),
                "total_civilians": sum(1 for d in self.gt.values() if not d["is_criminal"]),
                "kingpins": sorted(gt_kingpins),
                "bridges": sorted(gt_bridges),
                "detected_kingpins": sorted(pred_kingpins),
                "detected_bridges": sorted(pred_bridges),
            },
            "sample_results": predictions_table
        }
