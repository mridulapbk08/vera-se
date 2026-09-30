# VERA-SE Frozen Generator Provenance

## Authoritative real-world evaluation

The paper reports only the authoritative real-world runs:

- 20260904_164914
- 20260904_171236

The later run 20260904_181853 is excluded.

## Candidate-generation policy used for the reported evaluation

The reported experiment requested four candidate generations per task.

Invalid generations were recorded as invalid / missing candidate slots and
were not repeatedly replaced until four valid candidate patches were obtained.

Therefore:

- requested generations per task = 4
- invalid model outputs remain generation failures
- valid candidate count may be less than 4
- the paper reports both requested and valid candidate counts

This policy is reflected in the frozen experimental artifacts, which contain
40 requested generations across 10 tasks and 28 valid candidate instances.

## Current function-level generator

The current `vera/real_world_patch_generator.py` contains post-experiment
generation-retry behavior.

In the current implementation:

- `candidate_count` defaults to 4
- `max_generation_multiplier` defaults to 3
- the generator continues until either:
  - four valid patches are obtained, or
  - `candidate_count * max_generation_multiplier` generation attempts are used

Thus four requested valid candidates may cause as many as 12 model-generation
attempts.

This behavior must NOT be described as the generation policy used by the
authoritative September 4 experiments.

## Network retries versus candidate regeneration

The generator also contains HTTP/Ollama request retry logic.

Network retries are conceptually different from candidate regeneration:

- network retry: repeats a failed request caused by timeout / transport failure
- candidate regeneration: makes another model-generation attempt after an
  invalid candidate was returned

The reported frozen experiment should be described in terms of four requested
candidate-generation slots per task, with invalid candidates skipped rather
than replaced until four valid candidates were collected.

## Region generator

The currently inspected region generator still loops over exactly
`candidate_count` candidate slots.

However, because the repository was initialized after the experiments, the
current source files must not automatically be treated as exact historical
snapshots.

## Reproducibility limitation

Git history begins after the experiments were completed.

Consequently, the current repository preserves:

- frozen result artifacts
- candidate patches and diffs
- evaluation oracles
- current implementation
- documented experimental environment

but it does not establish the exact source-code revision used during the
authoritative September 4 generation runs.

The paper therefore reports the frozen artifacts as the authoritative
experimental record and explicitly discloses this provenance limitation.
