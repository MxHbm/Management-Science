#### Load necessary packages 

#### Import python scrips
from data_generation import *  #Werte für Parameter
import globals #Globale variablen

def main():

    # Erzeuge Sets für das Gurobi Modell
    T = [i for i in range(globals.T_end)]
    F = [i for i in range(globals.F_end)]
    S = [i for i in range(globals.S_end)]
    FT = globals.FT_values
    MP = [i for i in range(globals.MP_end)]
    CT = globals.CT_values
    L = [i for i in range(globals.L_end)]

    ### Get the needed parameters

    data = Parameters_FirstStage(T,F,S,FT,MP,CT,L)

    print(data.cmin)

main()