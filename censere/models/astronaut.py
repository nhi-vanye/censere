# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 17:30:50 2019

Original Concept: matej

Completely re-written November 2019: Richard Offer
"""

# Module governing the attributes of the settlers

import logging

import censere.db as DB
import censere.utils.random as RANDOM
from censere.config import thisApp

from .names import (
    get_random_family_name,
    get_random_female_first_name,
    get_random_male_first_name,
)
from .settler import LocationEnum as LocationEnum
from .settler import Settler as Settler


class Astronaut(Settler):

    class Meta:
        database = DB.db

        table_name = 'settlers'

    def initialize(self, solday, sex=None, config=None):

        if config == None:
            config = thisApp

        try:
            self.settler_id = RANDOM.id()
        except Exception as e:
            logging.error( 'Failed to set settler_id')

        self.simulation_id = config.simulation

        # might want to bias Astronaut sex beyond 50:50
        try:
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

        except Exception as e:
            logging.error( f'Failed to set sex and first name: {str(e)}')

        try:
            self.family_name = get_random_family_name()
        except Exception as e:
            logging.error( 'Failed to set family_name')

        # prefer lower case for all strings (except names)
        self.birth_location = LocationEnum.Earth

        self.current_location = LocationEnum.Mars

        # add dummy biological parents to make consanguinity
        # easier (no special cases)
        # There is an assumption that astronauts are not
        # related to any earlier astronaut
        self.biological_father = RANDOM.id()
        self.biological_mother = RANDOM.id()

        # earth age in earth days converted to sols, then backdated from now
        try:
            self.birth_solday =  solday - RANDOM.parse_random_value( thisApp.astronaut_age_range, key_in_earth_years=True )
        except Exception as e:
            logging.error( 'Failed to set birth_solday %s',thisApp.astronaut_age_range )

        self.cohort = solday

        self.productivity = 100
