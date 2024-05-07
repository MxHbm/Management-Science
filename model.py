#### Load necessary packages 

#### Import python scrips
from data_generation import *  #Werte für Parameter
from scenario_reduction import * 
import globals #Globale variablen
#from gurobipy import * #Gurobi
import gurobipy as gp
import datetime

def Objective_Function(data, decisionVariables_FirstStage, parameters_SecondStage, decisionVariables_SecondStage, binaryVariables, integerVariables, model, T, F, S, FT, MP, CT, L):
    ''' objective function:
    TCOST ... total costs
    ENB ... expected net benefit
    '''
    # Objective function
    ''' The following variables aid the definition of the objectives for the aggregated planning stochastic model.
        Total costs are composed of the sum of transport costs, setups costs and raw milk costs per scenario multiplied by their respective
        probability. Raw milk costs per scenario are calculated for the cases of overstock and understock. In cases of understock are the costs
        obtained from buying raw milk from a third party and for the case of overstock are production costs.'''
    #model.setObjective( sum(data.tc[l][i] for i in FT for l in L ), GRB.MINIMIZE)     #for t in T

    model.setObjective(
        quicksum(integerVariables.TRi_l_t[i, l, t] * data.tc[l][i] for i in FT for l in L for t in T) 
        + quicksum(binaryVariables.Ym_t[m, t] * data.sco for m in MP for t in T) 
        + parameters_SecondStage.rho_s[0] 
            * quicksum(decisionVariables_SecondStage.RSs_t[s, t] * data.rsc 
                   + decisionVariables_SecondStage.ROs_t[s, t] * data.roc 
                   for s in S for t in T),
        GRB.MINIMIZE
    )


    ''' The expected net benefit is obtained from income minus total costs. The incomes include from left to right, the export sales income, sales
        income, and overstock incomes. Overstock incomes are produced from selling at a reduced price by the quantity produced in overstock for
        each of families.'''
    
    model.setObjective((
        quicksum(
            data.re[f] * data.ls_f[f] * integerVariables.Ef_t[f, t]
            for f in F for t in T
        )
        + parameters_SecondStage.rho_s 
            * quicksum(
                quicksum(
                    data.r[f] 
                    * (parameters_SecondStage.dps_f_l_t[s][f][l][t] 
                       - decisionVariables_SecondStage.SO_sflt[s, f, l, t])
                    for l in L for f in F for t in T
                )
                + quicksum(
                    decisionVariables_SecondStage.OSs_f_l_t[s, f, l, t] * data.rr[f]
                    for l in L for f in F for t in T
                )
                for s in S )
        ) - model.getObjective().getValue(),
        GRB.MAXIMIZE) 
    

    return model


