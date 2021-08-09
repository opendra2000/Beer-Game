from . import stations
import time

# WTF IS ALL OF THIS GUYS?
def currency(value):
    """ format number as currency """
    if value == 0:
        return ' ' * 7 + '-'
    else:
        return '{:>8}'.format('${:.0f}'.format(value))


def percent(value):
    """ format number as percent """
    if value == 0:
        return ' ' * 7 + '-'
    else:
        return '{:>8}'.format('{:.1f}%'.format(value*100))


def combine_weekly(D):
    """combine a dictionary with weekly values into a single list"""
    if len(D) > 1:
        return [sum(y) for y in zip(*D.values())]
    else:
        return list(D.values())[0]


class Game(object):
    """ A game class for the Beer Game
    Attributes:
    Methods:
    """

    def __init__(self,config):
        # initialize variables
        self.network_stations = {}
        self.manual_stations_names = []
        self.auto_stations_names = []
        self.demand_stations_names = []
# ensure required config attributes exist
        config_keys = [x.lower() for x in config.keys()]
        if 'team_name' not in config_keys:
            raise ValueError('Game missing team_name attribute')
        for x in ['admin_password','play_password','weeks','stations','demands','connections']:
            if x not in config_keys:
                raise ValueError(config_keys['team_name'] + ': missing game config attrib: '+x)

        # set default values
        self.quick_backorder_recovery = False  # auto order method parameter: True or False
        self.expiry = 365  # game expiry in days
        self.turn_time = 90 
        self.script = []

        # setting available config values
        for k,v in config.items():
            if k.lower() not in ['stations','demands','connections']:
                setattr(self,k.lower(),v)

        for x in config['stations']:
            if x['name'] in self.network_stations.keys():
                raise ValueError(self.team_name + ': game includes at least two stations with the same name')
            self.network_stations[x['name']] = stations.Station(game=self,config=x)
            if x['auto_decide_order_qty'] and x['auto_decide_ship_qty']:
                self.auto_stations_names.append(x['name'])
            else:
                self.manual_stations_names.append(x['name'])
        for x in config['demands']:
            if x['name'] in self.network_stations.keys():
                raise ValueError(self.team_name + ': game includes at least two stations with the same name')
            self.network_stations[x['name']] = stations.Demand(game=self,config=x)
            self.demand_stations_names.append(x['name'])
        for x in config['connections']:
            stations.connect_stations(self.network_stations[x['supp']],
                                      self.network_stations[x['cust']])
        for x in self.network_stations.values():  # handle end_nodes
            x.check_endnode()

        # check for circular reference and diconnected segments
        self.Check_Network()

        # initialize variables
        self.network_walk = self.GenerateNetworkWalk()


        self.kpi_cost = {'inventory':[0] * self.weeks, 'backorder':[0] * self.weeks, 'total':[0] * self.weeks}

        self.players_completed_turn = 0
        self.connected_stations = 0
        self.current_week = 0
        self.turn_start_time = 0
        self.game_done = False
        self.created = time.time()
for x in self.network_walk:  # initialize the first week
            self.network_stations[x].initialize_week(0)

def reset(self):
        self.kpi_cost = {'inventory':[0] * self.weeks, 'backorder':[0] * self.weeks, 'total':[0] * self.weeks}
        self.players_completed_turn = 0
        self.connected_stations = 0
        self.current_week = 0
        self.turn_start_time = 0
        self.game_done = False

        for x in self.network_stations:
            self.network_stations[x].reset()

        for x in self.network_walk:  # initialize the first week
            self.network_stations[x].initialize_week(0)

def get_config(self):
        data = {}
        for x in ['team_name', 'admin_password', 'play_password', 'weeks', 'expiry','turn_time', 'quick_backorder_recovery','script']:
            data[x] = getattr(self,x,'')
        data['stations'] = []
        for x in self.manual_stations_names:
            data['stations'].append(self.network_stations[x].get_config())
        for x in self.auto_stations_names:
            data['stations'].append(self.network_stations[x].get_config())
        data['demands'] = []
        for x in self.demand_stations_names:
            data['demands'].append(self.network_stations[x].get_config())
        data['connections'] = []
        for x in self.network_walk:
            for s in self.network_stations[x].suppliers:
                data['connections'].append({"supp":s.station_name,"cust":x})
        return data
