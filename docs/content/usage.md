# Usage

## Input: user-defined scenarios: 
Download the [input data template - user_input_template.xlsm](https://github.com/alexrob18/elec_lca/blob/main/data/user_input_template.xlsm) 
Follow the instruction on README sheet, user can either 
- explore a case study on Canada Energy Future scenarios
- define own locations, scenarios, and periods to be supplied to the model 

## Model overwrites the ecoinvent database: 

## Output: 
The transformed database will be stored in several ways: 
- as a brightway2 datapackage 
- as a wurst datapackage 
- as a sparse matrix and arrays (storing changed electricity market for each location, scenario, periods) to be used for speeding up LCA calculation

## Interactive plots
Users can explore the interactive plots built for a case study on [Canada Energy Future scenarios](https://github.com/alexrob18/elec_lca)