SELECT CONVERT(VARCHAR(512), CONVERT(BIGINT,det.f$nrec)- CONVERT(BIGINT,0x8000000000000000)) AS ID
, det.f$name Name
FROM t$catalogs dok
INNER JOIN t$catalogs det ON det.f$mainlink=dok.f$nrec
WHERE dok.f$syscode=-3 AND det.f$BMULTI=1
