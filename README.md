# VERA-SE

**Verification-Guided Autonomous Software Repair with Risk-Aware Patch Selection**

Mridula Prabhakar · Independent research preprint, 2026 · [https://doi.org/10.5281/zenodo.23440127](https://doi.org/10.5281/zenodo.23440127)

VERA-SE separates the generation of software patches by a large language model from the decision to accept them. A local code model proposes several candidate repairs, and a verifier gathers independent evidence for each one (syntax validity, whether the target was changed, whether the change stayed inside the permitted scope, behavioural checks where available, and the size of the change) before any patch is accepted. The research question is whether this evidence reduces the acceptance of incorrect patches compared with accepting whatever passes the visible tests.

The project evaluates the idea in two settings:

* a **controlled benchmark** of six Python repair tasks and 240 candidate instances; and
* a **real-world pilot** on ten localised defects of the Black formatter from BugsInPy.

---

## Key Results

### Controlled benchmark (240 candidate instances: 153 correct, 87 incorrect)

| Configuration | Accuracy | Precision | Recall | False acceptance | False rejection |
| --- | ---: | ---: | ---: | ---: | ---: |
| Visible tests only | 72.9% | 70.2% | 100.0% | 74.7% | 0.0% |
| Visible + hidden tests | 90.0% | 86.4% | 100.0% | 27.6% | 0.0% |
| Visible + hidden + behaviour | 100.0% | 100.0% | 100.0% | 0.0% | 0.0% |
| Visible + hidden + structure | 89.6% | 86.4% | 99.3% | 27.6% | 0.7% |
| **Full VERA-SE** | **99.6%** | **100.0%** | **99.3%** | **0.0%** | **0.7%** |

Visible tests alone accepted 65 of the 87 incorrect candidates. Hidden tests reduced this to 24, and the full verifier to 0, at the cost of one false rejection out of 153 correct candidates. The reduction comes from the behavioural checks; the structural checks added no false-acceptance benefit and caused the one false rejection.

The behavioural probes and the held-out oracle were written from the same task specification and overlap substantially (the label-formatting probe reproduces every oracle example). The 0% false-acceptance rate is therefore partly a consequence of probe design, and should be read as a demonstration of the mechanism rather than an estimate of the gain without such probes. The 240 instances are repeated candidates for six tasks, not 240 independent bugs.

### Real-world pilot (ten Black defects from BugsInPy)

| Measure | Value |
| --- | ---: |
| Localised defects | 10 |
| Requested generations | 40 |
| Valid candidate instances | 28 |
| Unique patched-source contents | 27 |
| Tasks with at least one valid candidate | 8 / 10 |
| Oracle-positive candidates | 1 |

| Metric (28 valid candidates) | Visible-test baseline | VERA-SE |
| --- | ---: | ---: |
| True positives | 1 | 0 |
| False positives | 1 | 1 |
| True negatives | 26 | 26 |
| False negatives | 0 | 1 |
| Accuracy | 96.4% | 92.9% |
| False acceptance rate | 3.7% | 3.7% |
| False rejection rate | 0.0% | 100.0% |

In the pilot the real-world verifier did not improve on the visible-test baseline. In Black-9, the only defect with an oracle-correct patch, VERA-SE accepted candidate 2 (score 0.945, change risk 0.364), which passed only one of three oracle tests, and rejected candidate 4 (score 0.905), which passed all three, because its change risk of 0.636 exceeded the 0.50 limit. With a single positive instance, recall and false rejection are not stable estimates. The contrast between the two settings motivates deriving stronger behavioural properties automatically rather than relying on generic structural and change-size signals.

---

## How the Verifier Decides

**Controlled configuration.** A candidate is accepted only if all of these hold: visible and hidden tests pass, the code is syntactically valid, the target function changed, no other function changed, every behavioural probe passes, and the verification score is at least 0.80. The score combines visible-test pass ratio, hidden-test pass ratio, behavioural score, syntax validity and change size, minus a penalty for changes to unrelated functions.

**Real-world configuration.** No behavioural probes are available. A candidate is accepted only if the visible triggering test passes, the code is syntactically valid, the change stays within the authorised scope, the target changed, and the normalised change risk is at most 0.50. The held-out oracle is run only after the decision, to label candidates.

When several candidates are accepted, the one with the highest score is selected; if none is accepted, the system abstains. The change-risk value measures the size of a change relative to the original code. It is not a probability of correctness.

---

## Repository Layout

```text
vera/                        framework modules (generators, verifiers, AST and behaviour analysers, selector)
main.py                      one generation round over the six controlled tasks
run_experiments.py           controlled benchmark runner (10 generations per task, 4 candidates each)
run_real_world.py            real-world pilot runner
reevaluate_oracle.py         re-runs the oracle tests on the controlled candidates
analyze_ablations.py         ablation metrics for the controlled benchmark
generate_report.py           writes experiment_results/vera_summary_report.txt
benchmarks/                  six controlled tasks: source, visible, hidden and oracle tests
real_world_oracles/          held-out oracle tests for the ten Black defects
experiment_results/          controlled-benchmark results and summary report
results/                     real-world candidates, task summaries, metrics, patches and diffs
reproducibility/             frozen-generator notes and SHA-256 hashes of the result files
EXPERIMENTAL_SETUP.md        environment, provenance and run details
paper/                       earlier manuscript version
```

The final paper is the [Zenodo preprint](https://doi.org/10.5281/zenodo.23440127).

---

## Reproducing the Reported Numbers

The reported numbers can be recomputed from the frozen result files without running the model. Both scripts use only the Python standard library.

```bash
python3 analyze_ablations.py      # controlled benchmark: the five configurations above
python3 generate_report.py        # writes experiment_results/vera_summary_report.txt
```

The real-world metrics are in `results/final_real_world_metrics.txt`, built from the per-candidate records in `results/final_real_world_candidates.csv` and `results/final_real_world_task_summary.csv`. To check that the authoritative result files are unchanged:

```bash
sha256sum -c reproducibility/result_hashes.sha256
```

On macOS, use `shasum -a 256 -c reproducibility/result_hashes.sha256`.

Generating new candidates requires the packages in `requirements.txt` and a local [Ollama](https://ollama.com) server with the `qwen2.5-coder:7b` model at `http://localhost:11434`. New generations will differ from the frozen candidates and must not replace them.

---

## Experimental Provenance

* The authoritative real-world runs are `20260904_164914` (Black-1, 3, 4, 7, 8, 9 and 10) and `20260904_171236` (Black-13, 14 and 16). The later run `20260904_181853` is excluded from the reported results.
* Four candidate-generation slots were requested per task. Invalid generations were recorded as failed slots and were not replaced.
* Git was initialised after the experiments. The current snapshot does not establish the exact generator revision used for the frozen runs, and the current function-level generator contains retry behaviour added afterwards. The frozen artefacts are therefore the authoritative record, and end-to-end reproduction should not be claimed until the original generation configuration is reconstructed. See [`reproducibility/FROZEN_GENERATOR_NOTES.md`](reproducibility/FROZEN_GENERATOR_NOTES.md).
* The inspected environment was macOS 15.6 on Apple Silicon, Python 3.9, Ollama 0.33.0 and `qwen2.5-coder:7b`. Exact historical versions at the time of the runs have not all been established. See [`EXPERIMENTAL_SETUP.md`](EXPERIMENTAL_SETUP.md).

---

## Limitations

* Six controlled tasks and ten defects from one project are not enough to generalise across languages, repositories or the whole of BugsInPy.
* Visible, hidden, probe and oracle tests are finite approximations of intended behaviour, not proofs of correctness.
* The controlled and real-world experiments use different acceptance rules and different behavioural information, so their results cannot separate task difficulty from verifier configuration.
* The real-world change-risk threshold is a fixed heuristic, not a calibrated probability.

---

## Privacy

Local credentials and virtual environments are excluded through `.gitignore`. No credentials are required to read the reported results.

---

## Citation

Mridula Prabhakar. *VERA-SE: Verification-Guided Autonomous Software Repair with Risk-Aware Patch Selection.* Independent research preprint, 2026. Zenodo. https://doi.org/10.5281/zenodo.23440127

```bibtex
@misc{prabhakar2026verase,
  author    = {Prabhakar, Mridula},
  title     = {VERA-SE: Verification-Guided Autonomous Software Repair with Risk-Aware Patch Selection},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.23440127},
  url       = {https://doi.org/10.5281/zenodo.23440127},
  note      = {Independent research preprint}
}
```

---

## Author

**Mridula Prabhakar** · [GitHub](https://github.com/mridulapbk08)
