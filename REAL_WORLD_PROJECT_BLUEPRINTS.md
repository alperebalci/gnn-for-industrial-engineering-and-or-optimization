# Real-World GNN + Optimization Project Blueprints

This document contains project ideas that add a genuinely distinct optimization structure to the portfolio. It deliberately excludes ideas that are only industry relabelings of existing scheduling, resource-allocation, or generic supply-network examples.

The acceptance rule is:

> Add a project only when the graph structure changes the decision model, the GNN has a precise role, a classical baseline exists, and the downstream optimizer or simulator can verify operational value.

## 01 — Cold-Chain and Perishability-Aware Distribution Network

### Operational problem

Distribute temperature-sensitive products through plants, cold stores, cross-docks, hospitals, pharmacies, or retailers while jointly managing:

- transportation cost;
- shelf life and expiry;
- temperature exposure;
- service levels;
- capacity;
- disruption risk;
- inventory positioning.

This is stronger than a generic routing example because product condition evolves along paths and across time. The state of one shipment depends on the sequence of facilities, dwell times, temperatures, and transport legs it experiences.

### Graph representation

Use a temporal heterogeneous graph.

**Node types**

- production sites;
- cold-storage facilities;
- cross-docks;
- demand points;
- product lots / batches.

**Edge types**

- ships-to;
- transfers-through;
- replenishes;
- belongs-to-lot;
- emergency-substitution.

**Node features**

- inventory by remaining shelf-life bucket;
- storage temperature;
- storage capacity;
- demand forecast;
- refrigeration state;
- service criticality.

**Edge features**

- travel time;
- transportation cost;
- temperature-excursion probability;
- lane reliability;
- refrigerated capacity;
- delay distribution.

### GNN role

The GNN should not directly output an unconstrained shipping plan.

Useful learned outputs are:

- risk score for candidate arcs;
- expected quality degradation / usable-life loss;
- disruption-aware lane ranking;
- probability that a lot-route combination will violate a freshness or temperature threshold;
- warm-start scores for shipment and inventory decisions.

Recommended architecture:

```text
time-varying cold-chain graph
 -> temporal / relational GNN
 -> lane + lot risk scores
 -> candidate screening / warm start
 -> MILP or rolling-horizon optimizer
 -> feasible shipment and inventory plan
```

### Optimization layer

A useful MILP can include:

- multi-period inventory balance;
- FEFO allocation;
- shelf-life state transitions;
- facility and lane capacities;
- demand/service constraints;
- emergency sourcing;
- product disposal;
- optional chance / robust constraints for uncertain delays or temperature excursions.

A practical objective is:

```text
transport cost
+ holding cost
+ expiry / disposal cost
+ shortage cost
+ temperature-risk penalty
+ emergency-shipment cost
```

### MVP

Start with:

- 1 production site;
- 2–4 regional cold stores;
- 10–30 demand points;
- 2–3 product classes;
- 7–14 daily periods;
- simulated or public weather/traffic proxies;
- synthetic sensor histories generated from a transparent degradation model.

The first version does not require live IoT. A reproducible simulator is enough to test the architecture.

### Baselines

Compare against:

1. full MILP without learning;
2. rolling-horizon MILP;
3. cost-only lane pruning;
4. tabular ML risk model without graph structure;
5. GNN-assisted candidate screening / warm start.

### Evaluation

Report both prediction and decision metrics.

**Prediction**

- excursion-risk AUROC/AUPRC;
- calibration;
- top-k risky-lane recall.

**Decision**

- total landed cost;
- expired / discarded units;
- service level;
- emergency shipments;
- solver wall-clock time;
- objective gap to the full model;
- feasibility rate after screening.

The project is successful only if the GNN improves the downstream decision process relative to simpler baselines.

---

## 02 — Aerospace BOM, Qualification, and Supply-Risk Network

### Operational problem

Aerospace sourcing is not just a supplier-customer graph. A component may be usable only when the supplier, process, material source, certification route, plant, and program are jointly qualified.

