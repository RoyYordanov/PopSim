CREATE TEMP TABLE marriage_pool
AS SELECT id, age, sex
FROM population
WHERE age >= :marriage_age
AND alive = 1
AND sex = 'male'
AND marrital_status = 'Single';

CREATE TEMP TABLE bachelors AS
SELECT *
FROM marriage_pool
WHERE sex = 'male';

CREATE TEMP TABLE bachelorettes AS
SELECT *
FROM marriage_pool
WHERE sex = 'female';

CREATE TEMP TABLE couples AS
SELECT
m.id AS m
f.id AS f
FROM bachelors m
JOIN bacchelorette s 
ON ABS(m.age - f.age) <= :age_gap
ORDER BY RANDOM();
LIMIT (
    SELECT CAST(COUNT (*) *
    :marriage_rate / 1000 AS INTEGER)
    FROM population
    WHERE alive = 1
);

UPDATE population
SET marrital_status = 'married', partner = 
WHERE id IN OR(couples.m, couples.f)