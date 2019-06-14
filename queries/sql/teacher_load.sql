SELECT DISTINCT
 Persons.F$FIO AS Person_FIO
, Persons.F$strtabn AS OneCId
	, postList.f$code AS Person_PositionID
	, Dept.f$code AS Person_DepartmentId
	, LoadPersons.f$WYEARED AS Person_Year
	, CONVERT(VARCHAR(512), convert(BigInt, LoadPersons.F$NREC)-convert(bigInt,0x8000000000000000)) as Load_ID
	, tload.f$wmin AS Load_Min
	, tload.f$wmax AS Load_Max
, LoadPersons.f$dload AS load_plan
	, LoadPersons.f$dfactload AS load_fact
	, tLoad.f$MinAud AS load_AudMin
, tLoad.f$MaxAud AS load_AudMax
	, COALESCE(taudload.audload,0) AS load_AudLoad
	, app.F$RATE AS load_Rate
	, tload.f$NormHour*app.F$RATE AS load_StaffLoad
	, LoadPersons.f$dload-tload.f$NormHour*app.F$RATE AS load_Shift
	, CONVERT(VARCHAR(512), COALESCE(CONVERT(BIGINT,loadRow.F$NREC)- CONVERT(BIGINT,0x8000000000000000),' ')) AS loadRow_id
	, CASE WHEN loadRow.f$WTYPELOAD=0 THEN 'main' ELSE CASE WHEN loadRow.f$WTYPELOAD=1 THEN 'ext' ELSE ' ' END END AS loadRow_type
	, CONVERT(VARCHAR(512), COALESCE(CONVERT(BIGINT,tsubject.F$NREC)- CONVERT(BIGINT,0x8000000000000000),' ')) AS Subject_id
	, COALESCE(tsubject.F$NAME,' ') AS Subject_Name
	, COALESCE(loadRow.f$wCourse,' ') AS Course
	, COALESCE(loadRow.f$Semester, ' ') AS Semester
	, CONVERT(VARCHAR(512), COALESCE(CONVERT(BIGINT,typework.F$NREC)- CONVERT(BIGINT,0x8000000000000000),' ')) AS JobType_id
, COALESCE(typework.F$NAME,' ') AS JobType_Name
	, CONVERT(VARCHAR(512), COALESCE(CONVERT(BIGINT,Kontingent.F$NREC)- CONVERT(BIGINT,0x8000000000000000),' ')) AS Kontingent_id
, COALESCE(Kontingent.F$NAME,' ') AS Kontingent_KontName
	, COALESCE(lectLoad.F$DCONTCOUNT, ' ') AS Kontingent_Count
	, COALESCE(lectLoad.F$istudcount, ' ') AS Kontingent_StudentsCount
	, COALESCE(lectLoad.F$dsize, ' ') AS Volume_Value
	, COALESCE(lectLoad.F$dcredsize, ' ') AS Volume_Zet
	, COALESCE(lectLoad.F$dload, ' ') AS LoadValue_Value
	, COALESCE(lectLoad.F$dfactload, ' ') AS LoadValue_Fact
	, COALESCE(lectLoad.F$dcredload, ' ') AS LoadValue_Zet
	, COALESCE(lectLoad.f$numteachstaff, 0) AS Rate
	, CONVERT(VARCHAR(512), COALESCE(CONVERT(BIGINT,groups.F$NREC)- CONVERT(BIGINT,0x8000000000000000),' ')) AS Group_id
, COALESCE(groups.F$NAME,' ') AS Group_Name
FROM T$U_TEACHINGLOAD LoadPersons
INNER JOIN t$U_Lecture U_Lecture ON (U_Lecture.F$NREC=LoadPersons.F$CLECTURE)
INNER JOIN t$Persons Persons ON (Persons.F$NREC=U_Lecture.F$CPERSONS)
LEFT OUTER JOIN T$CATALOGS postList ON (postList.f$nrec=U_Lecture.F$CPOST)
LEFT OUTER JOIN T$CATALOGS Dept ON (Dept.f$nrec=U_Lecture.F$CCHAIR)
LEFT OUTER JOIN t$U_NormLoad tload ON (tload.f$WYEARED=LoadPersons.f$WYEARED AND tload.F$CPOST=postList.F$NREC AND tload.F$CATEGORY=U_Lecture.F$CATEGORY)
LEFT OUTER JOIN (
SELECT PrnLectLoad.f$cVariant, PrnLectLoad.f$wYearEd, PrnLectLoad.f$cLecture
, SUM(PrnLectLoad.f$DLOAD) AS audload
FROM t$U_LectureLoad PrnLectLoad
JOIN t$U_DisciplineLoad PrnDiscipLoad ON (PrnDiscipLoad.F$NREC=PrnLectLoad.F$cDiscipLoad)
JOIN t$U_TYPEWORK tw ON (tw.F$NREC=PrnDiscipLoad.f$ctypework AND [dbo].bitand(tw.f$wTypeMask,2)>0)
GROUP BY PrnLectLoad.f$cVariant, PrnLectLoad.f$wYearEd, PrnLectLoad.f$cLecture) taudload ON (taudload.f$cVariant = LoadPersons.f$cVariant AND
					 taudload.f$wYearEd = LoadPersons.f$wYearEd AND
																												 taudload.f$cLecture = LoadPersons.f$cLecture)
LEFT OUTER JOIN t$appointments app ON (app.f$nrec=U_Lecture.f$capp)
LEFT OUTER JOIN T$U_LECTURELOAD lectLoad ON (lectLoad.f$cVariant = LoadPersons.f$cVariant AND lectLoad.f$wYearEd = LoadPersons.f$wYearEd AND lectLoad.f$cLecture = LoadPersons.f$cLecture)
LEFT OUTER JOIN t$U_DISCIPLINELOAD loadRow ON (loadRow.f$nrec=lectLoad.f$cDiscipLoad)
LEFT OUTER JOIN T$U_DISCIPLINE tsubject ON (tsubject.F$NREC=loadrow.f$CDISCIPLINE)
LEFT OUTER JOIN t$U_TYPEWORK typework ON (TYPEWORK.f$nrec=loadRow.f$CTYPEWORK)
LEFT OUTER JOIN T$U_CONTINGENT Kontingent ON (Kontingent.f$nrec=loadRow.F$CCONTINGENT)
LEFT OUTER JOIN t$U_GroupLoad grload ON (grload.f$cLectLoadID=lectLoad.f$nrec)
LEFT OUTER JOIN t$u_studgroup groups ON (groups.F$NREC=grload.F$CSTGR)
