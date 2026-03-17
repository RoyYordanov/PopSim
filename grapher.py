import matplotlib.pyplot as plt

def plot_population_over_time(years, population_counts):
    plt.figure(figsize=(10, 5))
    plt.plot(years, population_counts, marker='o')
    plt.title('Population Growth Over Time')
    plt.xlabel('Year')
    plt.ylabel('Population Count')
    plt.grid()
    plt.show()