SELECT DISTINCT CONVERT(VARCHAR(512),(CONVERT(BIGINT, CATALOGS.f$NREC)+9223372036854775808) AS ID
, CATALOGS.f$NAME AS NAME
FROM t$CATALOGS CAT_MAIN
LEFT OUTER
JOIN t$CATALOGS CATALOGS ON
CATALOGS.f$CPARENT=CAT_MAIN.f$NREC
WHERE
 (
CAT_MAIN.f$SYSCODE=3037
)
