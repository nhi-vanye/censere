#! /usr/bin/env python3

import argparse
import logging
import sys
import urllib

import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

from config import Viewer as thisApp
from config import ViewerOptions as Options

## Initialize the parsing of any command line arguments
#
def initialize_arguments_parser( argv ):

    parser = argparse.ArgumentParser(
        fromfile_prefix_chars='@',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Mars Censere Viewer""",
        epilog="""
Arguments that start with '@' will be considered filenames that
specify arguments to the program - ONE ARGUMENT PER LINE.

The Database should be on a local disk - not in Dropbox etc.
""")

    Options().register( parser )

    args = parser.parse_args( namespace = thisApp )

    log_msg_format = '%(asctime)s %(levelname)5s %(message)s'

    logging.addLevelName(thisApp.NOTICE, "NOTICE")

    log_level = thisApp.NOTICE

    # shortcut
    if thisApp.debug:

        log_msg_format='%(asctime)s.%(msecs)03d %(levelname)5s %(filename)s#%(lineno)-3d %(message)s'

        log_level = logging.DEBUG    

    else:

        log_level = thisApp.log_level

    logging.basicConfig(level=log_level, format=log_msg_format, datefmt='%Y-%m-%dT%H:%M:%S')
 
## 
# Main entry point for execution
#
# TODO - turn this funtion into a module
def main( argv ):

    db_url = urllib.parse.urlparse( thisApp.database_url )

    cnx = sqlite3.connect( db_url.path )

    df = pd.read_sql_query("SELECT * FROM summary", cnx)

    print( df.groupby("simulation_id").last() )

    fig, ax = plt.subplots()

    for key, grp in df.groupby('simulation_id'):
        ax = grp.plot(ax=ax, kind='line', x='solday', y='population', label=key)

    plt.show()


if __name__ == '__main__':

    initialize_arguments_parser( sys.argv[1:] )

    main( sys.argv[1:] )

