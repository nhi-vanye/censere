# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 17:30:50 2019

@author: matej
"""

# Module gonverning the attributes of the colonists

import random
from random import randint

from .colonist import Colonist as Colonist

class Astronaut(Colonist):
    
    def __init__(self, sex, params):
        randage = randint(params.getASTRO_MIN_AGE(),params.getASTRO_MAX_AGE()) * 365
        Colonist.__init__(self, randage, sex, params)
        
    def getName(self):
        return "Astronaut"
    
