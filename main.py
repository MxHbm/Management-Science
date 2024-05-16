''' main.py '''

#### Load necessary packages 

#### Import python scrips
from data_generation import *  #Werte für Parameter
from scenario_reduction import * 
from model import *      #Gurobi Modell
import globals      #Globale variablen
#from gurobipy import * #Gurobi


def main():

    # Erzeuge Sets für das Gurobi Modell
    T = [i for i in range(globals.T_end)]
    F = [i for i in range(globals.F_end)]
    S = [i for i in range(globals.S_end)]
    FT = globals.FT_values
    MP = [i for i in range(globals.MP_end)]
    CT = globals.CT_values
    L = [i for i in range(globals.L_end)]



    #Create the set of reduced scenarios
    Scenarios = Scenario_Analyse()

    #print(Scenarios)

    # Model
    m = Model()
    m.Run_Model(T, F, S, FT, MP, CT, L)
    

if __name__ == "__main__":
    main()