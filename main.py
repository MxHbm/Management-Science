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
    #data = Parameters("data/base_data.json")
    #data_s_star = S_star("data/base_data_new.json")      # data for EMVP calculation

    if data.use_SRA: 
        #print(data.SRA.reduced_scenarios)
        #print(data.SRA.reduced_scenarios_probabilities)
        print(data.dp)
        print(data.rho)
    else: 
        print(data.dp)
        print(data.rho)

    # if you want to use only the expected values, set the following parameter to True in case_study_data.json use_sra = true / false


    try:
        gp_model, logger = m.Run_Model(data, logger)
        #gp_model.printAttr('X')

        # Run detailed model without logger so far!! 
        #m = Model()

        #gp_model_detailed, logger = m.Run_Detailed_Model(data,gp_model, logger)

        #results = Results(gp_model, gp_model_detailed, data)


        # Calculate the EMVP
        #emvp, logger = m.Calculate_emvp(data_s_star, logger)
        #logger.info(f'data.rho: {data.rho}')
        #logger.info(f'data_s_star.rho: {data_s_star.rho}')

        # calculate stochastic solution
        #ss, logger = results.Calculate_ss(data, gp_model_detailed, logger)

        # calculate the VSS
        #vss, logger = results.Calculate_vss(ss, emvp, logger)
        # Print the EMVP
        #print('VSS = SS - EMVP')
        #print(f"SS: {ss}")
        #print(f"EMVP: {emvp}")
        #print(f"VSS: {vss}")
            
        # results.Evaluate_results()
        #gp_model_detailed.printAttr('X')

    except Exception as e:
        logger.exception(e)    

    

    logger.info('========================================= End logging =========================================== \n')


if __name__ == "__main__":
    main()