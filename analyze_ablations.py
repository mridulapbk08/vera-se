import csv
from pathlib import Path


CSV_PATH = Path(
    "experiment_results/vera_experiment_results_rechecked.csv"
)


def as_bool(value):
    return str(value).strip().lower() == "true"


def calculate_metrics(rows, decision_fn):
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    for row in rows:
        predicted = decision_fn(row)
        actual = as_bool(row["oracle_correct"])

        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and not actual:
            tn += 1
        else:
            fn += 1

    total = tp + fp + tn + fn

    accuracy = (
        (tp + tn) / total
        if total
        else 0.0
    )

    precision = (
        tp / (tp + fp)
        if tp + fp
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn
        else 0.0
    )

    far = (
        fp / (fp + tn)
        if fp + tn
        else 0.0
    )

    frr = (
        fn / (fn + tp)
        if fn + tp
        else 0.0
    )

    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "far": far,
        "frr": frr,
    }


def visible_only(row):
    return as_bool(
        row["baseline_a"]
    )


def visible_hidden(row):
    return as_bool(
        row["baseline_b"]
    )


def visible_hidden_behavior(row):
    return (
        as_bool(row["baseline_b"])
        and float(
            row["behavior_score"]
        ) >= 1.0
    )


def visible_hidden_structure(row):
    return (
        as_bool(row["baseline_b"])
        and as_bool(
            row["syntax_valid"]
        )
        and int(
            row[
                "unrelated_function_changes"
            ]
        ) == 0
    )


def full_vera(row):
    return as_bool(
        row["vera"]
    )


def print_metrics(name, metrics):
    print(
        "\n"
        + "=" * 80
    )
    print(name)
    print(
        "=" * 80
    )

    print(
        f"TP: {metrics['tp']}"
    )
    print(
        f"FP: {metrics['fp']}"
    )
    print(
        f"TN: {metrics['tn']}"
    )
    print(
        f"FN: {metrics['fn']}"
    )
    print(
        f"Accuracy: "
        f"{metrics['accuracy']:.3f}"
    )
    print(
        f"Precision: "
        f"{metrics['precision']:.3f}"
    )
    print(
        f"Recall: "
        f"{metrics['recall']:.3f}"
    )
    print(
        f"False acceptance rate: "
        f"{metrics['far']:.3f}"
    )
    print(
        f"False rejection rate: "
        f"{metrics['frr']:.3f}"
    )


def print_summary_table(results):
    print(
        "\n"
        + "=" * 100
    )
    print(
        "ABLATION SUMMARY"
    )
    print(
        "=" * 100
    )

    header = (
        f"{'Method':<34}"
        f"{'Accuracy':>10}"
        f"{'Precision':>12}"
        f"{'Recall':>10}"
        f"{'FAR':>10}"
        f"{'FRR':>10}"
    )

    print(header)
    print("-" * 100)

    for name, metrics in results:
        print(
            f"{name:<34}"
            f"{metrics['accuracy']:>10.3f}"
            f"{metrics['precision']:>12.3f}"
            f"{metrics['recall']:>10.3f}"
            f"{metrics['far']:>10.3f}"
            f"{metrics['frr']:>10.3f}"
        )


def per_task_analysis(
    rows,
    methods,
):
    task_ids = sorted(
        {
            row["task_id"]
            for row in rows
        }
    )

    print(
        "\n"
        + "=" * 100
    )
    print(
        "PER-TASK FALSE ACCEPTANCE RATE"
    )
    print(
        "=" * 100
    )

    header = (
        f"{'Task':<25}"
        f"{'Visible':>12}"
        f"{'Hidden':>12}"
        f"{'+Behavior':>12}"
        f"{'+Structure':>12}"
        f"{'Full VERA':>12}"
    )

    print(header)
    print("-" * 100)

    for task_id in task_ids:
        task_rows = [
            row
            for row in rows
            if row["task_id"]
            == task_id
        ]

        metrics = []

        for _, decision_fn in methods:
            result = calculate_metrics(
                task_rows,
                decision_fn,
            )

            metrics.append(
                result["far"]
            )

        print(
            f"{task_id:<25}"
            f"{metrics[0]:>12.3f}"
            f"{metrics[1]:>12.3f}"
            f"{metrics[2]:>12.3f}"
            f"{metrics[3]:>12.3f}"
            f"{metrics[4]:>12.3f}"
        )


def main():
    rows = []

    with CSV_PATH.open(
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(
            csv_file
        )

        rows = list(reader)

    print(
        f"Loaded {len(rows)} "
        f"candidate results."
    )

    methods = [
        (
            "Visible tests only",
            visible_only,
        ),
        (
            "Visible + hidden",
            visible_hidden,
        ),
        (
            "Visible + hidden + behavior",
            visible_hidden_behavior,
        ),
        (
            "Visible + hidden + structure",
            visible_hidden_structure,
        ),
        (
            "Full VERA",
            full_vera,
        ),
    ]

    results = []

    for name, decision_fn in methods:
        metrics = calculate_metrics(
            rows,
            decision_fn,
        )

        results.append(
            (
                name,
                metrics,
            )
        )

        print_metrics(
            name,
            metrics,
        )

    print_summary_table(
        results
    )

    per_task_analysis(
        rows,
        methods,
    )


if __name__ == "__main__":
    main()