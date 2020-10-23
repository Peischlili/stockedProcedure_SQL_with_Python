from packagesManager import *
from dynamicQuery import getSurveyData

# The global "controller" of all operations 
# Check if an older version of CSV structure file exists and if oldStructure equals to currentStruture
# If not exists, create a new structure csv, refresh the view and retrieve data from the view
def getSurveyStructure(connector, cursor) -> pd.DataFrame:
    query = 'SELECT * FROM [Survey_Sample_A19].[dbo].[SurveyStructure]'
    currentStructure = pd.read_sql_query(query, connector)
    fileStruc = 'survey_structure.csv'
    filePiv = 'pivot_survey_table.csv'

    # Case 1: Structure exists
    if os.path.isfile(fileStruc):
        oldStructure = pd.read_csv(fileStruc)
        if oldStructure.equals(currentStructure):
            try: 
                pd.read_csv(filePiv)
            except FileNotFoundError:
                execRefreshView(connector, cursor)
                retrieveFreshData(connector)
        else:
            currentStructure.to_csv(fileStruc, index=False)
            execRefreshView(connector, cursor)
            retrieveFreshData(connector)
    # Case 2: Structure not exists
    else:
        currentStructure.to_csv(fileStruc, index=False)
        execRefreshView(connector, cursor)
        retrieveFreshData(connector)
    return currentStructure

# Trigger to execute dynamic query, create or refresh the view
def execRefreshView(connector, cursor) :
    strSQLSurveyData_0:str = ' CREATE OR ALTER VIEW vw_AllSurveyData AS '
    strSQLSurveyData = strSQLSurveyData_0 + f"{getSurveyData(connector)}"
    cursor.execute(strSQLSurveyData)
    return strSQLSurveyData
    
# Retrieve data from view and store as CSV file
def retrieveFreshData(connector) -> pd.DataFrame:
    strQuery:str = ' SELECT * FROM vw_AllSurveyData '
    freshData = pd.read_sql_query(strQuery, connector)
    filename = 'pivot_survey_table.csv'
    freshData.to_csv(filename, index=False) 
    return freshData
