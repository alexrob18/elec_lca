# Usage

## Input: user-defined scenarios
Download the [input data template - user_input_template.xlsm](https://github.com/alexrob18/elec_lca/blob/main/data/user_input_template.xlsm) 
Follow the instruction on README sheet, user can either 
- explore a case study on Canada Energy Future scenarios
- define own locations, scenarios, and periods to be supplied to the model 

## Model: overwrites the ecoinvent database
Using the [wurst package](https://github.com/polca/wurst/tree/main/wurst), and its key functions, e.g., [Transformations, Unlinking and Re-linking](https://wurst.readthedocs.io/index.html), 
the model essentially transform the whole background database once the user defines new electricity production technologies for the locations, scenario(s), periods (the electricity market), by: 
1. overwrite the current electricity production technology share feed into the grid electricity for the defined location
2. create new datasets for any new electricity production pathways that does not exist for the defined location
3. relinking the new electricity back to all datasets that consumes the electricity
4. export the new transformed database


## Output: 
The transformed database will be stored in several ways: 
- as a brightway2 datapackage 
- as a wurst datapackage 
- as a sparse technosphere matrix and additional_elec_arrays to be used for speeding up LCA calculation

## Interactive plots
Users can explore the interactive plots built for a case study on [Canada Energy Future scenarios](https://github.com/alexrob18/elec_lca) 


## Glossary
- <b>locations</b>: the locations are those defined in [ecoinvent locations](https://geography.ecoinvent.org/), users cannot add in a new electricity market for a new location that does not exist in ecoinvent, a total of 265 locations are available per ecoinvent v3.9.1
- <b>scenarios</b>: projections of different development pathways, the case study showcases two scenarios (Business as Usual (BAU) vs. Net-zero 2050) 
- <b>sparse technosphere matrix</b>:  a sparse matrix (known as technology A matrix) in LCA calculation, more about [matrix in LCA](https://github.com/Depart-de-Sentier/Spring-School-2024/blob/main/class-materials/brightway-basics/2%20-%20Building%20and%20using%20matrices%20in%20bw2calc.ipynb)
- <b>additional_elec_arrays</b>: storing changed electricity market for each location, scenario, periods, speeding up the LCA calculation without changing the technosphere matrix