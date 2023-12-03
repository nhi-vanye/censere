#! /bin/sh
#

# Use a in-memory databas so we don't create any files...
mars-censere --database ":memory:" generator --parameters sims/smoke-test.params --no-memory-database
