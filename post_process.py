"""
==============================================================================
POST PROCESS
==============================================================================
DESCRIPTION
    This script implements tools for post-processing simulation data.

CREATED
    4/2/2018
    last modified: 4/2/2018

COLLABORATORS
    R. Borela
    S. Hanumasagar
    F. Liu
    N. Roy 
"""

import matplotlib.pyplot as plt
import numpy as np

#============
# PLOT COSTS
        
def plot_costs(daily_loss, daily_delivery_cost):
    # daily plot
    daily_fig, daily_ax = plt.subplots()
    daily_ax.plot(range(len(daily_delivery_cost)),daily_delivery_cost, label='daily delivery cost')
    daily_ax.plot(range(len(daily_loss)),daily_loss, label='daily opportunity cost')
    daily_ax.set_xlabel('days')
    daily_ax.set_ylabel('cost ($)')
    daily_ax.legend()
    # cumulative plot
    cum_fig, cum_ax = plt.subplots()
    cum_ax.plot(range(len(daily_delivery_cost)), np.cumsum(daily_delivery_cost), label='cumulative delivery cost')
    cum_ax.plot(range(len(daily_loss)), np.cumsum(daily_loss), label='cumulative opportunity cost')
    cum_ax.set_xlabel('days')
    cum_ax.set_ylabel('cost ($)')
    cum_ax.legend()
    return daily_fig, cum_fig

#===============
# PLOT FINANCES

def plot_finances(daily_revenue, daily_delivery_cost, daily_profit):
    # daily plot
    daily_fig, daily_ax = plt.subplots()
    daily_ax.plot(range(len(daily_delivery_cost)),daily_delivery_cost, label='daily delivery cost')
    daily_ax.plot(range(len(daily_revenue)),daily_revenue, label='daily revenue')
    daily_ax.plot(range(len(daily_profit)),daily_profit, label='daily profit')
    daily_ax.set_xlabel('days')
    daily_ax.set_ylabel('dollar ($)')
    daily_ax.legend()
    # cumulative plot
    cum_fig, cum_ax = plt.subplots()
    cum_ax.plot(range(len(daily_delivery_cost)), np.cumsum(daily_delivery_cost), label='cumulative delivery cost')
    cum_ax.plot(range(len(daily_revenue)), np.cumsum(daily_revenue), label='cumulative revenue')
    cum_ax.plot(range(len(daily_profit)), np.cumsum(daily_profit), label='cumulative profit')    
    cum_ax.set_xlabel('days')
    cum_ax.set_ylabel('dollar ($)')
    cum_ax.legend()
    return daily_fig, cum_fig

#============
# PLOT SALES

def plot_sales(daily_stock, daily_demand):
    # daily plot
    daily_fig, daily_ax = plt.subplots()
    daily_ax.plot(range(len(daily_stock)),daily_stock, label='daily stock')
    daily_ax.plot(range(len(daily_demand)),daily_demand, label='daily demand')
    daily_ax.set_xlabel('days')
    daily_ax.set_ylabel('products')
    daily_ax.legend()
    # cumulative plot
    cum_fig, cum_ax = plt.subplots()
    cum_ax.plot(range(len(daily_stock)), np.cumsum(daily_stock), label='cumulative stock')
    cum_ax.plot(range(len(daily_demand)), np.cumsum(daily_demand), label='cumulative demand') 
    daily_ax.set_xlabel('days')
    daily_ax.set_ylabel('products')
    cum_ax.legend()
    return daily_fig, cum_fig

#============
# PLOT STOCK

def plot_warehouse_stock(daily_stock_W1, daily_stock_W2):
    # daily plot
    daily_fig, daily_ax = plt.subplots()
    daily_ax.plot(range(len(daily_stock_W1)),daily_stock_W1, label='W1 stock')
    daily_ax.plot(range(len(daily_stock_W2)),daily_stock_W2, label='W2 stock')
    daily_ax.set_xlabel('days')
    daily_ax.set_ylabel('products')
    daily_ax.legend()
    # cumulative plot
    cum_fig, cum_ax = plt.subplots()
    cum_ax.plot(range(len(daily_stock_W1)), np.cumsum(daily_stock_W1), label='W1 cum stock')
    cum_ax.plot(range(len(daily_stock_W2)), np.cumsum(daily_stock_W2), label='W2 cum stock') 
    daily_ax.set_xlabel('days')
    daily_ax.set_ylabel('products')
    cum_ax.legend()
    return daily_fig, cum_fig

#=================
# PLOT DELIVERIES

def plot_deliveries(daily_w_del, daily_s_del):
    # daily plot
    daily_fig, daily_ax = plt.subplots()
    daily_ax.plot(range(len(daily_w_del)),daily_w_del, label='daily warehouse deliveries')
    daily_ax.plot(range(len(daily_s_del)),daily_s_del, label='daily store deliveries')
    daily_ax.set_xlabel('days')
    daily_ax.set_ylabel('products')
    daily_ax.legend()
    # cumulative plot
    cum_fig, cum_ax = plt.subplots()
    cum_ax.plot(range(len(daily_w_del)), np.cumsum(daily_w_del), label='cumulative warehouse deliveries')
    cum_ax.plot(range(len(daily_s_del)), np.cumsum(daily_s_del), label='cumulative store deliveries') 
    daily_ax.set_xlabel('days')
    daily_ax.set_ylabel('products')
    cum_ax.legend()
    return daily_fig, cum_fig

#============
# PLOT STUDY

def plot_study_finances(tag, variable, cum_revenue, cum_del_cost, cum_opp_cost):
    # daily plot
    study_fig, study_ax = plt.subplots()
    study_ax.plot(variable, cum_revenue, label='revenue')
    study_ax.plot(variable, cum_del_cost, label='delivery cost')
    study_ax.plot(variable, cum_opp_cost, label='oppotunity cost')
    study_ax.set_xlabel(tag)
    study_ax.set_ylabel('dollar ($)')
    study_ax.legend()
    return study_fig

def plot_study_profit(tag, variable, cum_profit):
    # daily plot
    study_fig, study_ax = plt.subplots()
    study_ax.plot(variable, cum_profit, label='profit')
    study_ax.set_xlabel(tag)
    study_ax.set_ylabel('dollar ($)')
    study_ax.legend()
    return study_fig