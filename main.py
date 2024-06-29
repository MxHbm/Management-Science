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
    data = Parameters("data/case_study_data.json")
    data_s_star = S_star("data/case_study_data.json")      # data for EMVP calculation


    try:
        gp_model, logger = m.Run_Model(data, logger)
        #gp_model.printAttr('X')

        # Run detailed model without logger so far!! 
        m2 = Model()

        gp_model_detailed, logger = m2.Run_Detailed_Model(data,gp_model, logger)

        # Calculate the EMVP
        emvp_objective_value, emvp_model, mvp_model, logger = m2.Calculate_emvp(data_s_star, logger)
        logger.info(f'data.rho: {data.rho}')
        logger.info(f'data_s_star.rho: {data_s_star.rho}')

        # Create Results Object
        results = Results(gp_model, gp_model_detailed, emvp_model, mvp_model, data, data_s_star)

        # calculate stochastic solution
        ss, logger = results.Calculate_ss(data, gp_model_detailed, logger)

        # calculate the VSS
        vss, logger = results.Calculate_vss(ss, emvp_objective_value, logger)
        # Print the EMVP
        print('VSS = SS - EMVP')
        print(f"SS: {ss}")
        print(f"EMVP: {emvp_objective_value}")
        print(f"VSS: {vss}")
        print(f"SS/EMVP: {ss/emvp_objective_value}")

            
        results.Evaluate_results()
        # gp_model_detailed.printAttr('X')

    except Exception as e:
        logger.exception(e)    

    

    logger.info('========================================= End logging =========================================== \n')


if __name__ == "__main__":
    main()