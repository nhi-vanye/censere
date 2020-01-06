
import importlib
import logging
import json

from censere.config import Generator as thisApp

import censere.utils as UTILS

import censere.models as MODELS

##
# \param when - absolute solday to execute the function.
# \param callback_func - fully qualified function
def register_callback( when=0, name="", callback_func=None, kwargs=None ):

    if when == 0 or callback_func == None:

        logging.error("Missing required arguments in call to register_callback()")

        return


    logging.log( thisApp.DETAILS, "%d.%03d Registering callback %s.%s() to be run at %d (%d.%d)", *UTILS.from_soldays( thisApp.solday ), callback_func.__module__, callback_func.__name__, when, *UTILS.from_soldays( when ) )
    logging.debug( kwargs )

    try:
        idx = MODELS.Event.select().where(
            ( MODELS.Event.simulation_id == thisApp.simulation ) &
            ( MODELS.Event.when == when ) &
            ( MODELS.Event.callback_func == "{}.{}".format( callback_func.__module__, callback_func.__name__ ) )
        ).count()

        e = MODELS.Event()

        e.simulation_id = thisApp.simulation
        e.registered = thisApp.solday
        e.when = when
        e.idx = idx
        # This allows us to pass a real function into the ergister function (rather then a string)
        # but store the full name of the function for later execution
        e.callback_func = "{}.{}".format( callback_func.__module__, callback_func.__name__ )
        e.args =  json.dumps( kwargs )

        e.save()
    except Exception as e:
        logging.log( logging.FATAL, "%d.%03d Failed to register callback %s() to be run at %d (%d.%d)", *UTILS.from_soldays( thisApp.solday ), callback_func, when, *UTILS.from_soldays( when ) )


def invoke_callbacks( ):

    logging.info( '%d.%03d Processing scheduled events', *UTILS.from_soldays( thisApp.solday ) )

    query = MODELS.Event.select(
        MODELS.Event.callback_func,
        MODELS.Event.idx,
        MODELS.Event.args
    ).filter(
        ( MODELS.Event.simulation_id == thisApp.simulation ) &
        ( MODELS.Event.when == thisApp.solday )
    )

    for row in query.execute():

        logging.log( logging.DEBUG, '%d.%03d   Processing event %s()', *UTILS.from_soldays( thisApp.solday ), row.callback_func )

        try:

            mod_name, func_name = row.callback_func.rsplit('.',1)

            mod = importlib.import_module(mod_name)

            kwargs = json.loads( row.args )

            kwargs['idx'] = row.idx

            func = getattr(mod, func_name)

            logging.log( thisApp.DETAILS, "%d.%03d Invoking callback %s( %s )", *UTILS.from_soldays( thisApp.solday ), row.callback_func, kwargs )

            result = func( **kwargs )

        except Exception as e:
            logging.error( '%d.%03d Failure during invocation of event callback %s(): %s )', *UTILS.from_soldays( thisApp.solday ), row.callback_func, str(e) )





