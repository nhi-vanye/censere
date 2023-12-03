#
# Copyright (c) 2023 Richard Offer, All rights reserved.

from loguru import logger

_loguru_cfg = { }
logger.configure( ** _loguru_cfg )

LOGGER = logger

def CONSOLE( msg, *args, **kwargs):
    """Standarize CLI output"""
    import datetime

    import click
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    click.secho(f'{timestamp} | {msg}', *args, **kwargs)


# Function wrapper for debugging...
def WRAP(*, entry=True, exit=True, level="TRACE"):
    import functools

    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, "Entering '{}(args={}, kwargs={})", name, args, kwargs)
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper
