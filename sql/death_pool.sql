UPDATE population
SET alive = FALSE
WHERE id IN (
    SELECT id FROM population
    WHERE alive IS TRUE
    AND age > ?
    ORDER BY RANDOM()
    LIMIT (
        SELECT CAST(COUNT(*) * ? /1000 AS INTEGER)
        FROM population
        WHERE alive IS TRUE
    )
)

