# Reproducibility package: pre-LCA sustainability-readiness screening

This public folder contains the data and calculation files needed to reproduce the arithmetic checks reported in the manuscript **A Traceable Pre-LCA Sustainability-Readiness Framework for Prototype-Scale PV, CSP, Geothermal and Waste-Heat-to-Hydrogen Pathways**.

## Files
- `scenario_summaries.csv`: archived pathway-level scenario summaries.
- `scenario_parameters.csv`: archived PV and CSP scenario/input parameters.
- `pv_cell_voltage_pairs.csv`: 288 archived PV cell-temperature / cell-voltage pairs used for the output-derived regression.
- `reproduce_screening.py`: reproduces the PV regression, PV 24-h constant-power hydrogen equivalents, stoichiometric reaction-water equivalents, and the WHR-S5 diagnostic sensitivity.
- `source_to_claim_manifest.csv`: maps each public source to its evidence class and interpretation limits.

## Scope
This package reproduces only calculations recoverable from the archived data. It does **not** reproduce the original ANSYS simulations, mesh generation, solver convergence histories, closed turbine thermodynamics, or experimental validation, because those records are not available in the archive.

## Run
Python 3 with NumPy and pandas:

```bash
python reproduce_screening.py
```

The PV regression uses ordinary least squares on 288 archived cell-level pairs with G_ref = 1000 W m^-2 and T_ref = 25 degC.