The practical decision is to choose sourcing, qualification, inventory, and contingency actions under long lead times while preserving traceability and certification constraints.

### Graph representation

Use a heterogeneous graph or hypergraph.

**Node types**

- suppliers;
- manufacturing processes;
- raw materials;
- part numbers;
- subassemblies;
- final assemblies;
- plants;
- certification / qualification records;
- aircraft or product programs.

**Relations**

- supplies;
- manufactured-by;
- consumes-material;
- part-of-BOM;
- qualified-for;
- processed-at;
- approved-under;
- interchangeable-with.

Some relations are naturally higher-order. For example, a source may be valid only for a particular `supplier × process × part × plant × qualification` combination. A hypergraph or factor-graph representation can preserve that structure better than flattening it into pairwise edges.

### GNN role

Useful learned outputs include:

- disruption-propagation risk;
- critical-component ranking;
- candidate alternate-source ranking;
- qualification-success likelihood;
- likely bottleneck paths in the BOM;
- warm-start scores for sourcing and safety-stock decisions.

Recommended architecture:

```text
BOM + supplier + qualification graph
 -> heterogeneous / hypergraph GNN
 -> criticality + alternate-source scores
 -> sourcing / inventory / qualification MILP
 -> auditable contingency plan
```

The GNN may rank alternatives, but certification feasibility remains an explicit optimization constraint.

### Optimization layer

The downstream model can decide:

- supplier allocation;
- dual-sourcing activation;
- qualification projects to fund;
- strategic inventory;
- expedite actions;
- production allocation across qualified plants.

Constraints can include:

- approved-source lists;
- certification compatibility;
- lead-time windows;
- supplier and plant capacity;
- minimum order quantities;
- BOM precedence;
- program-specific traceability;
- inventory balance.

A useful objective is:

```text
procurement cost
+ qualification cost
+ inventory cost
+ expedite cost
+ expected shortage / line-stop cost
+ disruption exposure
```

### MVP

A credible first implementation can use a synthetic but structurally realistic dataset:

- 3 BOM levels;
- 100–500 parts;
- 20–50 suppliers;
- 2–4 plants;
- multiple qualification states;
- long-tailed lead times;
- single-source and dual-source components;
- simulated supplier disruptions.

The simulator should expose the true dependency structure so that cascade-risk ranking can be evaluated objectively.

### Baselines

Compare against:

1. deterministic sourcing MILP;
2. criticality ranking based on single-source status and lead time;
3. centrality-based graph heuristics;
4. tabular gradient boosting;
5. heterogeneous / hypergraph GNN + optimizer.

### Evaluation

**Prediction / ranking**

- top-k disrupted-part recall;
- alternate-source precision;
- calibration of disruption propagation risk;
- mean reciprocal rank of true critical paths.

**Decision**

- expected shortage cost;
- line-stop hours;
- qualification spend;
- inventory cost;
- recovery time;
- number of feasible alternate-source paths;
- solver time / optimality gap.

### Real-data path

A production deployment would normally integrate ERP/MRP, supplier master data, BOMs, approved-vendor lists, quality systems, lead-time histories, and certification records. The research version should avoid claiming deployability from synthetic data alone; the synthetic benchmark validates the method, not the enterprise integration.

---

## Ideas intentionally not promoted to separate projects

The following ideas are useful operational themes but are not distinct enough to justify new standalone portfolio projects at this point:

- **Automotive JIT coordinator:** substantially overlaps dynamic scheduling, routing, inventory, and disruption-control work already represented elsewhere in the portfolio.
- **Electronics manufacturing resource allocation:** overlaps production scheduling, setup sequencing, and resource-allocation repositories.
- **Generic semiconductor supply-chain optimizer:** valuable as an industry case, but methodologically close to the existing multi-echelon supply-chain + disruption framework unless a semiconductor-specific constraint set is modeled.
- **Fresh-food network optimizer:** closely related to the cold-chain/perishability project above; it is better treated as a second dataset or domain variant than as a separate method project.

This avoids multiplying repositories that differ mainly by industry labels.