def Check_Network(self):
        """ Deapth First Search to check for circular reference and network segmentation"""
        visited = set()
        for D in self.demand_stations_names:
            visited.add(D)
            path = list()
            path.append(D)
            self.Network_Check_Follow(D, path, visited)
        remaining = set(self.auto_stations_names + self.manual_stations_names + self.demand_stations_names) - visited
        if len(remaining) > 0:
            raise ValueError(self.team_name + ': game network not fully connected, unconnected nodes: ' + str(remaining))

def Network_Check_Follow(self,node,path,visited):
        """ recursively walk a demand supply chain to check for circular reference"""
        for S in [x.station_name for x in self.network_stations[node].suppliers]:
            if S in path:
                raise ValueError(self.team_name + ': found circular reference in game supply chain: ' + S + ' -> ' + ' -> '.join(path[::-1]))
            else:
                visited.add(S)
                tmp = path.copy()
                tmp.append(S)
                self.Network_Check_Follow(S, tmp, visited)

def GenerateNetworkWalk(self):
        """ generate an ordered list of the supply chain station according to their customer-supplier relationships"""
        netwalk = self.demand_stations_names.copy()  # start with demand nodes
        all_stations = self.auto_stations_names + self.manual_stations_names + self.demand_stations_names
        DONE = False
        while not DONE:
            tmp = [x for x in all_stations if x not in netwalk]
            for x in tmp:
                customers = [y.station_name for y in self.network_stations[x].customers]
                if set(customers).issubset(netwalk):
                    netwalk.append(x)
            if tmp == []:
                DONE = True
        return netwalk

def StepOneWeek(self,week):
        n = 0
        for node_name in self.network_walk:
            node = self.network_stations[node_name]
            node.process(week)
            if node_name not in self.demand_stations_names:
                n += 1
                self.kpi_cost['inventory'][week] += node.kpi_weeklycost_inventory[week]
                self.kpi_cost['backorder'][week] += node.kpi_weeklycost_backorder[week]
                self.kpi_cost['total'][week] += node.kpi_total_cost[week]
        if n > 0:
                self.players_completed_turn = 0
                self.current_week += 1
        if week < self.weeks-1:
            for x in self.network_walk:  # initialize the first week
                self.network_stations[x].initialize_week(week+1)  # prep for the next week
        else:
            self.game_done = True
        self.turn_start_time = time.time()

def Run(self):
        if not self.game_done:
            for week in range(self.weeks):
                self.StepOneWeek(week)
            return True
        else:
            return False

def SetPlayerTurnData(self, station_name, week, suppliers_orders, custoemrs_shipments):
        if self.network_stations[station_name].set_player_order_and_shipment(week,suppliers_orders,customers_shipments):
            self.players_completed_turn += 1
            if self.players_completed_turn == len(self.manual_stations_names):
                self.StepOneWeek(week)

