from collections import deque
from math import floor, ceil, inf
import time
import logging
from flask import flash

logger = logging.getLogger(__name__)

def week_sum(D,week):
    """ return a week's sum from a dictionary of lists of weekly values """
    return sum([x[week] for x in D.values()])


def dict_key_with_min_val(d,week):
    """ return the dictionary key with the min value for a given week """
    v = [x[week] for x in d.values()]
    k = list(d.keys())
    return k[v.index(min(v))]


def dict_key_with_max_val(d,week):
    """ return the dictionary key with the max value for a given week """
    v = [x[week] for x in d.values()]
    k = list(d.keys())
    return k[v.index(max(v))]



class Demand():
    """ A class defining demand in the beer game
    Attributes:
    Methods:
    """

    __MAX_NODE_SUPPLIERS = 4

    def __init__(self,game,config):
        self.game = game
        self.station_name = config['name']
        self.player_name = 'Demand'

        # set default values
        self.demand = [4]*5 + [8]*(game.weeks-5)

        # initialize variables
        self.inbound = {}
        self.customers = []
        self.suppliers = []

        # setting available config values
        for k,v in config.items():
            setattr(self,k.lower(),v)

        self.last_communication_time = 0  # provided only for compatibility with station class interface

    def reset(self):
        for s in self.suppliers:
            self.inbound[s.station_name] = [0] * self.game.weeks

    def get_config(self):
        data = {}
        for x in ['name','demand']:
            data[x] = getattr(self,x,'')
        return data

    def add_supplier(self,supplier):  # its okay to have multiple suppliers to the same demand point; they all will receive identical demand, and each will need to satisfy the full demand on its own
        if len(self.suppliers) == self.__MAX_NODE_SUPPLIERS:
            raise ValueError('Too many supplier connections per node ({:}), max is {:}, check game ({:}) settings data (Connections)'.format(self.station_name,self.__MAX_NODE_SUPPLIERS,self.game.team_name))
        self.suppliers.extend([supplier])
        self.inbound[supplier.station_name] = []

    def receive_product(self,name,shipment):
        self.inbound[name].append(shipment)

    def initialize_week(self,week):
        for x in self.suppliers:  # transmit POs
            x.receive_po(self.station_name,self.demand[week],week)


def connect_stations(A: Station, B: Station):
    if type(A) is Demand :
        raise ValueError('Demand point ({:}) cannot have customers. Check game ({:}) settings data (Connections)'.format(A.station_name, A.game.team_name))
    else:
        A.add_customer(B)
        B.add_supplier(A)