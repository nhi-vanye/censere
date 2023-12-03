
import importlib
import json

import censere.db as DB
import censere.models as MODELS
import censere.utils as UTILS
from censere import LOGGER
from censere.config import thisApp


##
# \param when - absolute solday to execute the function.
# \param callback_func - fully qualified function
def register_callback( runon=0, priority=20, periodic=0, name="", callback_func=None, kwargs=None ):

    ( year, sol ) = UTILS.from_soldays( thisApp.solday )

    if callback_func == None:

        LOGGER.error( f"Missing required arguments in call to register_callback( runon={runon}, callback={callback_func} {kwargs})")

        return

    runon = int(runon)
    (runon_yr, runon_sol) = UTILS.from_soldays( runon )

    if periodic == 0:

        LOGGER.info( f"{year}.{sol:03d} Registering {callback_func.__name__}() to be run once on Sol {runon} ({runon_yr}.{runon_sol:03d})")
    else:
        LOGGER.info( f"{year}.{sol:03d} Registering {callback_func.__name__}() to be run every {periodic} Sols starting on {runon} ({runon_yr}.{runon_sol:03d})" )

    try:
        idx = MODELS.Event.select().where(
            ( MODELS.Event.simulation_id == thisApp.simulation ) &
            ( MODELS.Event.runon == runon ) &
            ( MODELS.Event.callback_func == "{}.{}".format( callback_func.__module__, callback_func.__name__ ) )
        ).count()

        e = MODELS.Event()

        e.simulation_id = thisApp.simulation
        e.registered = thisApp.solday
        e.runon = runon
        e.priority = priority
        e.periodic = periodic
        e.idx = idx
        # This allows us to pass a real function into the register function (rather then a string)
        # but store the full name of the function for later execution
        e.callback_func = "{}.{}".format( callback_func.__module__, callback_func.__name__ )
        e.args =  json.dumps( kwargs )

        e.save()
    except Exception as e:
        LOGGER.critical( f"{year}.{sol:03d} Failed to register {callback_func}() to be run at {runon} ({runon_yr}.{runon_sol:03d})" )
        LOGGER.error( str(e))


def invoke_callbacks( ):
    """Invoke callbacks register for the current Sol day"""

    ( year, sol ) = UTILS.from_soldays( thisApp.solday )

    LOGGER.info( f'{year}.{sol:03d} Processing scheduled events' )

    query = MODELS.Event.select(
        MODELS.Event.callback_func,
        MODELS.Event.idx,
        MODELS.Event.args
    ).filter(
        ( MODELS.Event.simulation_id == thisApp.simulation ) &
        (
          ( MODELS.Event.runon == thisApp.solday ) | ( thisApp.solday > MODELS.Event.runon ) & ( ( MODELS.Event.periodic > 0 ) & ( DB.mod(thisApp.solday, MODELS.Event.periodic) == 0 ) )
        )
    ).order_by(
        MODELS.Event.priority,
        MODELS.Event.id,
        MODELS.Event.idx
    )

    for row in query.execute():

        try:
            mod_name, func_name = row.callback_func.rsplit('.',1)

            LOGGER.info( f'{year}.{sol:03d}   Calling {func_name}()' )

            mod = importlib.import_module(mod_name)

            kwargs = json.loads( row.args )

            kwargs['idx'] = row.idx

            func = getattr(mod, func_name)

            LOGGER.debug( f"{year}.{sol:03d}     {row.callback_func}( {kwargs} )" )

            result = func( **kwargs )

        except Exception as e:
            LOGGER.exception( f'{year}.{sol:03d} Failure during invocation of event callback {row.callback_func}(): )' )