def Debug_Report(self):
        if self.current_week == 0:
            return 'First week not completed yet.'

        report_txt = ''
        for y in self.network_walk:
            x = self.network_stations[y]
            if y in self.demand_stations_names:
                report_txt += '{:}'.format(x.station_name) + '\n'
                report_txt += 'Suppliers: {:}'.format(', '.join([str(y.station_name) for y in x.suppliers])) + '\n'
                report_txt += ' WK ' + '{:>6} '.format('Demand') + ' '.join(['{:>7}'.format('inbound') for y in x.inbound.keys()]) + '\n'
                for week in range(self.weeks):
                    if week < self.current_week:
                        report_txt += '{:3} {:6} '.format(week+1,x.demand[week]) + ' '.join(['{:7}'.format(y[week]) for y in x.inbound.values()]) + '\n'
                    else:
                        report_txt += '{:3} {:6} '.format(week+1,x.demand[week]) + '\n'
                report_txt += '\n'
            else:
                report_txt += '{:} ({:})'.format(x.station_name,x.player_name) + '\n'
                report_txt += 'Auto order qty: {:}'.format(x.auto_decide_order_qty) + '\n'
                report_txt += ' Auto ship qty: {:}'.format(x.auto_decide_ship_qty) + '\n'
                report_txt += 'Backorder cost: {:}'.format(x.backorder_cost) + '\n'
                report_txt += 'Init. que. val: {:}'.format(x.initial_queue_quantity) + '\n'
                report_txt += 'Init.inventory: {:}'.format(x.initial_inventory) + '\n'
                report_txt += 'Shipping delay: {:}'.format(x.delay_shipping) + '\n'
                report_txt += '     Customers: {:}'.format(', '.join([str(y.station_name) for y in x.customers])) + '\n'
                report_txt += '     Suppliers: {:}'.format(', '.join([str(y.station_name) for y in x.suppliers])) + '\n'
                report_txt += 'Order min: {:}'.format(x.order_min) + '\n'
                report_txt += 'Order max: {:}'.format(x.order_max) + '\n'
                report_txt += ' Ship min: {:}'.format(x.ship_min) + '\n'
                report_txt += ' Ship max: {:}'.format(x.ship_max) + '\n'
                report_txt += ' Wk ' + \
                    'Fullfill ' + \
                    'TruckUtl ' + \
                    'Invntroy ' + \
                    'BakOrder ' + \
                    'Transprt ' + \
                    'TotlCost ' + \
                    ' '.join(['{:>8}'.format('Inbound') for y in x.inbound.keys()]) + ' ' + \
                    ' '.join(['{:>8}'.format('RecvedPO') for y in x.received_po.keys()]) + ' ' + \
                    ' '.join(['{:>8}'.format('Outbound') for y in x.outbound.keys()]) + ' ' + \
                    ' '.join(['{:>8}'.format('SentPO') for y in x.sent_po.keys()]) + ' ' + \
                    ' '.join(['{:>8}'.format('OutStand') for y in x.outstanding_orders_to_suppliers.keys()]) + ' ' + \
                    'Invntroy ' + \
                    ' '.join(['{:>8}'.format('BakOrder') for y in x.backorder.keys()]) + '\n'
                for week in range(self.weeks):
                    if week > self.current_week:
                        report_txt += '{:3}\n'.format(week+1)
                    else:
                        report_txt += '{:3} {:} {:} {:} {:} {:} {:} '.format(week+1,
                                                                         
                                                                             currency(x.kpi_weeklycost_inventory[week]),
                                                                             currency(x.kpi_weeklycost_backorder[week]),
                                                                             currency(x.kpi_total_cost[week])) + \
                            ' '.join(['{:>8}'.format(y[week]) for y in x.inbound.values()]) + ' ' + \
                            ' '.join(['{:>8}'.format(y[week]) for y in x.received_po.values()]) + ' ' + \
                            ' '.join(['{:>8}'.format(y[week]) for y in x.outbound.values()]) + ' ' + \
                            ' '.join(['{:>8}'.format(y[week]) for y in x.sent_po.values()]) + ' ' + \
                            ' '.join(['{:>8}'.format(y[week]) for y in x.outstanding_orders_to_suppliers.values()]) + ' ' + \
                            '{:8d}'.format(x.inventory[week]) + ' ' + \
                            ' '.join(['{:>8}'.format(y[week]) for y in x.backorder.values()]) + '\n'
                report_txt += '\n'

        w = self.current_week
        report_txt += '{:20}'.format('Station summary') + '\n'
        report_txt += '*'*20 + '\n'
        report_txt += '{:>20} {:} {:} {:} {:} {:} {:} {:}'.format('Station','Invntory','BakOrder','TotlCost') + '\n'
        for y in self.network_walk:
            x = self.network_stations[y]
            if type(x) is not stations.Demand:
                report_txt += '{:>20} {:} {:} {:} {:} {:} {:} {:8d}'.format(y,
                                                                            currency(sum(x.kpi_weeklycost_inventory)),
                                                                            currency(sum(x.kpi_weeklycost_backorder)),
                                                                            currency(sum(x.kpi_total_cost)),
                                                                            sum(x.kpi_shipment_trucks)) + '\n'
        report_txt += '\n'

        report_txt += 'Beer Game Report' + '\n'
        report_txt += '*'*25 + '\n'
        report_txt += '{:>25} {:}'.format('Team name:',self.team_name) + '\n'
        report_txt += '{:>25} {:8d}'.format('# of weeks:',self.weeks) + '\n'
        report_txt += '{:>25} {:}'.format('Inventory cost:',currency(sum(self.kpi_cost['inventory']))) + '\n'
        report_txt += '{:>25} {:}'.format('Backorder cost:',currency(sum(self.kpi_cost['backorder']))) + '\n'
        report_txt += '{:>25} {:}'.format('Total cost:',currency(sum(self.kpi_cost['total']))) + '\n'
        report_txt += '{:>25} {:}'.format('Average cost:',currency(sum(self.kpi_cost['total'])/self.weeks)) + '\n'

        return report_txt

