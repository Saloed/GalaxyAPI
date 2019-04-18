SELECT CONVERT(VARCHAR(512), CONVERT(BIGINT,U_CURRIC.F$NREC)- CONVERT(BIGINT,0x8000000000000000)) AS ID
,U_CURRIC.f$Regnum AS RegNum
,U_CURRIC.f$Name AS name
,'' AS deletion_mark
,U_CURRIC.f$WFORMED AS EduFormID
,U_CURRIC.f$YearEd AS YearEd
,U_Curric.f$wmonth+12*(ROUND(U_curric.F$TERM,0,1) + CASE WHEN U_Curric.f$wmonth = 0 THEN CASE WHEN U_curric.F$TERM>0.5 AND ROUND(U_curric.F$TERM,0,1)<>U_curric.F$TERM THEN 1 ELSE 0 END ELSE CASE WHEN ROUND(U_curric.F$TERM,0,1)>0 AND ROUND(U_curric.F$TERM,0,1)=U_curric.F$TERM THEN -1 ELSE 0 END END) AS StudyTime
,otQualific.F$NAME AS EduQual
, CONVERT(VARCHAR(512), CONVERT(BIGINT,otQualific.F$NREC)- CONVERT(BIGINT,0x8000000000000000)) AS EduQual_ID
,slevel.name AS EduLevel
,U_CURRIC.f$WDEGREE AS EduLevel_ID
,CatSpec.F$NAME AS EduDirection
, CONVERT(VARCHAR(512), CONVERT(BIGINT,U_CURRIC.f$cSpeciality)- CONVERT(BIGINT,0x8000000000000000)) AS EduDirection_ID
,CatSpec.F$CODE AS EduDirection_CODE
,SpecZ.F$NAME AS EduProfile
, CONVERT(VARCHAR(512), CONVERT(BIGINT,U_CURRIC.f$cSpecialization)- CONVERT(BIGINT,0x8000000000000000)) AS EduProfile_ID
,OTFACULTY.F$NAME AS EduDepartment
, CONVERT(VARCHAR(512), CONVERT(BIGINT,U_CURRIC.f$cFaculty)- CONVERT(BIGINT,0x8000000000000000)) AS EduDepartment_ID
FROM t$U_Curriculum U_CURRIC
LEFT OUTER
JOIN t$Catalogs CatSpec ON CatSpec.F$NREC = U_CURRIC.f$cSpeciality
LEFT OUTER
JOIN T$U_SPECIALIZATION SpecZ ON SpecZ.F$NREC = U_CURRIC.f$cSpecialization
LEFT OUTER
JOIN t$Catalogs otFaculty ON otFaculty.F$NREC = U_CURRIC.f$cFaculty
LEFT OUTER
JOIN t$Catalogs otQualific ON otQualific.F$NREC = U_CURRIC.f$cQualification
LEFT OUTER
JOIN (
SELECT 0 AS ID, 'Специалист' AS name UNION ALL
SELECT 1, 'Бакалавр' UNION ALL
SELECT 2, 'Магистр' UNION ALL
SELECT 3, 'Базовый уровень' UNION ALL
SELECT 4, 'Повышенный уровень' UNION ALL
SELECT 5, 'Аспирант' UNION ALL
SELECT 6, 'Соискатель' UNION ALL
SELECT 7, 'Прикладной бакалавр' UNION ALL
SELECT 8, 'Интернатура' UNION ALL
SELECT 9, 'Ординатура' UNION ALL
SELECT 11, 'Подготовительное отделение' UNION ALL
SELECT 12, 'Повышение квалификации') sLevel ON (slevel.id=u_curric.f$wdegree)
WHERE U_CURRIC.F$WTYPE=1
