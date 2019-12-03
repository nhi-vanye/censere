
import collections
import logging

from censere.config import Generator as thisApp

import censere.utils as UTILS

store = collections.defaultdict(list)

def register_callback( when=0, name="", callback_func=None, kwargs=None ):

    if when == 0 or callback_func == None:

        logging.error("Missing required arguments in call to register_callback()")

    logging.log( thisApp.DETAILS, "%d.%d Registering callback %s() to be run at %d (%d.%d)", *UTILS.from_soldays( thisApp.solday ), callback_func.__name__, when, *UTILS.from_soldays( when ) )
    logging.debug( kwargs )

    store[ when ].append( {
            "name" : name,
            "func" : callback_func,
            "kwargs" : kwargs
        } )

def invoke_callbacks( ):

    if thisApp.solday in store:

        logging.info( '%.% Processing scheduled events', *UTILS.from_soldays( thisApp.solday ) )
        for entry in store[thisApp.solday]:

            name = ""
            kwargs = {}

            if "name" in entry:
                name = entry['name']

            if "kwargs" in entry:
                kwargs = entry['kwargs']

            if "func" in entry:

                logging.debug( '%d.%d   Processing event %s', *UTILS.from_soldays( thisApp.solday ), name )
                entry["func"](**kwargs )


