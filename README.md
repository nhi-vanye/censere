Mars Censere Project
====================

This project is aimed at building a robust population model for humanity on Mars.

This is a work in progress, the models are being developed, but for a graphical view of the sort of data we are producing take a look look at [docs/dashboard.png](docs/dashboard.png)



Getting Involved
================

The project is in the early stages of development so we're still working out how best to run the project.


All the project discussion is on the UK Mars Research Hub Slack channel - uk-mars-research-hub.slack.com




Quick Start
===========

This was developed using Python 3.8.0. It will probably work on earlier versions of Python 3. Not interested in supporting Python 2 at this point.

Install the pre-requisits - we really suggest doing this in a virtual envronment specific to this project.

```
% pip install -r requirements.txt
```

There are expected to be multiple components in the project, currently
we are separating the simulation run from any downstream analsis.
The simulation run (`generator`) outputs into a SQLite database,
which can be loaded into `pandas`, `R` etc) as desired.

The database can hold multiple simulations so you can analyse the
impact of changing the simulation model.


```
% python3 -m censere.generator --help
usage: generator.py [-h] [--database FILE] [--debug] [--dump] [--log-level LOG_LEVEL] [--debug-sql] [--astronaut-age-range RANDOM]
                    [--astronaut-gender-ratio MALE,FEMALE] [--astronaut-life-expectancy RANDOM] [--cache-details] [--common-ancestor GENERATION]
                    [--continue-simulation CONTINUE_SIMULATION] [--database-dir DIR] [--first-child-delay RANDOM]
                    [--fraction-singles-pairing-per-day FRACTION_SINGLES_PAIRING_PER_DAY]
                    [--fraction-relationships-having-children FRACTION_RELATIONSHIPS_HAVING_CHILDREN] [--initial-mission-lands DATETIME]
                    [--limit {sols,population}] [--limit-count LIMIT_COUNT] [--martian-gender-ratio MALE,FEMALE] [--martian-life-expectancy LIFE]
                    [--mission-lands RANDOM] [--notes TEXT] [--orientation HETROSEXUAL,HOMOSEXUAL,BISEXUAL] [--partner-max-age-difference YEARS]
                    [--random-seed RAND] [--relationship-length RANDOM] [--settlers-per-initial-ship RANDOM] [--settlers-per-ship RANDOM]
                    [--ships-per-initial-mission RANDOM] [--ships-per-mission RANDOM] [--sols-between-siblings RANDOM] [--use-ivf]

Mars Censere Generator

optional arguments:
  -h, --help            show this help message and exit
  --database FILE       Path to database (CENSERE_DATABASE)
  --debug               Enable debug mode (CENSERE_DEBUG)
  --dump                Dump the simulation parameters to stdout (CENSERE_DUMP)
  --log-level LOG_LEVEL
                        Enable debug mode: 15=DETAILS, 20=INFO, 25=NOTICE (CENSERE_LOG_LEVEL)
  --debug-sql           Enable debug mode for SQL queries (CENSERE_DEBUG_SQL)
  --astronaut-age-range RANDOM
                        Age range (years) of arriving astronauts (CENSERE_ASTRONAUT_AGE_RANGE)
  --astronaut-gender-ratio MALE,FEMALE
                        Male:Female ratio for astronauts, MUST add up to 100 (CENSERE_ASTRONAUT_GENDER_RATIO)
  --astronaut-life-expectancy RANDOM
                        Life expectancy of arriving astronauts - default is "cdc:" (CENSERE_ASTRONAUT_LIFE_EXPECTANCY)
  --cache-details       Log cache effectiveness as the simulation runs (CENSERE_CACHE_DETAILS)
  --common-ancestor GENERATION
                        Allow realtionships where common ancestor is older than GEN. GEN=1 => parent, GEN=2 => grandparent etc
                        (CENSERE_COMMON_ANCESTOR)
  --continue-simulation CONTINUE_SIMULATION
                        Continue the simulation to a new limit (CENSERE_CONTINUE_SIMULATION)
  --database-dir DIR    Use a unique file in DIR. This takes priority over --database. Unique file is based on the simulation id (CENSERE_DATABASE_DIR)
  --first-child-delay RANDOM
                        Delay (sols) between relationship start and first child (CENSERE_FIRST_CHILD_DELAY)
  --fraction-singles-pairing-per-day FRACTION_SINGLES_PAIRING_PER_DAY
                        The fraction of singles that will start a relationship PER DAY (CENSERE_FRACTION_SINGLES_PAIRING)
  --fraction-relationships-having-children FRACTION_RELATIONSHIPS_HAVING_CHILDREN
                        The fraction of relationships that will have children (CENSERE_FRACTION_RELATIONSHIPS_HAVING_CHILDREN)
  --initial-mission-lands DATETIME
                        Earth date that initial mission lands on Mars (CENSERE_INITIAL_MISSION_LANDS)
  --limit {sols,population}
                        Stop simmulation when we hit a time or population limit (CENSERE_LIMIT)
  --limit-count LIMIT_COUNT
                        Stop simulation when we hit a time or population limit (CENSERE_LIMIT_COUNT)
  --martian-gender-ratio MALE,FEMALE
                        Male:Female ratio for new born martians, MUST add up to 100 (CENSERE_MARTIAN_GENDER_RATIO)
  --martian-life-expectancy LIFE
                        Life expectancy of new born martians - default "cdc:" (CENSERE_MARTIAN_LIFE_EXPECTANCY)
  --mission-lands RANDOM
                        Land a new mission every MEAN +- STDDEV sols (CENSERE_MISSION_LANDS)
  --notes TEXT          Add TEXT into notes column in simulations table (CENSERE_NOTES)
  --orientation HETROSEXUAL,HOMOSEXUAL,BISEXUAL
                        Sexual orientation percentages, MUST add up to 100 (CENSERE_OREINTATION)
  --partner-max-age-difference YEARS
                        Limit possible relationships to partners with maximum age difference (CENSERE_PARTNER_MAX_AGE_DIFFERENCE)
  --random-seed RAND    Seed used to initialize random engine (CENSERE_SEED)
  --relationship-length RANDOM
                        How many SOLS a partnerhsip lasts (CENSERE_RELATIONSHIP_LENGTH)
  --settlers-per-initial-ship RANDOM
                        Numbering of arriving astronauts for the initial landing (CENSERE_INITIAL_SETTLERS_PER_SHIP)
  --settlers-per-ship RANDOM
                        Numbering of arriving astronauts per ship (CENSERE_SETTLERS_PER_SHIP)
  --ships-per-initial-mission RANDOM
                        Numbering of ships per mission (CENSERE_SHIPS_PER_INITIAL_MISSION)
  --ships-per-mission RANDOM
                        Numbering of ships per mission (CENSERE_SHIPS_PER_MISSION)
  --sols-between-siblings RANDOM
                        Gap between sibling births (CENSERE_SOLS_BETWEEN_SIBLINGS)
  --use-ivf             Use IFV to extend fertility (CENSERE_USE_IFV)

Arguments that start with '@' will be considered filenames that
specify arguments to the program - ONE ARGUMENT PER LINE.

The Database should be on a local disk - not in Dropbox etc.

RANDOM Values
-------------

This can be calculated using built-in tables from the CDC, or a random function age

The option is specified as string:arg1,arg2,..argn

Acceptable Values are:

  cdc:
    use CDC tables (no args are needed). This is only valid for Life Expectancy

  triangular:MIN,PEAK,MAX
    use NUMPY's triangular random function with MIN,PEAK and MAX ages (in earth years)

  guass:MEAN,STDDEV
    use NUMPY's guass random function with MEAN and STDDEV ages (in earth years)

  randint:MIN,MAX
    use NUMPY's randint random function with MIN and MAX ages such that MIN <= N <= MAX (in earth years)

  randrange:MIN,MAX
    use NUMPY's randint random function with MIN and MAX ages such that MIN <= N < MAX (in earth years)

  half:BEGIN,STEP
    There is a 50% probability that a value between BEGIN and BEGIN+STEP will be picked, 25% between BEGIN+STEP and BEGIN+(STEP*2), a 12.5% between BEGIN+(STEP*2) and BEGIN+(STEP*3) etc.
```

