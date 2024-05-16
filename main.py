''' main.py '''

#### Load necessary packages 

#### Import python scrips
from data_generation import *  #Werte für Parameter
from scenario_reduction import * 
from model import *      #Gurobi Modell
import globals      #Globale variablen
#from gurobipy import * #Gurobi


def main():

    #Create the set of reduced scenarios
    Scenarios = Scenario_Analyse()

    # Erzeuge Sets für das Gurobi Modell
    T = [i for i in range(globals.T_end)]
    F = [i for i in range(globals.F_end)]
    S = [i for i in range(Scenarios.get_len_reduced_scenarios())]
    FT = globals.FT_values
    MP = [i for i in range(globals.MP_end)]
    CT = globals.CT_values
    L = [i for i in range(globals.L_end)]

    #print(Scenarios)

    # Model
    m = Model()
    m.Run_Model(T, F, S, FT, MP, CT, L, Scenarios)
    

if __name__ == "__main__":
    main()