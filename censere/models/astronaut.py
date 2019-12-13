# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 17:30:50 2019

Original Concept: matej

Completely re-written November 2019: Richard Offer
"""

# Module gonverning the attributes of the settlers



from censere.config import Generator as thisApp

import censere.db as DB

import censere.utils as UTILS
import censere.utils.random as RANDOM

from .settler import Settler as Settler
from .settler import LocationEnum as LocationEnum

from .names import get_random_male_first_name
from .names import get_random_female_first_name
from .names import get_random_family_name

class Astronaut(Settler):

    class Meta:
        database = DB.db

        table_name = 'settlers'
    
    def initialize(self, solday, sex=None, config=None):

        if config == None:
            config = thisApp

        self.settler_id = RANDOM.id()

        self.simulation = config.simulation

        # might want to bias Astronaut sex beyond 50:50
        if sex == None:
            self.sex = RANDOM.choices( [ 'm', 'f'], [int(i) for i in thisApp.astronaut_gender_ratio.split(",") ] )[0]
        else:
            self.sex = sex

        if self.sex == 'm':
            self.first_name = get_random_male_first_name()

            # \TODO straight:homosexual:bisexual = 90:6:4 
            self.orientation = RANDOM.choices( [ 'f', 'm', 'mf' ], [int(i) for i in thisApp.orientation.split(",") ] )[0]

        else:
            self.first_name = get_random_female_first_name()

            self.orientation = RANDOM.choices( [ 'm', 'f', 'mf' ], [int(i) for i in thisApp.orientation.split(",") ] )[0]

        self.family_name = get_random_family_name()

        # prefer lower case for all strings (except names)
        self.birth_location = LocationEnum.Earth

        self.current_location = LocationEnum.Mars

        # add dummy biological parents to make consanguinity 
        # easier (no special cases)
        # There is an assumption that astronauts are not 
        # related to any earlier astronaut
        self.biological_father = RANDOM.id()
        self.biological_mother = RANDOM.id()

        # age min and max
        age_range = [int(i) for i in thisApp.astronaut_age_range.split(",") ]

        # earth age in earth days converted to sols, then backdated from now
        self.birth_solday =  solday - ( 
            UTILS.years_to_sols( RANDOM.randrange( age_range[0], age_range[1] ) ) )

        self.productivity = 100

