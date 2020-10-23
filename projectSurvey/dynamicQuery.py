from packagesManager import *

# getSurveyData will generate the dynamic query string to be executed when neede
def getSurveyData(connector) -> str:
	# Templates for final query
	strQueryTemplateForAnswerQuery: str = """
	 COALESCE(
		(
			SELECT a.Answer_Value
			FROM Answer as a
			WHERE
				a.UserId = u.UserId
				AND a.SurveyId = <SURVEY_ID>
				AND a.QuestionId = <QUESTION_ID>
		), -1) AS ANS_Q<QUESTION_ID> """

	strQueryTemplateForNullColumn: str = ' NULL AS ANS_Q<QUESTION_ID> '

	strQueryTemplateForOuterUnionQuery: str = """
		SELECT
				UserId
				, <SURVEY_ID> as SurveyId
				, <DYNAMIC_QUESTION_ANSWERS>
		FROM
			[User] as u
		WHERE EXISTS
		(
				SELECT *
				FROM Answer as a
				WHERE u.UserId = a.UserId
				AND a.SurveyId = <SURVEY_ID>
		) """

	strCurrentUnionQueryBlock: str = ''

	strFinalQuery: str = ''

	# Table of all surveyId's to be iterated over
	surveyQuery: str = 'SELECT SurveyId FROM Survey ORDER BY SurveyId'
	surveyQueryDF: pd.DataFrame = pd.read_sql_query(surveyQuery, connector)

	# Query to build a matching table for each surveyID: all questions and if they are included in the survey
	# If included: label 1; if not included, label 0.
	questionInSurvey: str = """
		SELECT * 
		FROM 
		(
			SELECT
				SurveyId,
				QuestionId,
				1 as InSurvey
			FROM
				SurveyStructure
			WHERE
				SurveyId = @currentSurveyId
			UNION
			SELECT 
				@currentSurveyId as SurveyId,
				Q.QuestionId,
				0 as InSurvey
			FROM
				Question as Q
			WHERE NOT EXISTS
			(
				SELECT *
				FROM SurveyStructure as S
				WHERE S.SurveyId = @currentSurveyId AND S.QuestionId = Q.QuestionId
			)
		) as t
		ORDER BY QuestionId 
	 """
	currentSurveyID:int = None
	currentQuestionId:int = None
	currentInSurvey:int = None
	strFinalQuery:str = ''
	
	surveyQuestionTable =pd.DataFrame()
	# dicSurveyQuestion stores for each survey its query string using key-value structure: SurveyID, query string
	dicSurveyQuestion = {}

	# Here starts the loop over surveys
	for rowID, row in surveyQueryDF.iterrows():
		currentSurveyID = row["SurveyId"]
		dicSurveyQuestion[currentSurveyID] = questionInSurvey.replace('@currentSurveyId', str(currentSurveyID))
		# surveyQuestionTable: survey-wise matching that we will iterate over
		surveyQuestionTable = pd.read_sql_query(dicSurveyQuestion[currentSurveyID], connector)

		# dicColumnsQuery stores for every question in a given survey its query string using key-value structure: QuestionID, query string
		dicColumnsQuery = {}
		# strColumnsQueryPart is a survey-wise compilation of all dicColumnQuery values
		strColumnsQueryPart:str = ''

		# Here is the loop over questions of each survey
		for rowID, row in surveyQuestionTable.iterrows():
			currentQuestionId = row["QuestionId"]
			currentInSurvey = row["InSurvey"]
			if currentInSurvey == 0 :
				dicColumnsQuery[currentQuestionId] = strQueryTemplateForNullColumn.replace(\
					'<QUESTION_ID>', str(currentQuestionId)) 
			else :
				dicColumnsQuery[currentQuestionId] = strQueryTemplateForAnswerQuery.replace(\
					'<QUESTION_ID>', str(currentQuestionId))
			strColumnsQueryPart = strColumnsQueryPart + dicColumnsQuery[currentQuestionId] + ' , '
		strColumnsQueryPart = strColumnsQueryPart[:-2] + ' '
		
		# Now, all the SQL for the question columns is in strColumnsQueryPart
		# We need to build the outer SQL for the current Survey, from the template
		strCurrentUnionQueryBlock:str = ''
		strCurrentUnionQueryBlock =  strQueryTemplateForOuterUnionQuery.replace('<DYNAMIC_QUESTION_ANSWERS>'\
											, strColumnsQueryPart)
		strCurrentUnionQueryBlock =  strCurrentUnionQueryBlock.replace('<SURVEY_ID>', str(currentSurveyID))

		strFinalQuery = strFinalQuery +  strCurrentUnionQueryBlock
		strFinalQuery = strFinalQuery + ' UNION ' ;
	strFinalQuery = strFinalQuery[:-6] + ' '

	return strFinalQuery

