
# -*- coding: utf-8 -*-
"""

@author: Richard Offer
"""

# Module governing the attributes of all physical commodities

import sys

import peewee
import playhouse.signals
import playhouse.apsw_ext as APSW

from censere.config import thisApp, current_solday, current_simulation

import censere.db as DB
import censere.utils.random as RANDOM

class Resource():
    Other = 'other'
    Electricity = 'electricity'
    O2 = 'o2'
    Water = 'water'
    Fuel = 'fuel'
    Food = 'food' # initially just calories
    # WIP
    Heating = 'heating' # TODO we should re-cycle waste heat to reduce Energy requirements
    Quarters = 'quarters' # TODO: living quarters, single, couples and  families

# notes for future use, not used yet
class EquipmentType():
    Other = 'other'
    Pump = 'pump'
    Tank = 'tank'
    Pipework = 'pipework'
    CO2Scrubber = 'scrubber'
    Vehicle = 'Vehicle'
    Computer = 'computer'
    Medical = 'medical'
    Sewage = 'sewage'
    Cooker = 'cooker'
    Refridgerator = 'fridge'
    AirCon = 'a/c'
    Heater = 'heater'
    PowerTools = 'powertools'


class CommodityType():
    Other = 'other'
    Resevoir = "resevoir"
    Supplier = "supplier"
    Consumer = "consumer"


commodity_counts = {}

##
class Commodity(playhouse.signals.Model):

    class Meta:
        database = DB.db

        table_name = 'commodities'

        indexes = (
            (('simulation_id', 'commodity_id'), True),
        )

    ## provide a internal representation function
    # to make debugging easier
    def __repr__(self):
        return "{} ({})".format( self.commodity, self.commodity_id ) 

    # Unique identifier for a single physical commodity
    commodity_id = APSW.CharField( 32, index=True, unique=True, primary_key=True )

    # allow the same database to be used for multple executions
    simulation_id = APSW.UUIDField( index=True, unique=False )

    # Human Name
    commodity = APSW.CharField( 16, default=Resource.Other )

    def initialize(self, commodity=Resource.Other ):

        self.simulation_id = thisApp.simulation
        self.commodity_id = RANDOM.id()

        self.commodity = commodity


class CommodityResevoir(playhouse.signals.Model):
    """
    A CommodityResevoir is a 'pure' storage container, it does not generate or consume
    any of its resource. But it does store how much of the resource is available
    on a Sol basis...

    'Suppliers' feed into the Resevoir, 'Consumers' get their resource from the Resevoir.

    There may be multiple stores for a given resource

    TODO: if there are multiple then it would make sence to distribute
    filling and depleting the stores non-equally. Thats for later.
    For now, its symetrica
    """

    class Meta:
        database = DB.db

        table_name = 'commodity_resevoirs'

        indexes = (
            (('simulation_id', 'commodity_id', 'store_id'), True),
        )

    def __str__(self):
        return "CommodityResevoir:{} ({}) on %d %f".format( self.name, self.store_id, self.solday, self.current_capacity ) 

    store_id = APSW.CharField( 32, index=True, unique=False )

    name = APSW.CharField( null=True )

    commodity_id = APSW.CharField( 32, index=True, unique=False )
    commodity = APSW.CharField( null=True)

    simulation_id = APSW.UUIDField( index=True, unique=False )

    availability = APSW.CharField( default="randint:1,1", null=True)

    # current status - updated by external availability callbacks
    is_online = APSW.BooleanField( default=True )

    description = APSW.CharField( null=True)

    # could use DB constraints to limit, but its easier at the application
    # so we don't have to handle database exceptions
    initial_capacity = APSW.FloatField( default=0.0 )
    max_capacity = APSW.FloatField( default=0.0)

    def initialize(self, max_capacity, initial_capacity=0.0, commodity=Resource.Other, description="" ):
        self.simulation_id = thisApp.simulation

        self.commodity_id = thisApp.commodity_ids[commodity]
        self.commodity = commodity

        self.store_id = RANDOM.id()

        self.is_online = True

        if max_capacity == "":
            self.max_capacity = sys.float_info.max
        else:
            self.max_capacity = RANDOM.parse_random_value(max_capacity)

        self.initial_capacity = min(self.max_capacity,
                                    RANDOM.parse_random_value(initial_capacity) )

        global commodity_counts

        if description:
            idx = description
        else:
            idx = f"{commodity}-resevoir"

        if idx not in commodity_counts:
            commodity_counts[idx] = 1

        self.name = f"{idx}-{commodity_counts[idx]:03d}"
        self.description = description

        commodity_counts[idx] += 1


