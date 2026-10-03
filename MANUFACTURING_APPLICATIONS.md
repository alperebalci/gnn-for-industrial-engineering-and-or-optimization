# Manufacturing-Focused GNN Application Blueprints

These blueprints extend the repository with manufacturing problems where graph structure is not cosmetic: operational dependencies, material flow, quality propagation, and equipment interdependence are part of the decision problem.

They are intentionally framed as **GNN-assisted decision systems**, not as claims that a neural network replaces process engineering, causal analysis, discrete-event simulation, or mathematical optimization.

## Selection rationale

Three applications are included because they add manufacturing-specific graph-learning patterns that are not already represented by the executable examples in this repository:

1. dynamic production-line bottleneck early warning;
2. quality-defect propagation and root-cause candidate ranking;
3. dependency-aware predictive maintenance and cascade-risk prioritization.

A fourth idea — integrated production planning and scheduling — is not promoted to a separate blueprint here because it overlaps substantially with the existing scheduling coverage in this repository and the dedicated [production-planning-optimization](https://github.com/jorsacademy/production-planning-optimization) repository. It becomes worth adding later only if it is implemented as a distinct solver-in-the-loop benchmark with shared-resource coupling that existing examples do not cover.

---

## 01 — Dynamic Production-Line Bottleneck Early Warning

### Manufacturing question

Which workstation, buffer, or shared resource is likely to become the next system constraint, and what intervention should be tested before throughput degrades?

Classical bottleneck analysis often uses local utilization, queue length, or cycle-time statistics. Those signals are useful, but they can miss propagation through blocking, starvation, rework loops, finite buffers, shared operators, and parallel routing.

### Graph representation

A heterogeneous directed graph can represent the line:

- **Node types:** workstations, buffers, inspection points, shared operators/tools, utilities;
- **Edge types:** material flow, precedence, blocking/starvation relation, shared-resource dependency, rework return;
- **Node features:** cycle time, queue length, utilization, downtime state, first-pass yield, WIP, recent variability;
- **Edge features:** transfer time, batch size, buffer capacity, routing probability, priority, transport availability.

For dynamic plants, use time-indexed snapshots or a temporal GNN rather than treating the graph as static.

### Learning target

Useful targets include:

- probability that a node becomes the active bottleneck in the next horizon;
- expected queue growth;
- expected throughput loss attributable to the local region;
- ranking of candidate intervention locations.

A classification target alone is insufficient. The benchmark should also measure whether acting on the prediction improves the production objective.

### Decision layer

A safe architecture is:

```text
shop-floor state
 -> temporal / heterogeneous GNN
 -> bottleneck-risk scores
 -> candidate intervention set
 -> discrete-event simulation or optimizer
 -> validated action
```

Candidate interventions can include:

- temporary labor reassignment;
- alternate routing;
- buffer policy change;
- maintenance timing adjustment;
- sequence or release-rate adjustment.

The GNN should rank where to look; simulation or optimization should evaluate what to do.

### Objective

A manufacturing decision model may minimize a weighted objective such as:

```text
cycle time
+ WIP holding cost
+ blocking/starvation loss
+ changeover cost
+ intervention cost
```

subject to capacity, precedence, buffer, labor, routing, and quality constraints.

### Synthetic benchmark design

A credible synthetic demonstrator should be generated from a discrete-event model rather than from independent random tables.

Recommended scenario elements:

- serial and parallel stations;
- finite buffers;
- stochastic processing times;
- planned and unplanned downtime;
- rework loops;
- shared operators or tools;
- demand or product-mix changes.

The benchmark should create train/test splits by **scenario regime or time block**, not by randomly shuffling highly autocorrelated state snapshots.

### Evaluation

Report:

- bottleneck top-k recall;
- horizon-specific precision/recall;
- calibration of risk scores;
- throughput and cycle-time impact after the downstream intervention policy;
- false-alarm rate;
- robustness under product-mix, downtime, and cycle-time distribution shift.

The strongest baseline is not merely a generic MLP. Include classical bottleneck indicators such as utilization, queue length, active-period percentage, and shifting-bottleneck heuristics.

---

## 02 — Quality-Defect Propagation and Root-Cause Candidate Ranking

### Manufacturing question

When a downstream defect is detected, which upstream process steps, parameter deviations, material states, or equipment conditions are the most plausible contributors?

A multi-stage process naturally forms a dependency graph. A GNN can exploit that structure to learn how abnormal states co-occur and propagate through the manufacturing sequence.

### Important causal caveat

A predictive GNN can rank **root-cause candidates**, but observational association is not automatically causal attribution.

A statement such as “Step 2 caused the defect at Step 7” requires stronger evidence: controlled experiments, process knowledge, valid causal assumptions, interventions, or another identification strategy.

Therefore the default output of this blueprint is:

> **candidate cause ranking with evidence paths**, not automatic causal proof.

### Graph representation

Possible graph designs include a process graph or a heterogeneous process-product graph.

- **Node types:** operations, machines, batches/lots, product states, inspection points;
- **Edge types:** product flow, precedence, machine usage, material genealogy, rework, parameter dependency;
- **Node features:** temperature, pressure, feed/speed, torque, tool wear, operator or recipe state, quality measurements;
- **Edge features:** elapsed time, material transfer state, batch/lot relation, route, transport or hold duration.

For genealogy-sensitive manufacturing, a heterogeneous graph linking lots, process steps, and assets is usually more informative than a graph of operations alone.

### Learning targets

Examples:

- downstream defect probability;
- defect class;
- process-step contribution/risk score;
- anomalous-path score;
- candidate upstream node ranking conditioned on the observed defect.

Explainability outputs can show high-scoring paths, but they should be described as **model evidence paths**, not automatically as causal mechanisms.

### Decision layer

A useful operational pattern is:

```text
process + genealogy graph
 -> GNN / temporal GNN
 -> defect risk + upstream candidate scores
 -> engineer review / DOE / targeted inspection
 -> process adjustment
```

This makes the GNN a screening and prioritization layer for quality engineering.

### Objective

Operational evaluation can combine:

```text
scrap cost
+ rework cost
+ investigation time
+ additional inspection cost
+ missed-defect cost
```

with first-pass yield and escape-rate metrics reported separately.

### Benchmark design

A synthetic benchmark should include:

- multi-stage routings;
- latent process drift;
- correlated sensor changes;
- tool-wear progression;
- batch/lot effects;
- delayed quality labels;
- occasional rework;
- injected faults whose true origin is known to the simulator.

The simulator's known injected fault origin creates a ground-truth evaluation channel for root-cause candidate ranking. This is preferable to claiming causal validity from an observational classifier.

### Evaluation

Report:

- AUROC/AUPRC for rare defects;
- top-k root-cause candidate recall;
- mean reciprocal rank of the injected source;
- time-to-detection;
- false investigation rate;
- performance under new recipes, machines, or operating regimes.

Compare against:

- SPC / rule-based alarms;
- gradient-boosted tabular models;
- temporal models without graph structure;
- ablations that remove genealogy or dependency edges.

For real-data extensions, the [Industry 4.0 Lab](https://github.com/jorsacademy/industry-4.0-lab) is the natural portfolio location for dataset-specific implementations.

---

## 03 — Dependency-Aware Predictive Maintenance and Cascade-Risk Prioritization

### Manufacturing question

Which asset should be maintained first when equipment health, production criticality, shared utilities, and downstream cascade risk are considered jointly?

Independent-machine predictive maintenance can estimate failure risk well while still making a poor system-level maintenance decision. A nominally healthy compressor, pump, transformer, robot controller, or utility asset may be critical because several production resources depend on it.

### Graph representation

Use a multi-relational asset graph:

- **Node types:** machines, subsystems, utility assets, production cells, buffers;
- **Edge types:** mechanical coupling, electrical supply, pneumatic/hydraulic supply, cooling, process dependency, redundancy/failover;
- **Node features:** vibration, temperature, pressure, current, load, age, usage, alarm history, estimated health state;
- **Edge features:** load transfer, dependency strength, shared-capacity fraction, redundancy, isolation capability.

The graph may change over time as routing, operating mode, redundancy, or production assignments change. Temporal or dynamic graph models are therefore preferable for nontrivial plants.

### Learning targets

Possible outputs include:

- node-level failure hazard;
- remaining-useful-life distribution;
- probability of downstream disruption conditional on a node failure;
- cascade-risk score;
- maintenance-priority score.

The last item should generally be produced together with an explicit scheduling/optimization model rather than learned as an unconstrained end-to-end action.

### Decision layer

Recommended architecture:

```text
sensor + maintenance + dependency graph
 -> temporal GNN
 -> failure / cascade-risk estimates
 -> maintenance optimization model
 -> feasible maintenance schedule
```

The optimizer can account for:

- crew availability;
- spare parts;
- production windows;
- simultaneous-maintenance restrictions;
- redundancy requirements;
- due maintenance;
- expected downtime cost.

This preserves feasibility and makes the graph model responsible for prediction, not constraint enforcement.

### Objective

A system-level model may minimize:

```text
expected unplanned downtime cost
+ planned maintenance cost
+ production-loss cost
+ cascade-risk penalty
+ overtime / spare-part cost
```

subject to crew, parts, timing, safety, and production constraints.

OEE can be reported as an operational KPI, but it is better treated as a resulting metric than as a single undifferentiated optimization objective.

### Synthetic benchmark design

A useful simulator should contain:

- asset health degradation;
- common-cause utility dependencies;
- redundant and nonredundant branches;
- load-dependent degradation;
- stochastic failure;
- imperfect sensors;
- maintenance restoration;
- production criticality that changes with the schedule.

This makes it possible to test whether graph-aware prediction improves system-level decisions over independent asset models.

### Evaluation

Report both predictive and decision metrics:

**Predictive**

- time-dependent AUROC/AUPRC;
- calibration / Brier score;
- RUL error where applicable;
- cascade-event recall.

**Decision**

- expected downtime;
- missed critical failures;
- maintenance cost;
- production loss;
- schedule feasibility;
- value relative to independent-machine risk ranking.

Dataset-specific maintenance implementations belong naturally in the [Industry 4.0 Lab](https://github.com/jorsacademy/industry-4.0-lab), while this repository should focus on the graph-learning and optimization architecture.

---

## Shared implementation stack

A lean research stack is sufficient:

```text
Python
PyTorch
PyTorch Geometric
NetworkX
NumPy / pandas
SimPy or another discrete-event simulator where needed
OR-Tools / Pyomo / SCIP / Gurobi for the decision layer
```

FastAPI, React, or D3.js can be useful for a public demo, but they are not required to validate the research contribution. The first implementation priority should be a reproducible benchmark, strong baselines, solver/simulation integration, and tests.

## Minimum engineering standard for adding executable examples

A manufacturing GNN example should not enter the main executable sequence until it has:

1. an explicit graph schema;
2. a reproducible data generator or legally usable real dataset;
3. a non-GNN operational baseline;
4. a graph-agnostic ML baseline;
5. leakage-safe train/validation/test splits;
6. decision-level metrics in addition to predictive metrics;
7. ablations showing whether the graph edges add value;
8. a downstream simulator or optimizer when the task recommends an action;
9. fixed seeds and automated tests;
10. no unsupported ROI or throughput claims.

This keeps the manufacturing examples aligned with the repository's central principle:

```text
learn structural signal
        ↓
rank / predict / screen
        ↓
simulate, repair, or optimize
        ↓
produce a feasible and auditable decision
```
