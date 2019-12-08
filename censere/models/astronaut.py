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
from .colonist import LocationEnum as LocationEnum

from .names import get_random_male_first_name
from .names import get_random_female_first_name
from .names import get_random_family_name

class Astronaut(Colonist):

    class Meta:
        database = DB.db

        table_name = 'colonists'
    
    def initialize(self, solday, sex=None, config=None):

        if config == None:
            config = thisApp

        self.colonist_id = str(uuid.uuid4())

        self.simulation = config.simulation

        # might want to bias Astronaut sex beyond 50:50
        if sex == None:
            self.sex = random.choices( [ 'm', 'f'], [50, 50] )[0]
        else:
            self.sex = sex

        if self.sex == 'm':
            self.first_name = get_random_male_first_name()

            # \TODO straight:homosexual:bisexual = 90:6:4 
            self.orientation = random.choices( [ 'f', 'm', 'mf' ], [ 90, 6, 4 ] )[0]

        else:
            self.first_name = get_random_female_first_name()

            self.orientation = random.choices( [ 'm', 'f', 'mf' ], [ 90, 6, 4 ] )[0]

        self.family_name = get_random_family_name()

        # prefer lower case for all strings (except names)
        self.birth_location = LocationEnum.Earth

        self.current_location = LocationEnum.Mars

        # add dummy biological parents to make consanguinity 
        # easier (no special cases)
        # There is an assumption that astronauts are not 
        # related to any earlier astronaut
        self.biological_father = str(uuid.uuid4())
        self.biological_mother = str(uuid.uuid4())

        # earth age in earth days converted to sols, then backdated from now
        self.birth_solday =  solday - ( 
            UTILS.years_to_sols( random.choice( config.astronaut_age_range.split(",") ) ) )

        self.productivity = 100

