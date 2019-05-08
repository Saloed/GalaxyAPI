SELECT DISTINCT CONVERT(VARCHAR(512), CONVERT(BIGINT,cat.f$nrec)- CONVERT(BIGINT,0x8000000000000000)) AS ID
, cat.F$NAME AS Name
FROM T$catalogs spr_typeforeigners
INNER JOIN T$catalogs cat ON (cat.f$mainlink=spr_typeforeigners.f$nrec)
WHERE spr_typeforeigners.F$SYSCODE = 3037
