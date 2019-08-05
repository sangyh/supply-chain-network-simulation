Supply Chain Network Simulation by R. Borela, F. Liu, S. Hanumasagar, N. Roy (April, 2018)

Files:
application.py	        application program for executing simulation, handlers for sales and logistics
topology.py    		generates network of stores, plants, warehouses and truck delivery
post_process.py	        miscellaneous functions for plotting
visualization.py        module for interactive data visualization (not tested on DeepThought) 
store_info.cvs          contains input for topology generation

To run the program:
- place the store_info.cvs file in the same folder as the topology.py and application.py files
- load python 2.7 and external libraries (matplotlib, numpy, networkx, scipy)
- run the command to execute:
    python parameter_study.py
  this will run the application simulation with the baseline case for 90 days
- in order to identify the effect of different parameters, change the baseline case on parameter_study or execute one of the "study_xxx" functions.
- different number of days can also be executed by changing the input to the "advance_time" function to the desired number of days as an integer.
- to execute the interactive visualization module, change the input path on the file and execute:
    python visualization.py

