"""
==============================================================================
NETWORK TOPOLOGY
==============================================================================
DESCRIPTION
    This script defines the entities of the simulation, namely: plant, stores,
    and warehouse. It converts the cartesian grid into a network used for optm.
    delivery routes.

CREATED
    3/25/2018
    last modified: 4/1/2018 (Borela)

COLLABORATORS
    R. Borela
    S. Hanumasagar
    F. Liu
    N. Roy 
"""


# ADDED DAILY BASE COST FOR TRUCKS
# CHANGED TRUCK ATTRIBUTES NAMES


#import modules
import sys, os
from math import *
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

#===========
# I/O PATHS
input_path = ''

#=========================
# MISCELLANEOUS FUNCTIONS

# manhattan distance
def one_norm(A,B):
    return (abs(A.x-B.x)+abs(A.y-B.y))

#==========
# ENTITIES
class store:
    def __init__(self,id, x, y, capacity, min_stock, refill_pc, exp_sale):
        # identification        
        self.id=id
        # cartesian location
        self.x=x
        self.y=y
        # storage 
        self.capacity=capacity
        self.curr_stock=capacity
        self.min_stock=min_stock
        self.refill_pc=refill_pc
        # effective and missed sales
        self.eff_sales = []
        self.miss_sales = []
        # data model: sales exp. distribution parameter
        self.exp_sale=exp_sale

class warehouse:
    def __init__(self,id, x, y, capacity, min_stock,refill_pc,parent):
        # identification        
        self.id=id
        # cartesian location
        self.x=x
        self.y=y
        # storage 
        self.capacity=capacity
        self.curr_stock=capacity
        self.min_stock=min_stock
        self.refill_pc=refill_pc
        # production plant responsible for supply
        self.parent=parent

class plant:
    def __init__(self,id, x, y, capacity, prod_rate):
        # identification        
        self.id=id
        # cartesian location
        self.x=x
        self.y=y
        # storage 
        self.capacity=capacity
        self.curr_stock=capacity
        # production rate
        self.prod_rate=prod_rate

class truck:
    def __init__(self,id, capacity, actual_load, route, on_hold, base_cost, cost_per_mile, max_stores):
        # identification        
        self.id=id
        # capacity
        self.capacity=capacity
        # number of products carried
        self.actual_load=actual_load    #WHY DO WE NEED THIS-SANGY
        # route
        self.route=route
        # days truck is on hold
        self.on_hold = on_hold
        # daily cost of hiring a truck
        self.base_cost = base_cost
        # truck cost per mile traveled
        self.cost_per_mile = cost_per_mile
        # maximum number of stores 
        self.max_stores = max_stores
"""
>>>>>>>>> RESPONSE: to be able to calculate how much is spent on delivery per product
"""

#=========
# NETWORK

G=nx.Graph()

#=== NODES

# minimum percentage of capacity
min_percent = .0

# plants
P = [plant('P1',1.0,4.0,10000,100),
     plant('P2',6.0,1.0,10000,100)]

# warehouses
W = [warehouse('W1',4.0,3.0,650,int(min_percent*650),100,P[0]),
     warehouse('W2',9.0,2.0,650,int(min_percent*650),100,P[1])]

"""
REMOVED <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
"""
#T=[truck('T1',50,0,'',0,10,5)] #,truck('T2',50,0,'',0,10,20)] 
"""
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
"""


# get store info (id,x,y,capacity,exp_sales_coefficient)
store_info = np.loadtxt(os.path.join(input_path,'store_info.csv'),delimiter=",",skiprows=1)

# stores
S=[]

for index in range(np.shape(store_info)[0]):#range(0,10):
    S.append(store('S'+str(int(store_info[index,0])),
             store_info[index,1],
             store_info[index,2],
             int(store_info[index,3]), 
             int(store_info[index,3]*min_percent),
             100,
             store_info[index,4]))

# add all nodes to graph
for entity in P+W+S:
    G.add_node((entity.x,entity.y))

#=== EDGES

# path from plant to warehouse
G.add_edge((W[0].x,W[0].y),(W[0].parent.x,W[0].parent.y),length=one_norm(W[0].parent,W[0]))
G.add_edge((W[1].x,W[1].y),(W[1].parent.x,W[1].parent.y),length=one_norm(W[1].parent,W[1]))


# paths between stores and warehouses
W_n_S = W+S
for index in range(len(W_n_S)):
    for neighbor_index in range(index+1,len(W_n_S)):
        G.add_edge((W_n_S[index].x, W_n_S[index].y),(W_n_S[neighbor_index].x,W_n_S[neighbor_index].y),length=one_norm(W_n_S[index],W_n_S[neighbor_index]))

#=============
# OUTPUT INFO

# print graph info
print('The network contains:',G.number_of_nodes(),'nodes and ',G.number_of_edges(),' edges')

# plot the graph
# pos = nx.spring_layout(G)
# nx.draw(G, pos)
# nx.draw_networkx_edge_labels(G, pos)
#plt.show()