Censere will read values from the environment as listed in the help
text (i.e. the database can be set using the environment variable
CENSERE_DATABASE_URL)


Then run the `generator` to run the simulation - a small run to start off.

```
% python3 -m censere.generator --limit-count=100
2019-11-21T11:26:07 NOTICE Mars Censere 2019.325
2019-11-21T11:26:07 NOTICE 1.1 (1) Simulation eff6acc5-a6a8-4cdb-9a37-b9f133078560 Started. Goal population = 100
2019-11-21T11:26:07 NOTICE 1.1 Mission landed with 20 colonists
2019-11-21T11:26:07 NOTICE 1.28 (28) #Colonists 20
2019-11-21T11:26:07 NOTICE 1.56 (56) #Colonists 20
2019-11-21T11:26:07 NOTICE 1.63 Martian Jesse Johnson (d8d54575-b4c0-4fab-8a92-35c2455f02d0) born
2019-11-21T11:26:07 NOTICE 1.84 (84) #Colonists 21
2019-11-21T11:26:07 NOTICE 1.106 Martian Brenda White (2717a34f-aa95-4809-8ad1-9fb2f0fc6025) born
2019-11-21T11:26:07 NOTICE 1.112 (112) #Colonists 22
2019-11-21T11:26:07 NOTICE 1.140 (140) #Colonists 22
...
2019-11-21T11:26:10 NOTICE 2.588 (1256) #Colonists 90
2019-11-21T11:26:10 NOTICE 2.616 (1284) #Colonists 90
2019-11-21T11:26:10 NOTICE 2.630 Martian Joshua Gray (73b83747-5883-499d-b7df-9b5bb291c495) born
2019-11-21T11:26:10 NOTICE 2.644 (1312) #Colonists 91
2019-11-21T11:26:10 NOTICE 3.0 (1336) #Colonists 91
2019-11-21T11:26:10 NOTICE 3.28 (1364) #Colonists 91
2019-11-21T11:26:10 NOTICE 3.56 (1392) #Colonists 91
2019-11-21T11:26:10 NOTICE 3.84 (1420) #Colonists 91
2019-11-21T11:26:11 NOTICE 3.112 (1448) #Colonists 91
2019-11-21T11:26:11 NOTICE 3.140 (1476) #Colonists 91
2019-11-21T11:26:11 NOTICE 3.168 (1504) #Colonists 91
2019-11-21T11:26:11 NOTICE 3.183 Mission landed with 69 colonists
2019-11-21T11:26:11 NOTICE 3.184 (1520) Simulation eff6acc5-a6a8-4cdb-9a37-b9f133078560 Complete. population 160 >= 100
```

Using Docker
------------

There is a script `scripts/build.sh` that will build a docker image


SQLite is not intended for parallel use, best practice is to mount
a directory into the container and then specify a run specific
database i.e.

```
docker run -it -d -v /home/core/data:/data  $image  \
			--database=/data/$(date +"%Y%m%d%H%M%S").db
```


Graphical Dashboard
===================

There is an early version of an interactive graphical dashboard in
`censere/dashboard.py` - it reads from a database

```
% python -m censere.dashboard --database data/202002021525.db
```

This database was from 25 independent simulation runs with the same
parameters, indicating that the overal simulation is still predominated
by randomness.


![alt text](docs/dashboard.png "Sample Dashboard")
