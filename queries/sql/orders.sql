SELECT DISTINCT CONVERT(VARCHAR(512), CONVERT(BIGINT,t$TitleDoc.f$Nrec)- CONVERT(BIGINT,0x8000000000000000)) AS ID
, COALESCE(t$TitleDoc.f$DocNMB,' ') AS number
, [dbo].date2str('%dd.%MM.%yyyy',t$TitleDoc.f$DocDate) AS Date
, CONVERT(VARCHAR(512), CONVERT(BIGINT,t$U_TypePr.f$Nrec)- CONVERT(BIGINT,0x8000000000000000)) AS action_ID
, COALESCE(t$U_TypePr.f$CODOPER,0) AS action_Type
, (CASE WHEN t$PartDoc.f$TypeOper=30001 OR t$PartDoc.f$TypeOper=30004 OR t$PartDoc.f$TypeOper=30052 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$Appointments.f$AppointDate), NULL) WHEN t$PartDoc.f$TypeOper=30002 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$CasePsn.f$DChange), NULL) WHEN t$PartDoc.f$TypeOper=30003 OR t$PartDoc.f$TypeOper=30011 OR t$PartDoc.f$TypeOper=30012 OR t$PartDoc.f$TypeOper=30013 OR t$PartDoc.f$TypeOper=30016 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$Raise.f$FromDate), NULL) WHEN t$PartDoc.f$TypeOper=30005 OR t$PartDoc.f$TypeOper=30042 OR t$PartDoc.f$TypeOper=30050 OR t$PartDoc.f$TypeOper=30051 OR t$PartDoc.f$TypeOper=30054 OR t$PartDoc.f$TypeOper=30060 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',NewAppoint.f$AppointDate), NULL) WHEN t$PartDoc.f$TypeOper=30006 OR t$PartDoc.f$TypeOper=30031 OR t$PartDoc.f$TypeOper=30080 OR t$PartDoc.f$TypeOper=30100 OR t$PartDoc.f$TypeOper=30105 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$PartDoc.f$dDat1), NULL) WHEN t$PartDoc.f$TypeOper=30007 OR t$PartDoc.f$TypeOper=30088 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',ContDoc2.f$Dat1), NULL) WHEN t$PartDoc.f$TypeOper=30008 OR t$PartDoc.f$TypeOper=30009 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$ContDoc.f$dPrik), NULL) WHEN t$PartDoc.f$TypeOper=30014 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$ContDoc.f$dRezerve), NULL) WHEN t$PartDoc.f$TypeOper=30015 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$U_Benefits.f$FromDate), NULL) WHEN t$PartDoc.f$TypeOper=30017 OR t$PartDoc.f$TypeOper=30018 OR t$PartDoc.f$TypeOper=30019 OR t$PartDoc.f$TypeOper=30021 OR t$PartDoc.f$TypeOper=30022 OR t$PartDoc.f$TypeOper=30023 OR t$PartDoc.f$TypeOper=30024 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$RaiseHist.f$Ddat1), NULL) WHEN t$PartDoc.f$TypeOper=30025 OR t$PartDoc.f$TypeOper=30026 OR t$PartDoc.f$TypeOper=30030 OR t$PartDoc.f$TypeOper=30053 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$ContDoc.f$Dat1), NULL) WHEN t$PartDoc.f$TypeOper=30032 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$Punishments.f$Dat1), NULL) WHEN t$PartDoc.f$TypeOper=30033 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$Fortune.f$Dat1), NULL) WHEN t$PartDoc.f$TypeOper=30041 OR t$PartDoc.f$TypeOper=30043 OR t$PartDoc.f$TypeOper=30044 OR t$PartDoc.f$TypeOper=30045 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$Vacations.f$PlanYearBeg), NULL) WHEN t$PartDoc.f$TypeOper=30081 OR t$PartDoc.f$TypeOper=30082 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$PartDoc.f$LastDate), NULL) ELSE COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$TitleDoc.f$DocDate), NULL) END) AS date_ras
, (CASE WHEN t$PartDoc.f$TypeOper=30001 OR t$PartDoc.f$TypeOper=30004 OR t$PartDoc.f$TypeOper=30005 OR t$PartDoc.f$TypeOper=30007 OR t$PartDoc.f$TypeOper=30042 OR t$PartDoc.f$TypeOper=30050 OR t$PartDoc.f$TypeOper=30051 OR t$PartDoc.f$TypeOper=30052 OR t$PartDoc.f$TypeOper=30080 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$Appointments.f$appointdate), NULL) ELSE NULL END) AS FromDate
, (CASE WHEN t$PartDoc.f$TypeOper=30041 OR t$PartDoc.f$TypeOper=30043 OR t$PartDoc.f$TypeOper=30044 OR t$PartDoc.f$TypeOper=30045 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$Vacations.f$PlanYearEnd), NULL) WHEN t$PartDoc.f$TypeOper=30001 OR t$PartDoc.f$TypeOper=30004 OR t$PartDoc.f$TypeOper=30005 OR t$PartDoc.f$TypeOper=30007 OR t$PartDoc.f$TypeOper=30042 OR t$PartDoc.f$TypeOper=30050 OR t$PartDoc.f$TypeOper=30051 OR t$PartDoc.f$TypeOper=30052 OR t$PartDoc.f$TypeOper=30080 THEN COALESCE([dbo].date2str('%dd.%MM.%yyyy',t$Appointments.f$dismissdate), NULL) ELSE NULL END) AS ToDate
, CONVERT(VARCHAR(512), CONVERT(BIGINT,DepartOLD.f$cRef3)- CONVERT(BIGINT,0x8000000000000000)) AS FromBUP
, CONVERT(VARCHAR(512), CONVERT(BIGINT,DepartNew.f$cRef3)- CONVERT(BIGINT,0x8000000000000000)) AS ToBUP
, CONVERT(VARCHAR(512), CONVERT(BIGINT,t$Appointments.f$cDopInf)- CONVERT(BIGINT,0x8000000000000000)) AS FromRUP
, CONVERT(VARCHAR(512), CONVERT(BIGINT,NewAppoint.f$cDopInf)- CONVERT(BIGINT,0x8000000000000000)) AS ToRUP
, CASE WHEN t$ContDoc.f$TypeOper=30080 AND t$ContDoc.f$wAttrDoc1>0 THEN 'Да' ELSE 'Нет' END AS USLPER
, UStudent.f$UNS AS student_UID
, CONVERT(VARCHAR(512), CONVERT(BIGINT,UStudent.f$Nrec)- CONVERT(BIGINT,0x8000000000000000)) AS NREC
, COALESCE(t$U_TypePr.f$NOPER,' ') AS action_TypeName
, COALESCE(spkau_ref.f$code,' ') AS action_reason
, COALESCE(spkau_ref.f$name + CASE WHEN aval.F$VSTRING IS NOT NULL THEN ' '+aval.F$VSTRING ELSE '' END, ' ') AS action_reasonName
FROM t$U_Student UStudent
INNER JOIN t$ContDoc ON t$ContDoc.f$Person = UStudent.f$cPersons
LEFT OUTER JOIN t$ContDoc Contdoc2 ON ContDoc2.f$Nrec = t$ContDoc.f$cDopRef AND Contdoc2.f$TypeOper = t$Contdoc.f$TypeOper AND (t$Contdoc.f$cPart=0 OR t$Contdoc.f$TypeOper = 30065)
INNER JOIN t$PartDoc ON t$PartDoc.f$Nrec = CASE WHEN COALESCE(Contdoc2.f$Nrec,0)=0 THEN t$ContDoc.f$cPart ELSE CONTDOC2.f$cPART END
INNER JOIN t$TitleDoc ON t$TitleDoc.f$Nrec = t$PartDoc.f$cDoc AND t$TitleDoc.f$wStatus=1
INNER JOIN t$U_TypePr ON t$U_TypePr.f$CodOper = t$PartDoc.f$TypeOper AND t$U_TypePr.f$wTDop = t$PartDoc.f$wAttr1
LEFT OUTER JOIN t$U_StudGroup U_StudGroupN ON U_StudGroupN.f$NRec = t$ContDoc.f$cStr
LEFT OUTER JOIN t$Appointments ON t$Appointments.f$Nrec = CASE WHEN t$PARTDOC.f$TYPEOPER = 30001 OR t$PartDoc.f$TypeOper=30004 OR t$PartDoc.f$TypeOper=30052 THEN t$ContDoc.f$ObjNrec ELSE t$ContDoc.f$cStr END
LEFT OUTER JOIN t$Appointments NewAppoint ON NewAppoint.f$cCont = t$ContDoc.f$Nrec
LEFT OUTER JOIN t$Catalogs DepartOLD ON DepartOLD.f$Nrec = t$Appointments.f$Department
LEFT OUTER JOIN t$Catalogs DepartNew ON DepartNew.f$Nrec = NewAppoint.f$Department
LEFT OUTER JOIN t$U_StudGroup ON t$U_StudGroup.f$Nrec = CASE WHEN t$PartDoc.f$TypeOper=30026 OR t$PartDoc.f$TypeOper=30053 OR t$PartDoc.f$TypeOper=30080 OR t$PartDoc.f$TypeOper=30081 OR t$PartDoc.f$TypeOper=30083 THEN COALESCE(U_StudGroupN.f$NRec,0) WHEN t$PartDoc.f$TypeOper=30106 OR t$PartDoc.f$TypeOper=30107 THEN -1 ELSE COALESCE(t$Appointments.f$cCat1,0) END
LEFT OUTER JOIN t$U_Stud_FinSource ON t$U_Stud_FinSource.f$Nrec = t$Appointments.f$cRef2
LEFT OUTER JOIN t$SpKau ON t$SpKau.f$Nrec = t$U_Stud_FinSource.f$cFinSource
LEFT OUTER JOIN t$CasePsn ON t$CasePsn.f$Nrec = t$ContDoc.f$ObjNRec
LEFT OUTER JOIN t$Raise ON t$Raise.f$cRDop = t$ContDoc.f$nRec
LEFT OUTER JOIN t$U_Benefits ON t$U_Benefits.f$cContDoc = t$U_Benefits.f$cContDoc
LEFT OUTER JOIN t$RaiseHist ON t$RaiseHist.f$cContDoc=t$ContDoc.f$nRec
LEFT OUTER JOIN t$Punishments ON t$Punishments.f$Nrec = t$ContDoc.f$ObjNrec
LEFT OUTER JOIN t$Fortune ON t$Fortune.f$Nrec = t$ContDoc.f$ObjNrec
LEFT OUTER JOIN t$Vacations ON t$Vacations.f$cPrikaz=t$ContDoc.f$nRec
LEFT OUTER JOIN t$Tunedef def ON def.F$CODE='UCS_DOP.PRIKAZ.KAU_REASON' AND def.F$ATL_ORIGINOFFICE=1 /*Здесь вставить код офиса входа в галактику*/
LEFT OUTER JOIN t$tuneval val ON val.F$CTUNE=def.F$NREC AND val.F$ATL_ORIGINOFFICE=1 /*Здесь вставить код офиса входа в галактику*/
LEFT OUTER JOIN t$Kaureff ON t$Kaureff.f$coTable=25044 AND t$Kaureff.f$crec=t$PartDoc.f$Nrec AND t$Kaureff.f$wkau=val.F$LONGVAL
LEFT OUTER JOIN t$Spkau spkau_ref ON spkau_ref.F$NREC=t$Kaureff.f$ckau
LEFT OUTER JOIN t$attrnam anam ON anam.F$WTABLE=8512 AND anam.f$name='Дополнение'
LEFT OUTER JOIN t$attrval aval ON aval.f$wtable=8512 AND aval.F$CATTRNAM=anam.F$NREC AND aval.F$CREC=spkau_ref.f$nrec
