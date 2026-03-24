CREATE TABLE IF NOT EXISTS population (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    sex TEXT,
    alive BOOLEAN,
    birth_year INTEGER,
    marital_status TEXT DEFAULT 'single'
);

CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_a INTEGER,
    person_b INTEGER,
    type TEXT NOT NULL CHECK(type IN ('spouse', 'parent')),
    FOREIGN KEY (person_a) REFERENCES population(id),
    FOREIGN KEY (person_b) REFERENCES population(id)
);

CREATE INDEX IF NOT EXISTS idx_rel_a ON relationships (person_a);
CREATE INDEX IF NOT EXISTS idx_rel_b ON relationships (person_b);