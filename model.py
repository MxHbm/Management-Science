#### Load necessary packages 

#### Import python scrips
from data_generation import *  #Werte für Parameter
import globals #Globale variablen
from gurobipy import * #Gurobi

def Objective_Function(data, decisionVariables_FirstStage, model, T, F, S, FT, MP, CT, L):
    ''' objective function:
    TCOST ... total costs
    ENB ... expected net benefit
    '''
    print('FT:',  FT)
    print('L:',  L)
    print('data.tc:',  data.tc)

    print(decisionVariables_FirstStage)


    model.setObjective( sum(data.tc[l][i] for i in FT for l in L ), GRB.MINIMIZE)     #for t in T

    return model


def Constraints(data, decisionVariables_FirstStage, integerVariables, model, T, F, S, FT, MP, CT, L):
    ''' constraints: 
    '''

    print(decisionVariables_FirstStage)

    # Constraint 1


    # Constraint 1.12: Required Number Of Trucks
    """ The volume shipped from factory inventory to DC l needs to be loaded in trucks. The number of required trucks (TRi, l, t ) is calculated
        in the following constraints. A shipment to a distribution center may require n trucks, only one of these n trucks is allowed to have less
        than a truck load tlmax and the minimum amount of cargo it can transport is given by parameter tlmin 
    """
    model.addConstrs( decisionVariables_FirstStage.Vi_l_t[i, l, t] 
                        <= integerVariables.TRi_l_t[i, l, t] * data.tl_max for i in FT for l in L for t in T)
    
    model.addConstrs( decisionVariables_FirstStage.Vi_l_t[i, l, t] 
                        >= (integerVariables.TRi_l_t[i, l, t] - 1)  * data.tl_max + data.tl_min for i in FT for l in L for t in T)
    
    """ Every shipment from a factory warehouse to a DC must be planned to arrive within the horizon. For that, Vi, l, t must be set to zero every
        time t + τl > hl     Vi,l,t = 0, ∀i ∈ F T , l ∈ L, t ∈ (hl - τl + 1 )..hl : τl > 0 
    """
    model.addConstrs( decisionVariables_FirstStage.Vi_l_t[i, l, t] == 0 for i in FT for l in L for t in T ) #if (data.hl - data.tau[l] + 1) > data.hl[l])

    return model

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



    print('data.cmin: ', data.cmin)
    print('data: ', data)

    # Create a new model
    model = Model("FirstStage")

    # get the needed decision variables
    decisionVariables_FirstStage = DecisionVariables_FirstStage(model, T, F, S, FT, MP, CT, L)

    # get the needed integer variables
    integerVariables = IntegerVariables(model, data, T, F, S, FT, MP, CT, L)

    # Add the objective function
    model = Objective_Function(data, decisionVariables_FirstStage,  model, T, F, S, FT, MP, CT, L)

    # Add the constraints
    model = Constraints(data, decisionVariables_FirstStage, integerVariables, model, T, F, S, FT, MP, CT, L)

    # Optimize model
    model.optimize()

    # Print the results
    for v in model.getVars():
        print('%s %g' % (v.varName, v.x))

    print('Obj: %g' % model.objVal)




if __name__ == "__main__":
    main()