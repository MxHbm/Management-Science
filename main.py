''' main.py '''

#### Load necessary packages 

#### Import python scrips
from data_generation import *  #Werte für Parameter
from scenario_reduction import * 
from model import *      #Gurobi Modell
import globals      #Globale variablen
#from gurobipy import * #Gurobi

import logging

def main():
    #initialize logging
    logger = logging.getLogger('Model_Log')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('results/logging.log')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info('========================================= Start logging ========================================= ')



    #Create the set of reduced scenarios
    scenarios = Scenario_Analyse()

    # Erzeuge Sets für das Gurobi Modell
    T = [i for i in range(globals.T_end)]
    F = [i for i in range(globals.F_end)]
    S = [i for i in range(scenarios.get_len_reduced_scenarios())]
    FT = globals.FT_values
    MP = [i for i in range(globals.MP_end)]
    CT = globals.CT_values
    L = [i for i in range(globals.L_end)]

    #print(scenarios)

    # Model
    m = Model()

    try:
        m.Run_Model(T, F, S, FT, MP, CT, L, scenarios, logger)
    except Exception as e:
        logger.exception(e)    

    logger.info('========================================= End logging =========================================== \n')


if __name__ == "__main__":
    main()