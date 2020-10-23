# Project: Stocked Procedure SQL with Python

## Scale
Purpose of this project is to have programmatic access to SQLServer database via codes developed with Python3.

### SQL components implemented by Python3
* Dynamic query that generates pivot table upon several tables
* Trigger implemented over SurveyStructure
* View created or altered when the trigger fires
* Simple query requested on the "fresh" view


## Details on python files
### packagesManager.py
It installs and imports all necessary python libraries for the project before excecuting any code so that user does not need to manage it.

### main.py
It manages connection to the SQLServer of user and executes functions in dynamicQuery.py and trigger.py.

### dynamicQuery.py
This is the core of the project and translate SQL dynamic query characteristics into Python, including replicating SQL features unavailable in Python such as cursors.
It prepares dynamic query string to be called and executed in SQL. 

### trigger.py
It is the 'controller' all SQL operations. It follows the following logic:
* A persistence component (csv file), storing the last known surveys’ structures is in place.
* Each time the code is executed (in main), request on SQLServer and compare the actual structure with the lastest one (csv file).
  * If no changes, do not trigger a new view.
  * In case of any change on INSERT, DELETE and UPDATE upon the table dbo.SurveyStructure, trigger a new view and retrieve data from the new view, then store information in a csv file. 


