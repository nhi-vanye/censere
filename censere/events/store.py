
import collections
import logging

from censere.config import Generator as thisApp

import censere.utils as UTILS

store = collections.defaultdict(list)

def register_callback( when=0, name="", callback_func=None, kwargs={}):

    if when == 0 or callback_func == None:

        logging.error("Missing required arguments in call to register_callback()")

    logging.debug( "{}.{} Registering callback {}() to be run at {} ({}.{})".format( *UTILS.from_soldays( thisApp.solday ), callback_func.__name__, when, *UTILS.from_soldays( when ), kwargs ) )
    logging.debug( "{}".format( kwargs ) )

    store[ when ].append( {
            "name" : name,
            "func" : callback_func,
            "kwargs" : kwargs
        } )

def invoke_callbacks( ):

    if thisApp.solday in store:

        logging.info( '{}.{} Processing scheduled events'.format( *UTILS.from_soldays( thisApp.solday ) ) )
        for entry in store[thisApp.solday]:

            name = ""
            kwargs = {}

            if "name" in entry:
                name = entry['name']

            if "kwargs" in entry:
                kwargs = entry['kwargs']

            if "func" in entry:

                logging.debug( '{}.{}   Processing event {}'.format( *UTILS.from_soldays( thisApp.solday ), name ) )
                entry["func"](**kwargs )


