# -*- coding: utf-8 -*-
"""
==============================================================================
APPLICATION
==============================================================================
DESCRIPTION
    This script defines the simulation execution pipeline and handlers for
    sales and logistics operations.

CREATED
    3/25/2018
    last modified: 4/24/2018

COLLABORATORS
    R. Borela
    S. Hanumasagar
    F. Liu
    N. Roy
"""

# python libraries
import numpy as np
import time, os, sys
from itertools import permutations, combinations

# auxiliary modules
from topology import *
from post_process import *

# deactivate interactive mode
plt.ioff()

#============
# DATA MODEL

# generate demand drawn from modelled exponential probability distribution for each store
def generate_demand(store):
    np.random.seed(0)
    demand = .5*np.ceil(np.random.exponential(1./(store.exp_sale), None))
    return(demand)


#==============
# MAIN PROGRAM

class simulation:
    # topology variables
    global P, W, S, G
    def __init__(self,case):
        #=== TAG
        self.tag = case.tag
        if case.tag == 'n_trucks':
            self.var = str(case.n_trucks)
        elif case.tag == 'interval':
            self.var = str(case.interval)
        elif case.tag == 'max_stores':
            self.var = str(case.max_stores)
        elif case.tag == 'min_percent':
            self.var = str(case.min_percent)
        else:
            self.var = ''
        #=== UPDATE MIN STOCK
        for entity in S+W:
            entity.min_stock = int(case.min_percent * entity.capacity)
        #=== TRUCK DELIVERY SYSTEM
        self.max_stores = case.max_stores
        self.T = []
        for t in range(case.n_trucks):
            self.T.append(truck('T'+str(t+1),50, 0, (), 1, case.base_cost, case.cost_per_mile, case.max_stores))
        # === FINANCES
        # daily
        self.price_per_unit = 100
        self.daily_demand=[]  	    # daily demand over 20 stores
        self.daily_sales=[]  	        # daily demand over 20 stores
        self.daily_revenue=[]		    # revenue from sales made over all stores
        self.daily_opp_cost=[]		 # opportunity loss arising from low stock
        self.daily_delivery_cost=[]	 # total delivery costs to stores and WHs
        self.daily_profit=[]         # daily profile calc as revenue - delivery cost
        # cumulative
        self.cum_demand=0
        self.cum_sales=0
        self.cum_revenue = 0
        self.cum_opp_cost = 0
        self.cum_profit=0
        self.cum_delivery_cost=0
        # stats
        self.delivery_cost_per_prod = 0 # update
        # === LOGISTICS
        self.opt_routes = self.optimal_routes()
        self.interval= case.interval				# interval between deliveries
        self.daily_stock_W1 = []
        self.daily_stock_W2 = []
        self.low_stock_warning = []
        self.zero_stock_warning = []
        self.daily_deliveries = []
        self.daily_warehouse_deliveries = []
        self.daily_store_deliveries = []
        self.daily_mileage = []

    # run simulation for 1 year, 6 days a week
    def advance_time(self, n_days):
        for day in range(n_days): # all days in a year except sundays
        #=== SUPPLY CHAIN
            # run logistics, restocking and delivery
            daily_logistics = self.supply_chain()
            # update global history
            self.daily_deliveries.append(daily_logistics[0])
            self.daily_warehouse_deliveries.append(daily_logistics[1])
            self.daily_store_deliveries.append(daily_logistics[2])
            self.daily_mileage.append(daily_logistics[3])
            self.daily_delivery_cost.append(daily_logistics[4])
            self.daily_stock_W1.append(W[0].curr_stock)
            self.daily_stock_W2.append(W[1].curr_stock)    
        
        #=== STORES
            # run store sales and collect data
            daily_balance=self.store_iterator()
            # update global history
            self.daily_demand.append(daily_balance[0])
            self.daily_sales.append(daily_balance[1])
            self.daily_revenue.append(daily_balance[2])
            self.daily_opp_cost.append(daily_balance[3])


        #==========================================
        # SUMMARY OF FINANCES
        self.cum_demand = np.sum(self.daily_demand)
        self.cum_sales = np.sum(self.daily_sales)
        self.cum_revenue = np.sum(self.daily_revenue)
        self.cum_opp_cost = np.sum(self.daily_opp_cost)
        self.daily_profit = np.subtract(self.daily_revenue, self.daily_delivery_cost)
        self.cum_profit= np.sum(self.daily_profit)
        self.cum_delivery_cost = np.sum(self.daily_delivery_cost)


        # plot costs and save output
        daily_fig, cum_fig = plot_costs(self.daily_opp_cost, self.daily_delivery_cost)
        daily_fig.savefig(self.tag +'_'+  self.var +'_daily_costs.png')
        cum_fig.savefig(self.tag +'_'+  self.var +'_cum_costs.png')

        # plot revenue, total cost and profit
        daily_fig, cum_fig = plot_finances(self.daily_revenue, self.daily_delivery_cost, self.daily_profit)
        daily_fig.savefig(self.tag +'_'+  self.var +'_daily_finances.png')
        cum_fig.savefig(self.tag +'_'+  self.var +'_cum_finances.png')

        # plot warehouse stock
        daily_fig, cum_fig = plot_warehouse_stock(self.daily_stock_W1, self.daily_stock_W2)
        daily_fig.savefig(self.tag +'_'+  self.var +'_daily_warehouse_stock.png')
        cum_fig.savefig(self.tag +'_'+  self.var +'_cum_warehouse_stock.png')

        # plot deliveries
        daily_fig, cum_fig = plot_deliveries(self.daily_warehouse_deliveries,
                                             self.daily_store_deliveries)
        daily_fig.savefig(self.tag +'_'+  self.var +'_daily_deliveries.png')
        cum_fig.savefig(self.tag +'_'+ self.var +'_cum_deliveries.png')

        # close all figures
        plt.close('all')

