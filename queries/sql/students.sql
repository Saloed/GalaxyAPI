SELECT DISTINCT
 [dbo].date2str('%dd.%MM.%yyyy',UStudent.f$Atl_LastDate)+' '+[dbo].time2str('%HH:%mm:%SS',UStudent.f$Atl_LastTime) AS Modified
, '' AS DeletionMark
, CONVERT(VARCHAR(512),UStudent.f$nrec,1) AS ID
, CONVERT(VARCHAR(512), CONVERT(BIGINT,UStudent.f$nrec)- CONVERT(BIGINT,0x8000000000000000)) AS NREC
, CONVERT(VARCHAR(512), CONVERT(BIGINT,UStudent.f$cPersons)- CONVERT(BIGINT,0x8000000000000000)) AS Persnrec
, UStudent.f$UNS AS UID
, UStudent.f$FIO AS FullName
, UStudent.f$SSTATUS AS STATUS
, COALESCE(CONVERT(VARCHAR(512), CONVERT(BIGINT,UStudent.f$CSTATUS)- CONVERT(BIGINT,0x8000000000000000)),'') AS Status_ID
, COALESCE(Cat_Status.f$Code,' ') AS Status_IDS
, COALESCE(Cat_Faculty.f$Name,' ') AS Department
, COALESCE(CONVERT(VARCHAR(512), CONVERT(BIGINT,Cat_Faculty.f$Nrec)- CONVERT(BIGINT,0x8000000000000000)),'') AS Department_ID
, COALESCE(Cat_Faculty.f$CODE,' ') AS Department_IDS
, COALESCE(Cat_Faculty.f$CATDATA,' ') AS Department_Short
, COALESCE(Cat_Speciality.f$Name,' ') AS EduDirection
, COALESCE(CONVERT(VARCHAR(512), CONVERT(BIGINT,Cat_Speciality.f$Nrec)- CONVERT(BIGINT,0x8000000000000000)),'') AS EduDirection_ID
, COALESCE(Cat_Speciality.f$Code,' ') AS EduDirection_CODE
, COALESCE(t$U_Specialization.f$Name,' ') AS EduProfile
, COALESCE(CONVERT(VARCHAR(512), CONVERT(BIGINT,t$U_Specialization.f$Nrec)- CONVERT(BIGINT,0x8000000000000000)),'') AS EduProfile_ID
, COALESCE(sLevel.Name,' ') as EduLevel
, COALESCE(sLevel.ID,' ') as EduLevel_ID
, COALESCE(Qualification.f$Name,' ')  as  EduQual
, COALESCE(CONVERT(VARCHAR(512), convert(BigInt,Qualification.f$Nrec)-convert(bigInt,0x8000000000000000)),'') as  EduQual_ID
, ' ' AS StudyForm
, UStudent.f$WFORMED AS StudyForm_ID
, UStudent.f$WCOURSE AS StYear
, UStudent.F$WARCH AS baza
, [dbo].date2str('%dd.%MM.%yyyy', COALESCE(t$Persons.f$AppDate, NULL)) AS AppDate
, ' ' AS AdmissionYear
, COALESCE(t$U_SUBGROUP.f$NUMBER,' ') AS Group_Name
, COALESCE(CONVERT(VARCHAR(512), CONVERT(BIGINT,UStudent.f$cStGr)- CONVERT(BIGINT,0x8000000000000000)),'') AS Group_ID
, COALESCE(t$U_SUBGROUP.f$NUMBER,' ') AS SubGroup
, COALESCE(CONVERT(VARCHAR(512), CONVERT(BIGINT,t$U_SUBGROUP.f$Nrec)- CONVERT(BIGINT,0x8000000000000000)),'') AS SubGroup_ID
, [dbo].date2str('%dd.%MM.%yyyy', COALESCE(t$Persons.f$DisDate, NULL)) AS DisDate
, COALESCE(CONVERT(VARCHAR(512), CONVERT(BIGINT,t$StaffStruct.f$cStr)- CONVERT(BIGINT,0x8000000000000000)),'') AS BUPNREC
, COALESCE(CONVERT(VARCHAR(512), CONVERT(BIGINT,t$Appointments.f$cDopInf)- CONVERT(BIGINT,0x8000000000000000)),'') AS RUPNREC
, [dbo].date2str('%dd.%MM.%yyyy', COALESCE(t$Persons.f$BornDate, NULL)) AS Borndate
, COALESCE(t$Persons.f$Sex,'') AS Sex
, COALESCE(Cat_EduType.f$Name,'') AS Edu_type
, COALESCE(Cat_Localiz.f$Name,'') AS Localiz
, COALESCE(CONVERT(VARCHAR(512), CONVERT(BIGINT,Cat_Localiz.f$Nrec)- CONVERT(BIGINT,0x8000000000000000)),'') AS Localiz_ID
, COALESCE(Cat_Gr.f$code,'') AS Gr_ID
, COALESCE(Cat_Gr.f$Name,'') AS Gr
, COALESCE(t$Spkau.f$Name,'') AS FIN
, COALESCE(CONVERT(VARCHAR(512), CONVERT(BIGINT,t$Spkau.f$Nrec)- CONVERT(BIGINT,0x8000000000000000)),'') AS FIN_ID
, t$Spkau.f$Code AS FIN_Code
, (CASE WHEN T$APPHIST.f$Coef1 = 0 THEN 'False' ELSE 'True' END) AS USL
, COALESCE(CONVERT(VARCHAR(512), CONVERT(BIGINT,BUPFIRST.f$Nrec)- CONVERT(BIGINT,0x8000000000000000)),'') AS ADMISSIONBUPNREC
, COALESCE(CONVERT(VARCHAR(512), CONVERT(BIGINT,RUPFIRST.f$Nrec)- CONVERT(BIGINT,0x8000000000000000)),'') AS ADMISSIONRUPNREC
, (CASE WHEN Cont52.F$NREC>0 THEN 'True' ELSE 'False' END) AS IsFromOtherVuz
,(CASE WHEN (tempfin.F$ABBR = t$Spkau.F$CODE AND tempfin.F$Code = t$Spkau.F$LevelCODE) THEN 'True' ELSE 'False' END) AS IsCp
, SUBSTRING(UStudent.f$Fio,0,charindex(' ',UStudent.f$Fio)) AS LastName
, SUBSTRING(SUBSTRING(UStudent.f$Fio,charindex(' ',UStudent.f$Fio)+1,len(UStudent.f$Fio)),0,charindex(' ', SUBSTRING(UStudent.f$Fio,charindex(' ',UStudent.f$Fio)+1,len(UStudent.f$Fio)))) AS FirstName
, SUBSTRING(SUBSTRING(UStudent.f$Fio,charindex(' ',UStudent.f$Fio)+1,len(UStudent.f$Fio)),charindex(' ', SUBSTRING(UStudent.f$Fio,charindex(' ',UStudent.f$Fio)+1,len(UStudent.f$Fio))),len(SUBSTRING(UStudent.f$Fio,charindex(' ',UStudent.f$Fio)+1,len(UStudent.f$Fio)))) AS PatrName
, CatPassp.f$Name AS IdentityDoc
, COALESCE(CONVERT(VARCHAR(512), CONVERT(BIGINT,t$Passports.f$Nrec)- CONVERT(BIGINT,0x8000000000000000)),'') AS Passp_Id
, t$Passports.f$Ser AS DocSerie
, t$Passports.f$NMB AS DocNumber
, t$Passports.f$GIVENDATE AS DocDate
, t$Passports.f$GIVENBy AS DocOrg
, t$Passports.f$GIVENPodr AS DocCodeOrg
, BornVal.f$vString AS BirthPlace
, (
    SELECT top 1 f$email
    FROM t$communications COMEmail
    WHERE COMEmail.f$person = t$persons.f$nrec AND COMEmail.f$ObjType = 3 AND COMEmail.f$seqnmb = 1
) AS email
, (
    SELECT top 1 f$addr
    FROM t$communications COMPhone
    WHERE COMPhone.f$person = t$persons.f$nrec AND COMPhone.f$ObjType = 2 AND COMPhone.f$seqnmb = 1
) AS phone
, 'true' AS IsPersonalDataAgreement
, PINN.f$Ser+PINN.f$NMB AS INN
, PSnils.f$Ser+PSnils.f$NMB AS SNILS
, INVALIDGRPCAT.f$Name AS invalid
, t$Persons.f$wPrizn2 AS sirota
FROM T$U_STUDENT UStudent
INNER JOIN t$Persons ON t$Persons.f$NRec = UStudent.f$cPersons
LEFT OUTER JOIN t$Catalogs Cat_Status ON Cat_Status.f$NRec = UStudent.f$CSTATUS
LEFT OUTER JOIN t$Catalogs Cat_Faculty ON Cat_Faculty.f$NRec = UStudent.f$cFaculty
LEFT OUTER JOIN t$Catalogs Cat_Speciality ON Cat_Speciality.f$NRec = UStudent.f$CPOST
LEFT OUTER JOIN t$Appointments MainAppoint ON MainAppoint.f$Nrec = CASE WHEN COALESCE(t$PERSONS.f$AppointCUR,0)<>0 THEN t$PERSONS.f$AppointCUR ELSE t$PERSONS.f$AppointLAST END
LEFT OUTER JOIN (select 0 as ID, 'Специалист' as name
                    union all select 1, 'Бакалавр'
                    union all select 2, 'Магистр'
                    union all select 3, 'Базовый уровень'
                    union all select 4, 'Повышенный уровень'
                    union all select 5, 'Аспирант'
                    union all select 6, 'Соискатель'
                    union all select 7, 'Прикладной бакалавр'
                    union all select 8, 'Интернатура'
                    union all select 9, 'Ординатура'
                    union all select 11, 'Подготовительное отделение'
                    union all select 12, 'Повышение квалификации') sLevel on (slevel.id=MainAppoint.f$FilialNo)
