Mars Censere Project
====================

This project is aimed at building a robust population model for humanity on Mars.


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
usage: generator.py [-h] [--database-url URL] [--debug] [--log-level LOG_LEVEL] [--debug-sql] [--astronaut-age-range MIN,MAX] [--limit {sols,population}] [--limit-count LIMIT_COUNT]

Mars Censere Generator

optional arguments:
  -h, --help            show this help message and exit
  --database FILE       Path to database (CENSERE_DATABASE)
  --debug               Enable debug mode (CENSERE_DEBUG)
  --log-level LOG_LEVEL
                        Enable debug mode: 15=DETAILS, 20=INFO, 25=NOTICE (CENSERE_LOG_LEVEL)
  --debug-sql           Enable debug mode for SQL queries (CENSERE_DEBUG_SQL)
  --astronaut-age-range MIN,MAX
                        Age range of arriving astronauts (CENSERE_ASTRONAUT_AGE_RANGE)
  --limit {sols,population}
                        Stop simmulation when we hit a time or population limit (CENSERE_LIMIT)
  --limit-count LIMIT_COUNT
                        Stop simulation when we hit this limit (CENSERE_LIMIT_COUNT)

Arguments that start with '@' will be considered filenames that
specify arguments to the program - ONE ARGUMENT PER LINE.

The Database should be on a local disk - not in Dropbox etc.
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

This is currently an early work in progress - so there is not much
configuration in changing the likelyhood of events occuring. If you
don't like the rate of randomness please consider submitting a pull
request that changes the likelyhood AND makes it configurable from
the command line.

At this point you should have a database in `./censere.db` 


Using Docker
============

There is a script `scripts/build.sh` that will build a docker image

You will need to mount the database outside of the container for
the data to be persisted beyond the container's life

i.e. on CoreOS

```
core% docker run -it -v /home/core/fred:/censere.db censere
```

SQLite is not intended for parallel use, so only have one container
running at a time. `peewee` - the database layer does supprt other
SQL databases so it should be easy to do this if needed.

