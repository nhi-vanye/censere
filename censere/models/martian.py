# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 17:30:50 2019

@author: matej
Completely re-written November 2019: Richard Offer
"""

# Module governing the attributes of the settlers

from censere.config import Generator as thisApp

import censere.utils.random as RANDOM

import censere.db as DB


from .settler import Settler as Settler
from .settler import LocationEnum as LocationEnum

from .names import get_random_male_first_name
from .names import get_random_female_first_name

## 
# class Martian
#
# Someone who was born on Mars
#
class Martian(Settler):
    
    class Meta:
        database = DB.db

        table_name = 'settlers'
    
    def initialize(self, solday, sex=None, config=None):

        self.settler_id = RANDOM.id()

        self.simulation = thisApp.simulation

        # might want to bias Astronaut sex beyond 50:50
        if sex == None:
            self.sex = RANDOM.choices( [ 'm', 'f'], [int(i) for i in thisApp.martian_gender_ratio.split(",") ] )[0]
        else:
            self.sex = sex

        if self.sex == 'm':
            self.first_name = get_random_male_first_name()

            self.orientation = RANDOM.choices( [ 'f', 'm', 'mf' ], [int(i) for i in thisApp.orientation.split(",") ] )[0]

        else:
            self.first_name = get_random_female_first_name()

            self.orientation = RANDOM.choices( [ 'm', 'f', 'mf' ], [int(i) for i in thisApp.orientation.split(",") ] )[0]

        # prefer lower case for all "enums"
        self.birth_location = LocationEnum.Mars

        self.current_location = LocationEnum.Mars


        # earth age in earth days converted to sols, then backdated from now
        self.birth_solday =  thisApp.solday

        self.productivity = 0

        ## These three need extra data - so update in the caller
        #
        # self.biological_father
        # self.biological_mother
        # self.family_name