#================
# EVENT HANDLERS

    #=== SALES
    def store_iterator(self):
        day_demand, day_sales, day_revenue, day_opp_cost = 0,0,0,0
        for store in S:
            # get demand for individual store
            demand = generate_demand(store)
            # balance sales for individual store
            eff_sales, miss_sales = self.balance_sales(demand, store)
            # update store info
            store.eff_sales.append(eff_sales)
            store.miss_sales.append(miss_sales)
            # check stock and issue call for restock
            self.inventory_check(store)
            # update info of the day
            day_demand += demand
            day_sales += eff_sales
            day_revenue += eff_sales * self.price_per_unit
            day_opp_cost += miss_sales * self.price_per_unit
        return(day_demand,day_sales,day_revenue,day_opp_cost)

    #=== SUPPLY CHAIN
    def supply_chain(self):
        day_deliveries, day_warehouse_deliveries, day_store_deliveries  = 0,0,0
        day_mileage, day_delivery_cost = 0,0
        # sum base cost of truck system
        day_delivery_cost += len(self.T)*self.T[0].base_cost
        # restock warehouses if necessary
        w_del, w_miles, w_del_cost = self.restock_warehouses()
        # restock stores if necessary
        s_del, s_miles, s_del_cost = self.restock_stores()
        # clear trucks routes at the end of the day
        for truck in self.T:
            truck.route=()
        # update variables of the day
        day_warehouse_deliveries = w_del
        day_store_deliveries = s_del
        day_deliveries = w_del + s_del
        day_mileage = w_miles + s_miles
        day_delivery_cost = w_del_cost + s_del_cost
        return(day_deliveries, day_warehouse_deliveries, day_store_deliveries,
               day_mileage, day_delivery_cost)


    #============================
    # MANAGE STORES & WAREHOUSES

    # compute local effective and missed sales
    def balance_sales(self,demand, store):
        # stock meets demand
        if demand <= store.curr_stock:
            eff_sales = demand
            miss_sales = 0
            store.curr_stock -= demand
        # stock is insufficient and sales are missed
        else:
            eff_sales = store.curr_stock
            miss_sales = (demand - store.curr_stock)
            store.curr_stock = 0
        return(eff_sales,miss_sales)

    # check if stock is low and issue warning
    def inventory_check(self,store):
        if store.curr_stock <= store.min_stock:
            if not store in self.low_stock_warning and not store.curr_stock == 0:
                self.low_stock_warning.append(store)
            elif store.curr_stock == 0 and not store in self.zero_stock_warning:
                self.zero_stock_warning.append(store)
        # remove duplicates
        if store in self.low_stock_warning and store in self.zero_stock_warning:
            self.low_stock_warning.remove(store)


    #===================
    # MANAGE LOGISTICS

    # restock warehouse
    def restock_warehouses(self):
        n_trips, mileage, delivery_cost = 0, 0, 0
        # loop over trucks
        for truck in self.T:
            # check whether truck can leave according to schedule and availability
            if truck.on_hold >= self.interval and not truck.route:
                # loop over warehouses
                for warehouse in W:
                    # check if current stock is smaller than minimum
                    if warehouse.curr_stock <= warehouse.min_stock:
                        # reset on hold counter
                        truck.on_hold = 1
                        # get parent production plant
                        parent_plant = warehouse.parent
                        # assign truck route
                        truck.route = (warehouse,parent_plant,warehouse)
                        # calculate distance warehouse/parent plant/warehouse
                        path_dist = 2.*G[warehouse.x,warehouse.y][parent_plant.x,parent_plant.y]['length']
                        # number of products on delivery order
                        order = (warehouse.capacity*(warehouse.refill_pc/100.0))- warehouse.curr_stock
                        if order > truck.capacity:
                            actual_load = truck.capacity
                        else:
                            actual_load = order
                        # load truck
                        truck.actual_load = actual_load
                        # mileage
                        mileage += path_dist
                        # delivery cost
                        delivery_cost += mileage * truck.cost_per_mile
                        # number of trips
                        n_trips += 1
                        # perform delivery
                        self.delivery(truck,'W_RESTOCK')
            elif not truck.route:
                # update truck on hold days
                truck.on_hold  += 1
        return(n_trips, mileage, delivery_cost)


    # restock stores
    def restock_stores(self):
        n_trips, mileage, delivery_cost = 0, 0, 0
        for truck in self.T:
            # get list of stores that need restocking
            stores_w_warning = self.low_stock_warning + self.zero_stock_warning
            if len(stores_w_warning) > 0:
                # check whether truck can leave (according to schedule and availability)
                if truck.on_hold >=self.interval and not truck.route:
                    # update on hold counter
                    truck.on_hold  = 1
                    # get route for truck
                    route_dist, truck.route = self.delivery_route(truck, stores_w_warning)
                    # compile order for stores
                    order = 0
                    for store in truck.route[1:-1]:
                        order += (store.capacity * (store.refill_pc / 100.0)) - store.curr_stock
                    if order > truck.capacity:
                        actual_load = truck.capacity
                    else:
                        actual_load = order
                    # load truck
                    truck.actual_load = actual_load
                    # mileage
                    mileage += route_dist
                    # delivery cost
                    delivery_cost += route_dist * truck.cost_per_mile
                    # number of trips
                    n_trips += 1
                    # perform delivery
                    self.delivery(truck, 'S_RESTOCK')
            elif not truck.route:
                # update truck schedule
                truck.on_hold  += 1
        return (n_trips, mileage, delivery_cost)


    # computes optimal route between for all store combinations
    def optimal_routes(self):
        # iterate over combination sizes
        opt_routes = []
        for comb_size in range(1,self.max_stores+1):
            # get all possible combinations of stores for a combination size
            all_comb = list(combinations(S, comb_size))
            # loop over all poss. combinations to get permutations
            for comb in all_comb:
                all_perm = []
                # get permutations with warehouses included
                perm = list(permutations(comb,len(comb)))
                for warehouse in W:
                    for p in perm:
                        all_perm.append((warehouse,)+p+(warehouse,))
                # path distances
                path_dist = [0]*len(all_perm)
                for index in range(len(all_perm)):
                    for p in range(len(all_perm[index])-1):
                        path_dist[index]+=G[all_perm[index][p].x, all_perm[index][p].y][all_perm[index][p+1].x, all_perm[index][p+1].y]['length']
                # get shortest route
                shortest_dist = min(path_dist)
                shortest_index = path_dist.index(shortest_dist)
                shortest_route = all_perm[shortest_index]
                # append shortest route to global optimal routes
                opt_routes.append([shortest_dist, shortest_route])
        return(opt_routes)



    # find optimal delivery route to service under-stocked stores
    def delivery_route(self,truck,list_stores):
        # max number of combinations
        if truck.max_stores >= len(list_stores):
            comb_size = len(list_stores)
        else:
            comb_size = truck.max_stores
        # get possible combinations of stores in list
        all_comb = []
        stores_comb = list(combinations(list_stores, comb_size))
        for comb in stores_comb:
            for warehouse in W:
                all_comb.append(set((warehouse,)+comb))
        # get corresponding optimal routes for each combination
        subset_opt_routes = [route for route in self.opt_routes if set(route[1]) in all_comb]
        # select shortest route in subset of optimal routes
        subset_opt_routes_dist = [route[0] for route in subset_opt_routes]
        shortest_dist = min(subset_opt_routes_dist)
        shortest_index = subset_opt_routes_dist.index(shortest_dist)
        shortest_route = subset_opt_routes[shortest_index][1]
        return(shortest_dist, shortest_route)


    # update parameters upon dispatching trucks
    def delivery(self, truck, route_type):
        # get warehouse of origin
        origin = truck.route[0]
        # delivery warehouse/plant/warehouse
        if route_type == 'W_RESTOCK':
            # receive all content
            origin.curr_stock += truck.actual_load
            # unload all content
            truck.actual_load = 0
        # delivery warehouse/[stores]/warehouse
        elif route_type == 'S_RESTOCK':
            # update stock in warehouse
            origin.curr_stock -= truck.actual_load
            # unload content along the route (first come / first serve)
            for store in truck.route[1:-1]:
                # products requested by store
                order = (store.capacity * (store.refill_pc/100.0)) - store.curr_stock
                # actual restock
                if truck.actual_load >= order:
                    actual_restock = order
                else:
                    actual_restock = truck.actual_load
                # update store stock
                store.curr_stock += actual_restock
                # update truck load
                truck.actual_load -= actual_restock
                # check new store stock and verify it can be removed from low_stock + zero_stock list
                if store.curr_stock >= store.min_stock:
                    try:
                        self.low_stock_warning.remove(store)
                    except:pass
                elif store.curr_stock > 0:
                    # add it to the list of low stock stores
                    self.low_stock_warning.append(store)
                    # remove it from the zero stock
                    try:
                        self.zero_stock_warning.remove(store)
                    except:pass