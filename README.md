# VERA-SE

Verification-Guided Autonomous Software Repair with Risk-Aware Patch Selection

Author: Mridula Prabhakar

## Overview

VERA-SE investigates verification-guided acceptance and selection of
LLM-generated software repairs.

The project includes:
- A controlled benchmark containing six repair tasks.
- A real-world pilot containing ten localized BugsInPy Black defects.
- Candidate generation, verification, and patch-selection modules.
- Experimental results and research manuscript.

## Controlled Benchmark

The controlled benchmark contains 240 candidate instances:
153 correct and 87 incorrect.

Results and analysis scripts are available in:
- benchmarks/
- experiment_results/
- analyze_ablations.py

## Real-World Pilot

The real-world pilot contains ten localized Black defects.

Four candidate generations were requested per task, resulting in
40 requested generations and 28 valid candidate instances.

The authoritative experimental runs are:

- 20260904_164914: Black-1, 3, 4, 7, 8, 9, and 10.
- 20260904_171236: Black-13, 14, and 16.

The consolidated results are:

- results/final_real_world_candidates.csv
- results/final_real_world_task_summary.csv
- results/final_real_world_metrics.txt

The corresponding candidate patches and diffs are retained under
results/real_world_patches_20260904_164914/
and results/real_world_patches_20260904_171236/.

## Experimental Provenance

The later run 20260904_181853 is excluded from the paper's results.

This repository was initialized after the experiments were conducted.
The initial Git commit preserves the current project snapshot and
does not establish that the current generator implementation is
identical to the frozen experimental implementation.

The current generator must be reconciled with the frozen experimental
configuration before claiming end-to-end reproducibility.

Do not substitute a later run for the authoritative results.

## Manuscript

The research manuscript is located at:

paper/VERA_SE_Manuscript.docx

## Privacy

Local credentials and virtual environments are excluded through
.gitignore. No credentials are required to read the reported results.
