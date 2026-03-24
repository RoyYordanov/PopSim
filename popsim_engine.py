import json
import sqlite3
from pathlib import Path
import random
# load configuration from JSON file and make it callable as an object
with open("config.json") as f:
    config = json.load(f)

class Config:
    def __init__(self, data):
        self.initial_population = data["initial_population"]
        self.sex_age_distribution = data["sex_age_distribution"]
        self.current_year = data["current_year"]
        self.timespan = data["timespan"]
        self.birth_rate = data["birth_rate"]
        self.death_rate = data["death_rate"]
        self.death_age = data["death_age"]
        self.marriage_rate = data["marriage_rate"]
        self.initial_marriage_rate = data["initial_marriage_rate"]
        self.marriage_age = data["marriage_age"]
        self.parenting_age = data["parenting_age"]
        self.marriage_age_gap = data["marriage_age_gap"]
        self.children_per_couple = data["children_per_couple"]
        self.queer_rate = data["queer_rate"]
        self.start_year = data["current_year"]

cfg = Config(config)

# test that the configuration is loaded correctly
print("Initial_population:", cfg.initial_population)
print("Current_year:", cfg.current_year)
print("timespan:", cfg.timespan)

# load SQL query from file
def load_query(name):
    with open(Path("sql") / f"{name}.sql") as f:
        return f.read()
    

# Noise function to add randomness to the simulation
def noisy(value, noise):
    return random.gauss(value, noise)

def get_population_count(conn, cursor):
    count = int(cursor.execute(load_query("count_population")).fetchone()[0])
    return count

def InsertInitialPopulation(conn, cursor):

    batch_of_people = [] # Temporary list to hold people before batch insertion

    cursor.executescript(load_query("initial_table"))

    def random_age_from_group(age_group):
        if "+" in age_group:
            return int(age_group.replace("+", ""))
        start, end = map(int, age_group.split("-"))
        return random.randint(start, end)

    for age_group, sexes in cfg.sex_age_distribution.items():
        male_percentage = sexes["male"]
        female_percentage = sexes["female"]

        males = int(cfg.initial_population * male_percentage / 100)
        females = int(cfg.initial_population * female_percentage / 100)

        for _ in range(males):
            age = random_age_from_group(age_group)
            batch_of_people.append((age, "male", True, cfg.current_year - age))
        for _ in range(females):
            age = random_age_from_group(age_group)
            batch_of_people.append((age, "female", True, cfg.current_year - age))

    # Insert all people into the database
    cursor.executemany(load_query("insert_person"), batch_of_people)

    conn.commit()

def Death(conn, cursor):
    death_rate = max(0, noisy(cfg.death_rate, 0.5))
    cursor.execute(load_query("death_pool"), (cfg.death_age, death_rate))

    conn.commit()

def Birth(conn, cursor):
    to_be_born = int(get_population_count(conn, cursor) * cfg.birth_rate / 1000)
    births_batch = []

    for _ in range(to_be_born):
        sex = random.choice(["male", "female"])
        births_batch.append((0, sex, True, cfg.current_year))

    cursor.executemany(load_query("insert_person"), births_batch)

    conn.commit()

def Ageing(conn, cursor):
    cursor.execute(load_query("age_population"))

    conn.commit()

def FamilyFormation(conn, cursor):
    # fetch eligible singles
    cursor.execute("""
        SELECT id, age, sex FROM population
        WHERE alive = 1
        AND age >= ?
        AND marital_status = 'single'
    """, (cfg.marriage_age,))
    singles = cursor.fetchall()

    # fetch unparented children
    cursor.execute("""
        SELECT p.id, p.age FROM population p
        WHERE p.alive = 1
        AND p.age < ?
        AND NOT EXISTS (
            SELECT 1 FROM relationships r
            WHERE r.person_b = p.id AND r.type = 'parent'
        )
    """, (cfg.marriage_age,))
    children = cursor.fetchall()

    males   = [(id, age) for id, age, sex in singles if sex == 'male']
    females = [(id, age) for id, age, sex in singles if sex == 'female']

    random.shuffle(males)
    random.shuffle(females)
    random.shuffle(children)

    couples = []
    taken_females  = set()
    taken_children = set()

    for m_id, m_age in males:
        for f_id, f_age in females:
            if f_id not in taken_females and abs(m_age - f_age) <= cfg.marriage_age_gap:
                children_this_couple = []
                if f_age >= cfg.parenting_age:
                    num_children = max(0, round(noisy(cfg.children_per_couple, 0.5)))
                    assigned = 0
                    for c_id, c_age in children:
                        if assigned >= num_children:
                            break
                        if c_id not in taken_children and c_age <= f_age - cfg.parenting_age:
                            children_this_couple.append(c_id)
                            taken_children.add(c_id)
                            assigned += 1
                couples.append((m_id, f_id, children_this_couple))
                taken_females.add(f_id)
                break

    # use initial_marriage_rate on first year, marriage_rate thereafter
    rate = cfg.initial_marriage_rate if cfg.current_year == cfg.start_year else cfg.marriage_rate
    num_couples = int(get_population_count(conn, cursor) * rate / 1000)
    couples = couples[:num_couples]

    relationship_rows = []
    married_ids = []

    for m_id, f_id, children_this_couple in couples:
        relationship_rows.append((m_id, f_id, 'spouse'))
        relationship_rows.append((f_id, m_id, 'spouse'))
        married_ids.extend([m_id, f_id])
        for c_id in children_this_couple:
            relationship_rows.append((m_id, c_id, 'parent'))
            relationship_rows.append((f_id, c_id, 'parent'))

    cursor.executemany("""
        INSERT INTO relationships (person_a, person_b, type)
        VALUES (?, ?, ?)
    """, relationship_rows)

    cursor.executemany("""
        UPDATE population SET marital_status = 'married'
        WHERE id = ?
    """, [(id,) for id in married_ids])

    conn.commit()