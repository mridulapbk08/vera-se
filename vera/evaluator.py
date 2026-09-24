class ExperimentEvaluator:
    def __init__(self, ground_truth):
        self.ground_truth = ground_truth

    def evaluate_method(
        self,
        results,
        decision_function,
    ):
        tp = 0
        fp = 0
        tn = 0
        fn = 0

        for result in results:
            predicted = decision_function(
                result
            )

            actual = self.ground_truth.get(
                result.candidate_id,
                False,
            )

            if predicted and actual:
                tp += 1

            elif predicted and not actual:
                fp += 1

            elif not predicted and not actual:
                tn += 1

            elif not predicted and actual:
                fn += 1

        total = (
            tp
            + fp
            + tn
            + fn
        )

        accuracy = (
            (tp + tn) / total
            if total > 0
            else 0.0
        )

        precision = (
            tp / (tp + fp)
            if (tp + fp) > 0
            else 0.0
        )

        recall = (
            tp / (tp + fn)
            if (tp + fn) > 0
            else 0.0
        )

        false_acceptance_rate = (
            fp / (fp + tn)
            if (fp + tn) > 0
            else 0.0
        )

        return {
            "true_positive": tp,
            "false_positive": fp,
            "true_negative": tn,
            "false_negative": fn,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "false_acceptance_rate": (
                false_acceptance_rate
            ),
        }