
import collections
import logging

from censere.config import Generator as thisApp

import censere.utils as UTILS

store = collections.defaultdict(list)

##
# \param when - absolute solday to execute the function.
def register_callback( when=0, name="", callback_func=None, kwargs=None ):

    if when == 0 or callback_func == None:

        logging.error("Missing required arguments in call to register_callback()")


    logging.log( thisApp.DETAILS, "%d.%03d Registering callback %s() to be run at %d (%d.%d)", *UTILS.from_soldays( thisApp.solday ), callback_func.__name__, when, *UTILS.from_soldays( when ) )
    logging.debug( kwargs )

    indices = collections.defaultdict(int)
    indices[ callback_func.__name__] = 0
    for entry in store[when]:
        indices[ entry['func'].__name__  ] += 1

    store[ when ].append( {
            "idx"  : indices[ callback_func.__name__],
            "name" : name,
            "func" : callback_func,
            "kwargs" : kwargs
        } )

def invoke_callbacks( ):

    if thisApp.solday in store:

        logging.info( '%d.%03d Processing scheduled events', *UTILS.from_soldays( thisApp.solday ) )

        for entry in store[thisApp.solday]:
            name = ""
            kwargs = {}

            if "name" in entry:
                name = entry['name']

            if "kwargs" in entry:
                kwargs = entry['kwargs']

            kwargs['idx'] = entry['idx']

            if "func" in entry:

                logging.debug( '%d.%03d   Processing event %s', *UTILS.from_soldays( thisApp.solday ), name )
                entry["func"](**kwargs )


