# Import all packages and functions
from packagesManager import *
from dynamicQuery import getSurveyData
from trigger import getSurveyStructure
from trigger import execRefreshView 
from trigger import retrieveFreshData


# Connect to SQL Server
connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};\
            SERVER=yourServerName;\
            DATABASE=Survey_Sample_A19;\
            Trusted_connection=Yes;')
cursor = connection.cursor()

# Call the main function that "controls" all operations
getSurveyStructure(connection, cursor)

cursor.close()
connection.close()

