SELECT 0 AS ID, 'очное обучение' AS NAME
FROM t$clones t
WHERE t.F$SNAME='UNIVER' UNION ALL
SELECT 1, 'заочное обучение'
FROM t$clones t
WHERE t.F$SNAME='UNIVER' UNION ALL
SELECT 2, 'очно-заочное обучение'
FROM t$clones t
WHERE t.F$SNAME='UNIVER' UNION ALL
SELECT 3, 'самообразование'
FROM t$clones t
WHERE t.F$SNAME='UNIVER' UNION ALL
SELECT 4, 'сетевая форма'
FROM t$clones t
WHERE t.F$SNAME='UNIVER' UNION ALL
SELECT 5, 'электронное обучение (исключительно)'
FROM t$clones t
WHERE t.F$SNAME='UNIVER' UNION ALL
SELECT 6, 'электронное обучение (частично)'
FROM t$clones t
WHERE t.F$SNAME='UNIVER' UNION ALL
SELECT 7, 'дистанц.образов.технологии (исключительно)'
FROM t$clones t
WHERE t.F$SNAME='UNIVER' UNION ALL
SELECT 8, 'дистанц.образов.технологии (частично)'
FROM t$clones t
WHERE t.F$SNAME='UNIVER'
