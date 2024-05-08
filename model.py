#### Load necessary packages 

#### Import python scrips
from data_generation import *  #Werte für Parameter
from scenario_reduction import * 
import globals #Globale variablen
#from gurobipy import * #Gurobi
import gurobipy as gp
import datetime



def Objective_Function(                  data:Parameters_FirstStage,    decisionVariables_FirstStage: DecisionVariables_FirstStage, 
                       parameters_SecondStage:Parameters_SecondStage,   decisionVariables_SecondStage: DecisionVariables_SecondStage, 
                       binaryVariables:BinaryVariables,                 integerVariables:IntegerVariables,
                       model, T, F, S, FT, MP, CT, L):

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
        gp.quicksum(integerVariables.TRi_l_t[i, l, t] * data.tc[l][i] for i in FT for l in L for t in T) +
        gp.quicksum(binaryVariables.Ym_t[m, t] * data.sco for m in MP for t in T) +
        #parameters_SecondStage.rho[s] * gp.quicksum(decisionVariables_SecondStage.RSs_t[s, t] * data.rsc + decisionVariables_SecondStage.ROs_t[s, t] * data.roc for s in S for t in T),
        gp.quicksum(parameters_SecondStage.rho[s] 
                    * (decisionVariables_SecondStage.RSs_t[s, t] * data.rsc + decisionVariables_SecondStage.ROs_t[s, t] * data.roc) for s in S for t in T),
        GRB.MINIMIZE
    )


    ''' The expected net benefit is obtained from income minus total costs. The incomes include from left to right, the export sales income, sales
        income, and overstock incomes. Overstock incomes are produced from selling at a reduced price by the quantity produced in overstock for
        each of families.'''
    
    model.setObjective((

        gp.quicksum(
            data.re[f] * data.ls_f[f] * integerVariables.Ef_t[f, t]
            for f in F for t in T
        )
        + #parameters_SecondStage.rho 
            gp.quicksum(
                parameters_SecondStage.rho[s]
                    * ( gp.quicksum(
                            data.r[f] 
                            * (parameters_SecondStage.dp[s][f][l][t] - decisionVariables_SecondStage.SO_sflt[s, f, l, t])
                            for l in L for f in F for t in T
                        )
                        + gp.quicksum(

                            decisionVariables_SecondStage.OSs_f_l_t[s, f, l, t] * data.rr[f]
                            for l in L for f in F for t in T
                        )
                    )
                for s in S )
        ) - model.getObjective().getValue(),
        GRB.MAXIMIZE) 

    return model


