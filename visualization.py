# -*- coding: utf-8 -*-
"""
==============================================================================
INTERACTIVE VISUALIZATION MODULE
==============================================================================
DESCRIPTION
    This script implements tools for visualizing original data offered by 
    competition organizing committee (Jeux Mathematiques).
    
CREATED
    3/25/2018
    last modified: 4/2/2018

COLLABORATORS
    R. Borela
    S. Hanumasagar
    F. Liu
    N. Roy 
"""

# import modules
import sys, os
import numpy as np
from scipy import interpolate as intp
import matplotlib as mpl
import matplotlib.colors as colors
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

# define what product
plot_product = 'Product 1' # 'Product 1', 'Product 2','Products 1 and 2'

# set plot font properties
font = {'size'   : 20}    
mpl.rc('font', **font)

# paths
input_path = 'C:/Users/Rodrigo Borela/Documents/spring18/cse6730/proj2/viz_input'
output_path = ''

# load data
stores = np.loadtxt(os.path.join(input_path,'stores.csv'),delimiter=",")
sales_p1 = np.loadtxt(os.path.join(input_path,'sales_p1.csv'),delimiter=",")
sales_p2 = np.loadtxt(os.path.join(input_path,'sales_p2.csv'),delimiter=",")
warehouses = np.loadtxt(os.path.join(input_path,'warehouses.csv'),delimiter=",")
plants = np.loadtxt(os.path.join(input_path,'plants.csv'),delimiter=",")

# define warehouse store assignment
warehouse_assgn = [[1,3,4,6,7,8,11,12,14,17,18],
                   [2,5,9,10,13,15,16,19,20]]

# get number of days
n_days = np.shape(sales_p1)[1]

# generate grid
x = np.arange(0,13,1)
y = np.arange(0,7,1)

# generate total sales grid
total_sales = np.zeros([13, 7])
total_sales[total_sales == 0.0] = np.nan
total_sales[stores[:,0].astype(int),stores[:,1].astype(int)] = 0.0

# generate figure objects
fig, ax = plt.subplots()
div = make_axes_locatable(ax)
cax = div.append_axes('right', '3%', '3%')
        
# loop over year
for day in range(n_days):
    ax.cla()
    s_index = 0
    for s in stores:
        # update sale totals in each store
        if plot_product == 'Product 1':
            total_sales[int(s[0]),int(s[1])] += sales_p1[s_index,day]
        elif plot_product == 'Product 2':
            total_sales[int(s[0]),int(s[1])] += sales_p2[s_index,day]
        elif plot_product == 'Products 1 and 2':
            total_sales[int(s[0]),int(s[1])] += sales_p1[s_index,day] + sales_p2[s_index,day]
        # annotate stores
        bbox_props = dict(boxstyle='round', fc = 'white', ec='w',
                          alpha = .8, lw=2)
        t = ax.text(s[0],s[1], 'S'+str(s_index+1), ha="center", va="center",
            size=14,
            bbox=bbox_props)
        # update store counter
        s_index += 1
    # annotate warehouses
    bbox_props = dict(boxstyle='circle', fc = 'black', ec='k',
                          alpha = .8, lw=2, pad = 1.5)
    t = ax.text(int(warehouses[0,0]),int(warehouses[0,1]), 'W1', ha="center", va="center",
            size=14, color = 'white',
            bbox=bbox_props)
    t = ax.text(int(warehouses[1,0]),int(warehouses[1,1]), 'W2', ha="center", va="center",
            size=14, color = 'white',
            bbox=bbox_props)
    # annotate plants
    bbox_props = dict(boxstyle='roundtooth', fc = 'grey', ec='k',
                          alpha = .8, lw=2, pad = 1.5)
    t = ax.text(int(plants[0,0]),int(plants[0,1]), 'P1', ha="center", va="center",
            size=14, color = 'white',
            bbox=bbox_props)
    t = ax.text(int(plants[1,0]),int(plants[1,1]), 'P2', ha="center", va="center",
            size=14, color = 'white',
            bbox=bbox_props)
    # update graph
    ax.grid()
    im = ax.imshow(total_sales.T, origin = 'lower', interpolation = 'none', cmap='jet')
    cb = fig.colorbar(im, cax=cax)
    ax.set_title(plot_product+': Day {}'.format(day))
    ax.set_aspect('equal')
    ax.xaxis.set_ticks(x); ax.xaxis.set_label('x (km)');
    ax.yaxis.set_ticks(y); ax.yaxis.set_label('y (km)');
    plt.pause(.025)