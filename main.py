import popsim_engine as pe
import grapher
import sqlite3

years = []
population_counts = []

conn = sqlite3.connect("population.db")
cursor = conn.cursor()

pe.InsertInitialPopulation(conn, cursor)

for year in range(pe.cfg.current_year, pe.cfg.current_year + pe.cfg.timespan):
    print(f"Year: {year}")
    pe.cfg.current_year = year
    print("Population count:", pe.get_population_count(conn, cursor))
    pe.Death(conn, cursor)
    pe.Birth(conn, cursor)
    pe.Ageing(conn, cursor)
    years.append(year)
    population_counts.append(pe.get_population_count(conn, cursor))
    conn.commit()

grapher.plot_population_over_time(years, population_counts)
conn.close()