def Constraints(data:Parameters_FirstStage, decisionVariables_FirstStage: DecisionVariables_FirstStage,
                parameters_SecondStage:Parameters_SecondStage, decisionVariables_SecondStage: DecisionVariables_SecondStage,
                integerVariables:IntegerVariables, model, T, F, S, FT, MP, CT, L):
    ''' constraints: 
    '''

    # Constraint 1

    # Constraint 1.7: Campaign Setups
    """In order to model these features, the binary variable Ym, t is introduced. This variable takes value 1 when a new production campaign
    starts at t, if and only if R2m, t > 0 and Zm,t−1 = 0, which is ensured by constraints (34) - (35) – (36). We emphasize the redundancy of
    constraint (36) which was included to improve the computational performance of the family aggregated model.
    If at any period t, a production campaign for a manufacturing plant start (Ym,t = 1), then on periods t− t1 : t1 ∈ 0..(αm− 1) setup
    tasks may be required and therefore production is not allowed in these periods . In this way if Ym,t = 1 keeps Zm,t−t1 = 0 (there is no
    production) until finish the setup task (constraint (37)). Now for the special case that at the beginning of the horizon there is a setup task
    in progress, this is reflected in the parameter ostm > 0, constraint (38) keeping campaign indicator variable to 0 until the task is finished.
    """
    model.addConstrs(integerVariables.Zm_t[m, t-1] <= data.zmax[m] * (1 - integerVariables.Zm_t[m, t-1]) for m in MP for t in T if t > 0)
    model.addConstrs(integerVariables.R2m_t[m,t] >= integerVariables.Ym_t[m,t] for m in MP for t in T)
    model.addConstrs(integerVariables.R2m_t[m,t] - integerVariables.Zm_t[m, t-1] <= integerVariables.Ym_t[m,t] for m in MP for t in T if t > 0)
    model.addConstrs(integerVariables.Zm_t[m, t - t1] <= data.zmax[m] * (1 - integerVariables.Ym_t[m,t]) for m in MP for t in T for t1 in range(data.alpha[m]) if (data.alpha[m] > 0)  and (t - t1 >= 0))
    model.addConstrs(integerVariables.Zm_t[m,t] <= 0 for m in MP for t in T if t < data.ost[m])

    #5.1.8. Factory inventory balances
    """ The following constraints model the filling of factory inventory with finished products and the shipments and exports that deplete this
    inventory."""

    model.addConstrs(decisionVariables_FirstStage.IFf_t[f,t] 
                     <= gp.quicksum(decisionVariables_FirstStage.DVf_l_t[f,l,t1] for t1 in range(t+1, t+data.omega_fw[f] + 1) for l in L)
                    for f in F for t in T 
                    if (data.fty[f] == 1) and (t + data.omega_fw[f] <= data.hl))

    model.addConstrs(decisionVariables_FirstStage.IFf_t[f,t] <= gp.quicksum((decisionVariables_FirstStage.DVf_l_t[f,l,t1]/data.omega_fw[f])*(t+data.omega_fw[f]-data.hl) for t1 in range(t - data.omega_fw[f]+1,t+1) for l in L) + 
                     gp.quicksum(decisionVariables_FirstStage.DVf_l_t[f,l,t2] for t2 in range(t+1,t+data.omega_fw[f] + 1) for l in L if t2 <= data.hl) for f in F for t in T if data.fty[f] == 1 and (t + data.omega_fw[f] > data.hl))
    
    model.addConstrs(decisionVariables_SecondStage.IDs_f_l_t[s,f,l,t] <= gp.quicksum(parameters_SecondStage.dp[s][f][l][t1] for t1 in range(t+1,t+data.omega_dc[f] + 1)) for l in L for f in F for t in T for s in S if data.fty[f]== 1 and (t + data.omega_dc[f] <= data.hl))

    model.addConstrs(decisionVariables_SecondStage.IDs_f_l_t[s,f,l,t] <= gp.quicksum((parameters_SecondStage.dp[s][f][l][t1]/data.omega_dc[f])*(t+data.omega_dc[f]-data.hl) for t1 in range(t - data.omega_dc[f]+1,t+1)) +
                        gp.quicksum(parameters_SecondStage.dp[s][f][l][t2] for t2 in range(t+1,t+data.omega_dc[f] + 1) if t2 <= data.hl) for l in L for f in F for t in T for s in S if data.fty[f] == 1 and (t + data.omega_dc[f] > data.hl))

    # Constraint 1.11: Shipments consolidation
    """ Shipments (Vi, l, t ) from the factory inventory to DCs l are consolidated into fresh and dry shipments with variables DVf, l, t according to
    their refrigerated transportation requirements.
    """

    model.addConstrs(decisionVariables_FirstStage.Vi_l_t[i,l,t] == gp.quicksum(decisionVariables_FirstStage.DVf_l_t[f,l,t] for f in F if data.fty[f] == i) for i in FT for l in L for t in T)

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
    model.addConstrs( decisionVariables_FirstStage.Vi_l_t[i, l, t] == 0 for i in FT for l in L for t in T 
                     if (t in (range(data.hl - data.tau[l] + 1), data.hl)) and data.tau[l] > 0)

    # Constraint 1.13: Exports lots
    """ Bounds for the number of lots to be exported for each family f on the horizon
    """

    model.addConstrs( data.el_min[f] <= gp.quicksum(integerVariables.Ef_t[f, t] for t in T) for f in F)
    model.addConstrs( gp.quicksum(integerVariables.Ef_t[f, t] for t in T) <= data.el_max[f] for f in F)

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
    parameters_SecondStage = Parameters_SecondStage(T, F, S, FT, MP, CT, L)

    # get the needed decision variables for the second stage
    decisionVariables_SecondStage = DecisionVariables_SecondStage(model, T, F, S, FT, MP, CT, L)

    # Add the objective function

    model = Objective_Function(data, decisionVariables_FirstStage, parameters_SecondStage, decisionVariables_SecondStage, binaryVariables, integerVariables, model, T, F, S, FT, MP, CT, L)

    # Add the constraints
    model = Constraints(data, decisionVariables_FirstStage, parameters_SecondStage, decisionVariables_SecondStage, integerVariables, model, T, F, S, FT, MP, CT, L)

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