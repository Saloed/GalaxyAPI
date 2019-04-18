SELECT CONVERT(VARCHAR(512), CONVERT(BIGINT,det.f$nrec)- CONVERT(BIGINT,0x8000000000000000)) AS ID
, det.f$name Name
FROM t$catalogs nat
INNER JOIN t$catalogs det ON det.f$mainlink=nat.f$nrec
WHERE nat.f$syscode=-120