LEFT OUTER JOIN t$U_Specialization ON t$U_Specialization.f$nrec =MainAppoint.f$PostAccord
LEFT OUTER JOIN t$Catalogs Qualification ON Qualification.f$NRec = UStudent.f$cQualification
LEFT OUTER JOIN t$U_StudGroup ON t$U_StudGroup.f$NRec = UStudent.f$cStGr
LEFT OUTER JOIN t$U_SUBGRSTUD ON t$U_SUBGRSTUD.f$cStudent = UStudent.f$cPersons
LEFT OUTER JOIN t$U_SUBGROUP ON t$U_SUBGROUP.f$NRec = t$U_SUBGRSTUD.f$CSUBGR
LEFT OUTER JOIN t$Appointments ON t$Appointments.f$NRec = CASE WHEN t$Persons.f$AppointCur>0 THEN t$Persons.f$AppointCur ELSE t$Persons.f$AppointLast END
LEFT OUTER JOIN t$StaffStruct ON t$StaffStruct.f$NRec = t$Appointments.f$StaffStr
LEFT OUTER JOIN t$U_Curriculum ON t$U_Curriculum.f$Nrec = t$StaffStruct.f$cStr
LEFT OUTER JOIN t$Catalogs Cat_EduType ON Cat_EduType.f$Nrec = t$U_Curriculum.f$cBaseEducation
LEFT OUTER JOIN t$Catalogs Cat_Localiz ON Cat_Localiz.f$Nrec = Ustudent.f$cForeignCat
LEFT OUTER JOIN t$Catalogs Cat_Gr ON Cat_Gr.f$Nrec = t$Persons.f$Gr
LEFT OUTER JOIN t$Spkau ON t$SpKau.f$Nrec = UStudent.F$CFINSOURCENAME
LEFT OUTER JOIN T$APPHIST ON T$APPHIST.f$cAppoint = t$Appointments.f$NRec
LEFT OUTER JOIN t$Appointments AppFirst ON AppFirst.f$nrec = t$Persons.f$AppointFirst
LEFT OUTER JOIN t$StaffStruct StaffFirst ON StaffFirst.f$NRec = AppFirst.f$StaffStr
LEFT OUTER JOIN t$U_Curriculum BUPFIRST ON BUPFIRST.f$Nrec = StaffFirst.f$cStr
LEFT OUTER JOIN t$U_Curriculum RUPFIRST ON RUPFIRST.f$cParent = BupFirst.f$nRec AND RUPFIRST.f$COURSE = 1
LEFT OUTER JOIN t$tunedef tunefin ON tunefin.f$code = 'UUP.LOAD.FINSRCGROUPS.TARGETBUDGET'
LEFT OUTER JOIN t$tuneval tunefinval ON tunefinval.f$cTune = tunefin.f$nrec
LEFT OUTER JOIN t$U_DISLOADFINSRCGR tempfin ON tempfin.F$NREC = tunefinval.F$COMPVAL
LEFT OUTER JOIN T$CONTDOC Cont52 ON Cont52.f$Person = t$Persons.f$nrec AND Cont52.f$typeOper = 30052
LEFT OUTER JOIN t$Passports ON t$Passports.f$nREc = t$Persons.f$PasspRus
LEFT OUTER JOIN t$Catalogs CatPassp ON CatPassp.f$nRec = t$Passports.f$DocName
LEFT OUTER JOIN T$ATTRVAL BornVal ON BornVal.f$cRec = t$Persons.F$NREC AND BornVal.f$cAttrNam =
(
    SELECT top 1 BornNam.f$nrec
    FROM t$AttrNam BornNam
    WHERE BornNam.f$Name = 'Место рождения'
)
LEFT OUTER JOIN t$Passports PINN ON PINN.f$Person = t$Persons.f$nRec AND PINN.f$SysCode = 505
LEFT OUTER JOIN t$Passports PSnils ON PSnils.f$Person = t$Persons.f$nRec AND PSnils.f$SysCode = 501
LEFT OUTER JOIN t$Passports PIncalid ON PIncalid.f$Person = t$Persons.f$nRec AND PSnils.f$SysCode = 560
LEFT OUTER JOIN t$Catalogs INVALIDGRPCAT ON INVALIDGRPCAT.f$nREc = PIncalid.f$GivenPodr
