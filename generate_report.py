import csv
from pathlib import Path


CSV_PATH = Path(
    "experiment_results/vera_experiment_results_rechecked.csv"
)

OUTPUT_PATH = Path(
    "experiment_results/vera_summary_report.txt"
)


def as_bool(value):
    return (
        str(value)
        .strip()
        .lower()
        == "true"
    )


def calculate_metrics(rows, decision_fn):
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    for row in rows:
        predicted = decision_fn(row)
        actual = as_bool(
            row["oracle_correct"]
        )

        if predicted and actual:
            tp += 1

        elif predicted and not actual:
            fp += 1

        elif not predicted and not actual:
            tn += 1

        else:
            fn += 1

    total = (
        tp + fp + tn + fn
    )

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
        as_bool(
            row["baseline_b"]
        )
        and float(
            row["behavior_score"]
        ) >= 1.0
    )


def visible_hidden_structure(row):
    return (
        as_bool(
            row["baseline_b"]
        )
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


def percent(value):
    return (
        f"{value * 100:.1f}%"
    )


def make_table(results):
    lines = []

    lines.append(
        "| Method | Accuracy | Precision | Recall | FAR | FRR | TP | FP | TN | FN |"
    )

    lines.append(
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    )

    for name, metrics in results:
        lines.append(
            f"| {name} "
            f"| {percent(metrics['accuracy'])} "
            f"| {percent(metrics['precision'])} "
            f"| {percent(metrics['recall'])} "
            f"| {percent(metrics['far'])} "
            f"| {percent(metrics['frr'])} "
            f"| {metrics['tp']} "
            f"| {metrics['fp']} "
            f"| {metrics['tn']} "
            f"| {metrics['fn']} |"
        )

    return "\n".join(lines)


def per_task_far(rows, methods):
    task_ids = sorted(
        {
            row["task_id"]
            for row in rows
        }
    )

    lines = []

    lines.append(
        "| Task | Visible | Hidden | + Behavior | + Structure | Full VERA |"
    )

    lines.append(
        "|---|---:|---:|---:|---:|---:|"
    )

    for task_id in task_ids:
        task_rows = [
            row
            for row in rows
            if row["task_id"]
            == task_id
        ]

        fars = []

        for _, decision_fn in methods:
            metrics = calculate_metrics(
                task_rows,
                decision_fn,
            )

            fars.append(
                metrics["far"]
            )

        lines.append(
            f"| {task_id} "
            f"| {percent(fars[0])} "
            f"| {percent(fars[1])} "
            f"| {percent(fars[2])} "
            f"| {percent(fars[3])} "
            f"| {percent(fars[4])} |"
        )

    return "\n".join(lines)


def main():
    with CSV_PATH.open(
        newline="",
        encoding="utf-8",
    ) as csv_file:
        rows = list(
            csv.DictReader(
                csv_file
            )
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
            "Full VERA-SE",
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

    baseline_b = results[1][1]
    vera = results[4][1]

    fp_reduction = (
        (
            baseline_b["fp"]
            - vera["fp"]
        )
        / baseline_b["fp"]
        if baseline_b["fp"] > 0
        else 0.0
    )

    accuracy_gain = (
        vera["accuracy"]
        - baseline_b["accuracy"]
    )

    far_reduction = (
        baseline_b["far"]
        - vera["far"]
    )

    report = []

    report.append(
        "VERA-SE EXPERIMENTAL SUMMARY"
    )

    report.append(
        "=" * 70
    )

    report.append("")

    report.append(
        f"Total candidates evaluated: "
        f"{len(rows)}"
    )

    report.append(
        "Benchmark tasks: 6"
    )

    report.append(
        "Independent generation runs per task: 10"
    )

    report.append(
        "Candidates per generation: 4"
    )

    report.append("")

    report.append(
        "OVERALL RESULTS"
    )

    report.append(
        "-" * 70
    )

    report.append("")

    report.append(
        make_table(
            results
        )
    )

    report.append("")

    report.append(
        "KEY FINDINGS"
    )

    report.append(
        "-" * 70
    )

    report.append("")

    report.append(
        "1. False acceptances eliminated "
        "relative to the visible + hidden "
        "test baseline:"
    )

    report.append(
        f"   {baseline_b['fp']} -> "
        f"{vera['fp']}"
    )

    report.append(
        f"   Reduction: "
        f"{percent(fp_reduction)}"
    )

    report.append("")

    report.append(
        "2. False acceptance rate:"
    )

    report.append(
        f"   Baseline B: "
        f"{percent(baseline_b['far'])}"
    )

    report.append(
        f"   VERA-SE: "
        f"{percent(vera['far'])}"
    )

    report.append(
        f"   Absolute reduction: "
        f"{far_reduction * 100:.1f} "
        f"percentage points"
    )

    report.append("")

    report.append(
        "3. Accuracy:"
    )

    report.append(
        f"   Baseline B: "
        f"{percent(baseline_b['accuracy'])}"
    )

    report.append(
        f"   VERA-SE: "
        f"{percent(vera['accuracy'])}"
    )

    report.append(
        f"   Improvement: "
        f"{accuracy_gain * 100:.1f} "
        f"percentage points"
    )

    report.append("")

    report.append(
        "4. Precision:"
    )

    report.append(
        f"   VERA-SE: "
        f"{percent(vera['precision'])}"
    )

    report.append("")

    report.append(
        "5. Recall:"
    )

    report.append(
        f"   VERA-SE: "
        f"{percent(vera['recall'])}"
    )

    report.append("")

    report.append(
        "6. False rejection rate:"
    )

    report.append(
        f"   VERA-SE: "
        f"{percent(vera['frr'])}"
    )

    report.append("")

    report.append(
        "PER-TASK FALSE ACCEPTANCE RATE"
    )

    report.append(
        "-" * 70
    )

    report.append("")

    report.append(
        per_task_far(
            rows,
            methods,
        )
    )

    report.append("")

    report.append(
        "INTERPRETATION"
    )

    report.append(
        "-" * 70
    )

    report.append("")

    report.append(
        "The controlled benchmark indicates "
        "that behavior-preservation verification "
        "is the primary contributor to the "
        "reduction in false acceptance of "
        "LLM-generated patches."
    )

    report.append("")

    report.append(
        "The visible + hidden test baseline "
        f"produced {baseline_b['fp']} false "
        "acceptances, while VERA-SE produced "
        f"{vera['fp']}."
    )

    report.append("")

    report.append(
        "The structural scope constraint did "
        "not reduce false acceptance in this "
        "benchmark and introduced one false "
        "rejection, showing a conservative "
        "precision-recall tradeoff."
    )

    report.append("")

    report.append(
        "LIMITATIONS"
    )

    report.append(
        "-" * 70
    )

    report.append("")

    report.append(
        "- The benchmark currently contains "
        "six synthetic repair tasks."
    )

    report.append(
        "- The 240 candidates were generated "
        "from repeated runs over these tasks, "
        "so candidate count should not be "
        "interpreted as 240 independent bugs."
    )

    report.append(
        "- Behavior probes were manually "
        "specified for the controlled tasks."
    )

    report.append(
        "- Results should therefore be treated "
        "as controlled prototype evidence, "
        "not final evidence of generalization "
        "to real-world software repositories."
    )

    report_text = "\n".join(
        report
    )

    OUTPUT_PATH.write_text(
        report_text,
        encoding="utf-8",
    )

    print(
        report_text
    )

    print(
        "\n"
        + "=" * 70
    )

    print(
        f"Report saved to: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()