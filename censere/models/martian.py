# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 17:30:50 2019

@author: matej
"""

# Module gonverning the attributes of the colonists

import random
from random import randint

from .colonist import Colonist as Colonist

class Martian(Colonist):
    
    def __init__(self, params):
        Colonist.__init__(self, 0, random.choice(["m", "f"]), params)
        
    def getName(self):
        return "Martian"
