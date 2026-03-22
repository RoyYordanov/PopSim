CREATE TABLE population (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    sex TEXT,
    alive BOOLEAN,
    birth_year INTEGER,
    marital_status TEXT DEFAULT 'single',
    partner_id INTEGER,
    father_id INTEGER,
    mother_id INTEGER,
    children_ids TEXT
);