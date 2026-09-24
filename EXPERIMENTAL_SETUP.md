# VERA-SE Experimental Setup

## 1. System Environment

Environment inspected on September 24, 2026.

- Operating system: macOS 15.6
- Architecture: arm64 (Apple Silicon)
- System Python: 3.9.25
- Project virtual environment: Python 3.9.6
- Ollama: 0.33.0
- Model: qwen2.5-coder:7b
- Model ID: dae161e27b0e

The installed dependencies are recorded separately in
environment-requirements.txt.

These versions describe the inspected environment. Exact historical
versions at the time of the frozen runs have not all been established.

## 2. Git Provenance

Current research snapshot:

9cf8a159aad40be400e717cc45ef5f093b08fe3f

Tag:

research-snapshot-20260924

Git was initialized after the experiments.

The snapshot preserves the current project state but must not be
represented as the exact historical generator revision.

## 3. Controlled Benchmark

Six Python repair tasks.

- 240 candidate instances
- 153 oracle-correct candidates
- 87 oracle-incorrect candidates

Results are retained in experiment_results/.

## 4. Real-World Pilot

Ten localized BugsInPy defects from the Black project.

- 40 requested generations
- 28 valid candidate instances
- 27 unique patch contents
- One oracle-positive candidate

Authoritative runs:

20260904_164914
20260904_171236

Consolidated results:

results/final_real_world_candidates.csv
results/final_real_world_task_summary.csv
results/final_real_world_metrics.txt

The later run 20260904_181853 is excluded from the reported results.

## 5. Correctness Assessment

The held-out real-world oracle was used for evaluation after VERA-SE
made its acceptance decision.

Oracle success is a finite-test correctness proxy, not formal proof
of semantic equivalence.

## 6. Reproducibility Limitation

The generator was modified after the frozen experiments.

The current generator must be reconciled with the frozen implementation
before claiming end-to-end reproduction of the reported experiments.

The frozen results must not be replaced by later experimental runs.
