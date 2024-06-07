''' main.py '''

#### Import python scrips
from model import *      #Gurobi Modell
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


    # Model Class Object! 
    m = Model()
    data = Parameters("data/base_data.json")

    try:
        gp_model, logger = m.Run_Model(data, logger)

        # Run detailed model without logger so far!! 
        gp_model_detailed = m.Run_Detailed_Model(data,gp_model)
            
        #results = Results(gp_model, data)
        #results.Evaluate_results()

    except Exception as e:
        logger.exception(e)    

    

    logger.info('========================================= End logging =========================================== \n')


if __name__ == "__main__":
    main()