# Goal
To make a software in Python that allows to generate a population of people with a variety of parameters and examine their growth over a specified period of time.
 
The aim is to make the Simulator less deterministic and more event-driven.
 
Note:
- 🎲 - variable
- 📝 - trait
Wherever missed to mention for a variable, assume it is per 1k people.
Every variable will have an adjustable noise value.
# Cultural and Societal inspiration
Some aspects of the simulator are inspired by Western-values.
# Stack
- Python to build the app
- SQL for the data
- HTML, CSS and JS for the web interface
# Starting Parameters
- 🎲initial population
- 🎲timespan (years)
# Phase 1 - Basic
A "population" array of objects fluctuates over the given period of time, depending on the birth, death, and noise.
- 🎲birth rate (births per 1k per year)
- 🎲death rate (deaths per 1k per year)
Each object has
- 📝 ID number - assigned incrementally
- 📝 Sex - 50/50 male/female
- 📝 Name - depending on sex
# Phase 2 - Death
- 🎲Initial Age and Sex distribution - a dataset determining the age-sex distribution for the initial population.Index column's rows determine age (1-100). The two columns determine sex (male, female). The values inside determine percentage of population in that age-sex group.
- 📝Alive - TRUE/FALSE
- Newborns:
- Alive - TRUE
- begin with age 1 and grow +1
- 50/50 chance of being male/female
- 🎲Death age
- People that die stop ageing and are marked as dead.
- Every year, a pool of people proportional to the death rate that are close to the death age die.
# Phase 3 - Families
🎲A "marriage" rate determines amount of marriages per 1k per year.
🎲"Initial Married" variable determines how many people are married from the start per 1k (Ireland 46.2% 2022).
🎲Marriage age
🎲 Parenting age
- current gen (31)
- gran gen (27)
- great-gran gen (25)
🎲Marriage age gap
Organize married people into families:
- randomly select pool of married people
- pair them male to female using the marriage age gap variable
- allocate them to generations:
- ~31 parents
- +27 grandparents
- +25 great-grandp
- older
- assign grandparents and great-grandparents to parents
📝Partner
📝Father
📝Mother
📝Children
- Assign Family names
- select all males and sort old-young
- starting from the eldest:
- assign a name
- if married - wife inherits name
- if has children - inherit name
- repeat for each child
# Phase 4 - Pairing
🎲Children per family
📝Marital status
Single
Married
Widowed
- Define children as under 18.
- Distribute kids among Parents families generation, where the mother's age is at least 18 years more than the child's age
- Inherit family name, father, mother
Every year:
- a pool of people with "Single" Marital status and close to the marriage age is gathered
- a number of them, proportional to the marriage rate, are paired male to female
- Partner field gets filled out
- couples that are at the parenting age receive a newborn with fields:
- Family name inherited from father
- Father, Mother, Siblings
# Phase 5 - Special cases
🎲Queer rate - assign a probability to a newborn for sexuality
📝Sexuality
- homosexual
- heterosexual
- bisexual
- asexual
The pairing mechanism is adjusted to pair people that are attracted to the relevant sex.
📝Orphan status
# Phase 6 - Migration
📝Immigration rate - annual rate of foreign people spawning into the population
📝Emigration rate - annual rate of local people leaving the population
Immigrant traits
- Surname - unique
- Marital status - single
- Father, Mother, Partner, Children - none
# Interface
I want a web interface displaying:
A front page with all variables (and their noise) to be set up, and a "Run" button.
The following graphs:
- Initial and final sex-age distribution pyramid
- A line chart with Y=population count and X=years
- A Gantt chart of the families' longevity, with Y=families and X=years

# Software structure
- JSON config file with all parameters
- DB file containing the entire population
- Python loop engine
- SQL query files to call & manipulate the data
- FastAPI
- HTML & CSS frontend