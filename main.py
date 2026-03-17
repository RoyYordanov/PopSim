import popsim_engine as pe
import grapher

years = []
population_counts = []

pe.InsertInitialPopulation()

for year in range(pe.cfg.current_year, pe.cfg.current_year + pe.cfg.timespan):
    print(f"Year: {year}")
    print("Population count:", pe.get_population_count())
    pe.Death()
    pe.Birth()
    pe.Ageing()
    years.append(year)
    population_counts.append(pe.get_population_count())

grapher.plot_population_over_time(years, population_counts)