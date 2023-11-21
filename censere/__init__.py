#
# Copyright (c) 2023 Richard Offer, All rights reserved.
import os.path
import traceback
import logging

BORING_FILES = [
    "peewee.py",        
    "core.py",          # click/core.py
    "__init__.py"       # this file and other boring ones
]

class AddStackFilter(logging.Filter):
    def __init__(self, levels=None):
        self.levels = levels or set()

    def get_stack(self):
        # Iterator over file names
        frames = traceback.walk_stack(None)

        interesting=[]

        # Walk up the frames
        for frame, lineno in frames:
            #if os.path.basename(frame.f_code.co_filename) not in BORING_FILES:
            if "site-packages" in frame.f_code.co_filename:
                pass
                # interesting.append( f"  ..." )
            elif "logging/__init__.py" in frame.f_code.co_filename:
                pass
                # interesting.append( f"  ..." )
            else:
                interesting.append( f"  {os.path.relpath(frame.f_code.co_filename)}:{frame.f_lineno}" )

        interesting.insert(0, 'Called from :')
        interesting.append("")

        return "\n".join(interesting)

    def filter(self, record):
        if record.levelno in self.levels:
            sinfo = self.get_stack()
            if sinfo is not None:
                record.stack_info = sinfo

        return True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "datefmt": "%m/%d/%Y %I:%M:%S %p",
    "formatters": {
        "cli": {
            "format": "%(asctime)s.%(msecs)03d %(levelname)-6s %(name)15s | %(message)s",
            "datefmt": "%H:%M:%S",
        },
        "devel": {
            "format": "%(asctime)s.%(msecs)03d %(funcName)s() %(filename)s:%(lineno)d  | %(message)s",
            "datefmt": "%H:%M:%S",
        },
        "trace": {
            "format": "%(asctime)s.%(msecs)03d %(levelname)-6s %(name)14s | %(message)s",
            "datefmt": "%H:%M:%S",
        },
        "peewee": {
            "format": "%(asctime)s.%(msecs)03d %(name)14s | %(message)s\n%(stack_info)s",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "cli": {
            "class": "logging.StreamHandler",
            "formatter": "cli",
            "stream"  : "ext://sys.stdout"
        },
        "devel": {
            "class": "logging.StreamHandler",
            "formatter": "devel",
            "stream"  : "ext://sys.stdout"
        },
        "trace": {
            "class": "logging.StreamHandler",
            "formatter": "trace",
            "stream"  : "ext://sys.stdout"
        },
        "peewee": {
            "class": "logging.StreamHandler",
            "formatter": "peewee",
            "stream"  : "ext://sys.stdout"
        },
    },
    "loggers": {
        "": {
            "level": "ERROR",
            "handlers": [ "cli" ]
        },
        "c": {
            "level": "DEBUG",
            "handlers": [ "cli" ],
            'propagate': True,
        },
        "c.cli": {
            "level": "DETAIL",
            "handlers": [ "cli" ],
            'propagate': False,
        },
        "c.cli.generator": {
            "level": "INFO",
            "handlers": [ "cli" ],
            'propagate': False,
        },
        "c.cli.dashboard": {
            "level": "INFO",
            "handlers": [ "cli" ],
            'propagate': False,
        },
        "c.a": {
            "level": "NOTICE",
            "handlers": [ "cli" ],
            'propagate': False,
        },
        "c.e": {
            "level": "NOTICE",
            "handlers": [ "cli" ],
            'propagate': False,
        },
        "c.m": {
            "level": "NOTICE",
            "handlers": [ "cli" ],
            'propagate': False,
        },
        "c.u": {
            "level": "NOTICE",
            "handlers": [ "cli" ],
            'propagate': False,
        },
        "d.devel": {
            "level": "INFO",
            "handlers": [ "devel" ],
            'propagate': False,
        },
        "d.trace": {
            "level": "INFO",
            "handlers": [ "trace" ],
            'propagate': False,
        },
        "peewee": {
            "level": "INFO",
            "handlers": [ "peewee" ],
            'propagate': False,
        },       
    },
}