def Constraints(data, decisionVariables_FirstStage, integerVariables, model, T, F, S, FT, MP, CT, L):
    ''' constraints: 
    '''

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

    #Constraint 4

    model.addConstrs(IntegerVariables.Zm_t[MP, T]
                     == decisionVariables_FirstStage.Z1m_t[MP, T] + decisionVariables_FirstStage.Z2m_t[MP, T])
    
    model.addConstrs(decisionVariables_FirstStage.Z1m_t[MP, T]
                     <= Parameters_FirstStage.zmax[MP] * BinaryVariables.R1m_t[MP, T])
    
    model.addConstrs(decisionVariables_FirstStage.Z2m_t[MP, T]
                     <= Parameters_FirstStage.zmax[MP] * BinaryVariables.R2m_t[MP, T])
    
    model.addConstrs(BinaryVariables.R1m_t[MP, T]
                     + BinaryVariables.R2m_t[MP, T] == 1)
    
    model.addConstrs(BinaryVariables.R1m_t[MP, T==1]  #T = 1
                     == 1)
    
    model.addConstrs(decisionVariables_FirstStage.Z1m_t[MP, T]
                     <= IntegerVariables.Zm_t[MP, T]) # t - 1
    
    model.addConstrs(decisionVariables_FirstStage.Z1m_t[MP, T]
                     >= BinaryVariables.R1m_t[MP, T] * IntegerVariables.Zm_t[MP, T-1]) # t - 1
    
    model.addConstrs(decisionVariables_FirstStage.Auxm_t[MP, T]
                     <= IntegerVariables.Zm_t[MP, T-1]) # t - 1
    
    model.addConstrs(decisionVariables_FirstStage.Auxm_t[MP, T]
                     >= IntegerVariables.Zm_t[MP, T-1] - Parameters_FirstStage.zmax[MP] * (1 - BinaryVariables.R1m_t[MP, T])) # t - 1
    
    model.addConstrs(decisionVariables_FirstStage.Auxm_t[MP, T]
                     <= IntegerVariables.Zm_t[MP, T-1]) 
    
    model.addConstrs(decisionVariables_FirstStage.Auxm_t[MP, T]
                     <= BinaryVariables.R1m_t[MP, T] * Parameters_FirstStage.zmax[MP]) 
    
    #Constraint 5

    model.addConstrs((DecisionVariables_FirstStage.Qm_t[MP, T] / Parameters_FirstStage.cmin[0]) 
                     <= IntegerVariables.Zm_t[MP, T]
                    )
    
    model.addConstrs((DecisionVariables_FirstStage.Qm_t[MP, T] / Parameters_FirstStage.cmax[MP]) 
                     >= IntegerVariables.Zm_t[MP, T]
                    )
    
    model.addConstrs(DecisionVariables_FirstStage.Am_t[MP, T]  
                     <= DecisionVariables_FirstStage.Am_t[MP, T-1] + IntegerVariables.Zm_t[MP, T]
                    ) #t>=1

    model.addConstrs(DecisionVariables_FirstStage.Am_t[MP, T]  
                     >= DecisionVariables_FirstStage.Am_t[MP, T-1] + IntegerVariables.Zm_t[MP, T] - 
                     (Parameters_FirstStage.dmax[MP]/ Parameters_FirstStage.cmin[0] * BinaryVariables.R2m_t[MP, T])
                    ) # MP für dmax und am_t: t-1 und t>=1
    
    model.addConstrs(DecisionVariables_FirstStage.Am_t[MP, T]  
                     >= IntegerVariables.Zm_t[MP, T]
                    )
    
    model.addConstrs(DecisionVariables_FirstStage.Am_t[MP, T]
                    <= (Parameters_FirstStage.dmax[MP]/ Parameters_FirstStage.cmin[0])
                    )
    
    model.addConstrs(DecisionVariables_FirstStage.Am_t[MP, T==1]  # T=1
                    <= IntegerVariables.Zm_t[MP, T==1] # T=1
                    )
    
    model.addConstrs(DecisionVariables_FirstStage.Am_t[MP, T==1]  # T=1
                    <= (Parameters_FirstStage.dmax[MP]/ Parameters_FirstStage.cmin[0])
                    ) 
    
    model.addConstrs(DecisionVariables_FirstStage.Am_t[MP, T==1]  # T=1
                    >= IntegerVariables.Zm_t[MP, T==1] - ((Parameters_FirstStage.dmax[MP]/ Parameters_FirstStage.cmin[0]) * BinaryVariables.R2m_t[MP, T==1]) # T = 1
                    ) 

#Constraint 6
    model.addConstrs((DecisionVariables_FirstStage.Qm_t[MP, T] / Parameters_FirstStage.sc [MP])
                    <= IntegerVariables.Zm_t[MP, T] 
                    ) 
    
    model.addConstrs(DecisionVariables_FirstStage.AQm_t[MP, T] / (Parameters_FirstStage.sc [MP] * (1-Parameters_FirstStage.is_[MP]))
                    >= IntegerVariables.Zm_t[MP, T] 
                    ) 
    return model

def Run_Model(data, T, F, S, FT, MP, CT, L):
    # Create a new model
    model = gp.Model("FirstStage")

    # get the needed decision variables
    decisionVariables_FirstStage = DecisionVariables_FirstStage(model, T, F, S, FT, MP, CT, L)

    # get the needed integer variables
    binaryVariables = BinaryVariables(model, T, F, S, FT, MP, CT, L)

    # get the needed integer variables
    integerVariables = IntegerVariables(model, data, T, F, S, FT, MP, CT, L)

    # get the needed second stage parameters
    parameters_SecondStage = Parameters_SecondStage(data, T, F, S, FT, MP, CT, L)

    # get the needed decision variables for the second stage
    decisionVariables_SecondStage = DecisionVariables_SecondStage(model, T, F, S, FT, MP, CT, L)

    # Add the objective function
    model = Objective_Function(data, decisionVariables_FirstStage, parameters_SecondStage, decisionVariables_SecondStage, binaryVariables, integerVariables, model, T, F, S, FT, MP, CT, L)

    # Add the constraints
    model = Constraints(data, decisionVariables_FirstStage, integerVariables, model, T, F, S, FT, MP, CT, L)

    # Optimize model
    model.optimize()

    # Print the results
    #for v in model.getVars():
    #    print('%s %g' % (v.varName, v.x))

    #print('Attr:', model.getAttr('X'))
    print('Obj: %g' % model.objVal)

    # Save the model
    # Add timestamp to file name
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"results/result_FirstStage_LP_{timestamp}.lp"
    model.write(file_name)

    file_name = f"results/result_FirstStage_MPS_{timestamp}.mps"
    model.write(file_name)

    file_name = f"results/result_FirstStage_PRM_{timestamp}.prm"
    model.write(file_name)

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

    #Create the set of reduced scenarios
    Scenarios = Scenario_Analyse()

    print(Scenarios)

    # Model
    Run_Model(data, T, F, S, FT, MP, CT, L)
    

if __name__ == "__main__":
    main()