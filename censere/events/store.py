
import collections
import logging

from config import Generator as thisApp

store = collections.defaultdict(list)

def register_callback( when=0, name="", callback_func=None, kwargs={}):

    if when == 0 or callback_func == None:

        logging.error("Missing required arguments in call to register_callback()")

    logging.debug( "Registering {} ( {}() ) at {}".format( name, callback_func.__name__, when ) )

    store[ when ].append( {
            "name" : name,
            "func" : callback_func,
            "kwargs" : kwargs
        } )

def invoke_callbacks( solday, solyear, sol ):

    if solday in store:

        logging.info( '{}.{} Processing scheduled events'.format( solyear,sol ) )
        for entry in store[solday]:

            name = ""
            kwargs = {}

            if "name" in entry:
                name = entry['name']

            if "kwargs" in entry:
                kwargs = entry['kwargs']

            if "func" in entry:

                logging.debug( '{}.{}   Processing event {}'.format( solyear, sol, name ) )
                entry["func"](solday, solyear, sol,  **kwargs )


