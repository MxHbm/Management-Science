''' main.py '''

#### Load necessary packages 

#### Import python scrips
from variables import *  #Werte für Parameter
from scenario_reduction import * 
from model import *      #Gurobi Modell
from parameters import *   # All parameters
#from gurobipy import * #Gurobi
from results import *  #Ergebnisse

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


    # Model
    m = Model()
    data = Parameters("data/base_data.json")

    try:
        m, logger = m.Run_Model(data, logger)
            
        results = Results(m, data)

        results.Evaluate_results()
    except Exception as e:
        logger.exception(e)    

    

    logger.info('========================================= End logging =========================================== \n')


if __name__ == "__main__":
    main()