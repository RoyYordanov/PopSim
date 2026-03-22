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
    
    cursor.execute(load_query("delete_table")) # Clear existing data
    cursor.execute(load_query("initial_table"))
    insert_query = load_query("insert_person")

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
    cursor.executemany(insert_query, batch_of_people)

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
    # pool of bachelors
    cursor.execute("""
        SELECT id, age, sex
        FROM population
        WHERE alive = 1
        AND age >= ?
        AND marital_status = 'single'
        """, (cfg.marriage_age,))
    singles = cursor.fetchall()

    # split male and female
    males = [(id, age) for id, age, sex in singles if sex == 'male']
    females = [(id, age) for id, age, sex in singles if sex == 'female']

    # shuffle them
    random.shuffle(males)
    random.shuffle(females)

    # match based on marriage_age_gap
    couples = []
    taken_females = set()

    for m_id, m_age in males:
        for f_id, f_age in females:
            if f_id not in taken_females and abs(m_age - f_age) <= cfg.marriage_age_gap:
                couples.append((m_id, f_id))
                taken_females.add(f_id)
                break # each male gets at most one match
    
    # limit to marriage rate
    num_couples = int(get_population_count(conn, cursor) * cfg.initial_marriage_rate /1000 /2)
    couples = couples[:num_couples]

    # update marrital_status and partner_id
    for m_id, f_id in couples:
        cursor.execute("""
            UPDATE population
            SET marital_status = 'married', partner_id = ? WHERE id = ?
            """, (m_id, f_id))
        cursor.execute("""
            UPDATE population
            SET marital_status = 'married', partner_id = ? WHERE id = ?
            """, (f_id, m_id))
    
    conn.commit()
