# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 17:30:50 2019

@author: matej
"""

# Module gonverning the attributes of the colonists

import random
import uuid

from censere.config import Generator as thisApp

import censere.db as DB


from .colonist import Colonist as Colonist

from .names import get_random_male_first_name
from .names import get_random_female_first_name

class Martian(Colonist):
    
    class Meta:
        database = DB.db

        table_name = 'colonists'
    
    def initialize(self, solday):

        self.colonist_id = str(uuid.uuid4())

        self.simulation = thisApp.simulation

        # might want to bias Astronaut sex beyond 50:50
        self.sex = random.choices( [ 'm', 'f'], [50, 50] )[0]

        if self.sex == 'm':
            self.first_name = get_random_male_first_name()

            # \TODO straight:homosexual:bisexual = 90:6:4 
            self.orientation = random.choices( [ 'f', 'm', 'mf' ], [ 90, 6, 4 ] )[0]

        else:
            self.first_name = get_random_female_first_name()

            self.orientation = random.choices( [ 'm', 'f', 'mf' ], [ 90, 6, 4 ] )[0]

        # prefer lower case for all "enums"
        self.birth_location = 'mars'


        # earth age in earth days converted to sols, then backdated from now
        self.birth_solday =  thisApp.solday

        self.productivity = 0

        ## These three need extra data - so update in the caller
        #
        # self.biological_father
        # self.biological_mother
        # self.family_name