class CommoditySupplier(playhouse.signals.Model):

    class Meta:
        database = DB.db

        table_name = 'commodity_suppliers'

        indexes = (
            (('simulation_id', 'commodity_id', 'supplier_id'), True),
        )

    supplier_id = APSW.CharField( 32, index=True, unique=True, primary_key=True )

    name = APSW.CharField( )

    commodity_id = APSW.CharField( 32, index=True, unique=False )
    commodity = APSW.CharField( null=True)

    simulation_id = APSW.UUIDField( index=True, unique=False )

    availability = APSW.CharField( default="randint:1,1", null=True)

    # current status - updated by external availability callbacks
    is_online = APSW.BooleanField( default=True )

    description = APSW.CharField( null=True)

    # we store the model i.e. randint:1,4 not the calculated
    # value to make it dynamic
    supplies = APSW.CharField( default="randint:0,0" )

    def initialize(self, supplies, commodity=Resource.Other, description="" ):

        self.simulation_id = thisApp.simulation
        self.commodity_id = thisApp.commodity_ids[commodity]
        self.commodity = commodity

        self.supplier_id = RANDOM.id()

        self.supplies = supplies

        global commodity_counts

        if description:
            idx = description
        else:
            idx = f"{commodity}-supplier"

        if idx not in commodity_counts:
            commodity_counts[idx] = 1

        self.name = f"{idx}-{commodity_counts[idx]:03d}"
        self.description = description

        commodity_counts[idx] += 1


class CommodityConsumer(playhouse.signals.Model):

    class Meta:
        database = DB.db

        table_name = 'commodity_consumers'

        indexes = (
            (('simulation_id', 'commodity_id', 'consumer_id'), True),
        )

    consumer_id = APSW.CharField( 32, index=True, unique=True, primary_key=True )

    name = APSW.CharField( )

    commodity_id = APSW.CharField( 32, index=True, unique=False )
    commodity = APSW.CharField( null=True)

    simulation_id = APSW.UUIDField( index=True, unique=False )

    availability = APSW.CharField( default="randint:1,1", null=True)

    # current status - updated by external availability callbacks
    is_online = APSW.BooleanField( default=True )

    description = APSW.CharField( null=True)

    # we store the model i.e. randint:1,4 not the calculated
    # value to make it dynamic
    consumes = APSW.CharField( default="randint:0,0" )

    # if True, consumes is per-settler so multiply by living population
    is_per_settler = APSW.BooleanField( 12 )

    def initialize(self, consumes, commodity=Resource.Other, description="" ):

        self.simulation_id = thisApp.simulation
        self.commodity_id = thisApp.commodity_ids[commodity]
        self.commodity = commodity

        self.consumer_id = RANDOM.id()

        self.consumes = consumes

        self.is_settler = False

        global commodity_counts

        if description:
            idx = description
        else:
            idx = f"{commodity}-consumer"

        if idx not in commodity_counts:
            commodity_counts[idx] = 1

        self.name = f"{idx}-{commodity_counts[idx]:03d}"
        self.description = description

        commodity_counts[idx] += 1


##
# consumption and supply on a per-commodity and per sol basis
class CommodityUsage(playhouse.signals.Model):

    class Meta:
        database = DB.db

        table_name = 'commodity_activity'

        indexes = (
            (('simulation_id', 'commodity_id', 'key_id', 'solday' ), True),
        )

    ## provide a internal representation function
    # to make debugging easier
    def __repr__(self):
        return "{} ({})".format( self.commodity_type, self.commodity_id ) 

    # allow the same database to be used for multple executions
    simulation_id = APSW.UUIDField( index=True, unique=False )

    commodity = APSW.CharField( 16, default="other" )

    commodity_id = APSW.CharField( 32, index=True, unique=False )

    # Link back to the balance / credit /debit 
    key_type = APSW.CharField(32 )
    key_id = APSW.CharField(32, index=True, unique=False )

    is_online = APSW.BooleanField( default=True)

    # name corresponding to key_id
    name = APSW.CharField( 16, default="other" )

    solday = APSW.IntegerField()

    debit = APSW.FloatField( default=0.0, null=True)
    credit = APSW.FloatField( default=0.0, null=True)

    def initialize(self, commodity, commodity_id, debit=None, credit=None ):

        self.commodity = commodity

        self.commodity_id = commodity_id

        if debit:
            self.debit = debit

        if credit:
            self.credit = credit

        is_online = True

class CommodityResevoirCapacity(playhouse.signals.Model):

    class Meta:
        database = DB.db

        table_name = 'commodity_resevoir_storage'

        indexes = (
            (('simulation_id', 'store_id', 'solday'), True),
        )

    def __str__(self):
        return "CommodityResevoirCapacity:{} on {} {}".format( self.store_id, self.solday, self.capacity ) 

    store_id = APSW.CharField( 32, index=True, unique=False )

    simulation_id = APSW.UUIDField( index=True, unique=False )

    commodity = APSW.CharField( 32, index=True, unique=False )
    commodity_id = APSW.CharField( 32, index=True, unique=False )

    solday = APSW.IntegerField()

    capacity = APSW.FloatField( default=0.0 )

    is_online = APSW.BooleanField( default=True)

    def initialize(self, store_id, commodity, commodity_id, capacity=0.0 ):

        self.simulation_id = thisApp.simulation

        self.store_id = store_id

        self.commodity = commodity
        self.commodity_id = commodity_id

        self.capacity = capacity


