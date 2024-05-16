#### Load necessary packages 

#### Import python scrips
from data_generation import *  #Werte für Parameter
#from gurobipy import * #Gurobi
import gurobipy as gp
import datetime as dt


class Model:
    def __init__(self):
        pass

    def Objective_Function(self, parameters_FirstStage:Parameters_FirstStage,    decisionVariables_FirstStage: DecisionVariables_FirstStage, 
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

        # TCOST
        TCOST = (gp.quicksum(integerVariables.TRi_l_t[i, l, t] 
                            * parameters_FirstStage.tc[l][i] for i in FT for l in L for t in T) 
                + gp.quicksum(binaryVariables.Ym_t[m, t] 
                            * parameters_FirstStage.sco for m in MP for t in T) 
                + gp.quicksum(parameters_SecondStage.rho[s] 
                            * (decisionVariables_SecondStage.RSs_t[s, t] 
                                * parameters_FirstStage.rsc 
                                + decisionVariables_SecondStage.ROs_t[s, t] 
                                * parameters_FirstStage.roc) 
                            for s in S for t in T))


        ''' The expected net benefit is obtained from income minus total costs. The incomes include from left to right, the export sales income, sales
            income, and overstock incomes. Overstock incomes are produced from selling at a reduced price by the quantity produced in overstock for
            each of families.'''
        
        # BENEFIT
        BENEFIT = ( gp.quicksum( parameters_FirstStage.re[f] 
                                * parameters_FirstStage.ls_f[f] 
                                * integerVariables.Ef_t[f, t]
                                for f in F for t in T)
                    + gp.quicksum(  parameters_SecondStage.rho[s]
                                    * ( gp.quicksum(parameters_FirstStage.r[f] 
                                        * (parameters_SecondStage.dp[s][f][l][t] 
                                            - decisionVariables_SecondStage.SO_sflt[s, f, l, t])
                                        for l in L for f in F for t in T)
                                        + gp.quicksum(decisionVariables_SecondStage.OSs_f_l_t[s, f, l, t] 
                                                        * parameters_FirstStage.rr[f]
                                        for l in L for f in F for t in T)
                                        )
                                    for s in S )
                    ) 
        
        # EXPECTED NET BENEFIT
        model.setObjective(BENEFIT - TCOST, GRB.MAXIMIZE)

        return model


    def Constraints(self, parameters_FirstStage:Parameters_FirstStage, decisionVariables_FirstStage: DecisionVariables_FirstStage,
                    parameters_SecondStage:Parameters_SecondStage, decisionVariables_SecondStage: DecisionVariables_SecondStage,
                    binaryVariables:BinaryVariables, integerVariables:IntegerVariables, model, T, F, S, FT, MP, CT, L):
        ''' constraints: 
        '''
        
        # Constraint 1: Raw milk supply consumption
        """ The following constraints model raw milk inventory flow within the industrial complex. In some scenarios the purchase of raw milk to
            a third-party supplier (RSs, t) or its disposal (ROs, t) due to overstock may arise. For every scenario, dris, t is raw milk daily input (parameter)
            and RMt (independent of scenarios) is the variable modeling the raw milk consumption of all plants in the complex. """
        model.addConstrs((decisionVariables_SecondStage.RIs_t[s, t]
                        == parameters_FirstStage.r0
                        + gp.quicksum(parameters_SecondStage.dri[s][t1] for t1 in T if t1 <= t) 
                        - gp.quicksum(decisionVariables_FirstStage.RMt[t1] for t1 in T if t1 <= t) 
                        + gp.quicksum(decisionVariables_SecondStage.RSs_t[s,t1] for t1 in T if t1 <= t)
                        - gp.quicksum(decisionVariables_SecondStage.ROs_t[s,t1] for t1 in T if t1<= t)
                        for s in S for t in T),
                        'Constraint_1.1a')

        model.addConstrs((decisionVariables_SecondStage.RIs_t[s,t] 
                        <= parameters_FirstStage.r_max 
                        for s in S for t in T),
                        'Constraint_1.1b')

        model.addConstrs((decisionVariables_FirstStage.RMt[t] 
                        #== gp.quicksum(decisionVariables_FirstStage.Qm_t[m,t]/parameters_FirstStage.fy(parameters_FirstStage.fpr[m]) for m in MP)
                        == gp.quicksum(decisionVariables_FirstStage.Qm_t[m,t]/parameters_FirstStage.fy[m] for m in MP)         # just for debugging
                        for t in T),
                        'Constraint_1.1c')
        
        # Constraint 2: General production constraints
        """ Family f production of all plants in the complex is equal to the manufacturing output of plants producing f. """
        model.addConstrs((decisionVariables_FirstStage.FPf_t[f,t] 
                        #== gp.quicksum(decisionVariables_FirstStage.MOm_t[m,t] for m in MP if parameters_FirstStage.fpr[m] == f)
                        == gp.quicksum(decisionVariables_FirstStage.MOm_t[m,t] for m in MP)    # just for debugging, see Issue #41
                        for f in F for t in T),
                        'Constraint_1.2a')

        model.addConstrs((decisionVariables_FirstStage.MOm_t[m,t] 
                        == (1 - parameters_FirstStage.beta[m]) 
                        * decisionVariables_FirstStage.Qm_t[m,t-parameters_FirstStage.sigma[m]] 
                        for m in MP for t in T if t > parameters_FirstStage.sigma[m]),
                        'Constraint_1.2b')
        
        model.addConstrs((decisionVariables_FirstStage.MOm_t[m,t] 
                        == (1 - parameters_FirstStage.beta[m]) 
                        * parameters_FirstStage.wp[m][t] 
                        for m in MP for t in T if t <= parameters_FirstStage.sigma[m]),
                        'Constraint_1.2c')

        # Constraint 3: Work-in-progress (WIP) inventory constraints
        """ Manufacturing products with σ m > 0 generate WIP inventory which is depleted by the volume of finished products in period t represented by the variable MOm, t. Parameter iwip0
            m represents inventory from the previous planning horizon at manufacturing plant m. """
        model.addConstrs((decisionVariables_FirstStage.IWIPm_t[m,t] 
                        == parameters_FirstStage.iwip0[m]
                        + gp.quicksum(decisionVariables_FirstStage.Qm_t[m,t1] for t1 in T if t1 <= t)
                        - gp.quicksum(decisionVariables_FirstStage.MOm_t[m,t1] for t1 in T if t1 <= t)
                        for m in MP for t in T 
                        if parameters_FirstStage.sigma[m] > 0),
                        'Constraint_1.3a')
        
        # Constraint 4
        model.addConstrs((integerVariables.Zm_t[m, t]
                        == decisionVariables_FirstStage.Z1m_t[m, t] 
                        + decisionVariables_FirstStage.Z2m_t[m, t] 
                        for m in MP for t in T),
                        'Constraint_1.4a')
        
        model.addConstrs((decisionVariables_FirstStage.Z1m_t[m, t]
                        <= parameters_FirstStage.zmax[m] * binaryVariables.R1m_t[m, t] 
                        for m in MP for t in T),
                        'Constraint_1.4b')
        
        model.addConstrs((decisionVariables_FirstStage.Z2m_t[m, t]
                        <= parameters_FirstStage.zmax[m] 
                        * binaryVariables.R2m_t[m, t] 
                        for m in MP for t in T),
                        'Constraint_1.4c')
        
        model.addConstrs((binaryVariables.R1m_t[m, t]
                        + binaryVariables.R2m_t[m, t] 
                        == 1 
                        for m in MP for t in T),
                        'Constraint_1.4d')
        
        model.addConstrs((binaryVariables.R1m_t[m, 1]  #T = 1
                        == 1 
                        for m in MP for t in T),
                        'Constraint_1.4e')
        
        model.addConstrs((decisionVariables_FirstStage.Z1m_t[m, t]
                        <= integerVariables.Zm_t[m, t-1] 
                        for m in MP for t in T 
                        if t > 1 ),
                        'Constraint_1.4f') # t - 1
        
        model.addConstrs((decisionVariables_FirstStage.Z1m_t[m, t]
                        >= binaryVariables.R1m_t[m, t] 
                        * integerVariables.Zm_t[m, t-1] 
                        for m in MP for t in T 
                        if t > 1),
                        'Constraint_1.4g') 
        
        model.addConstrs((decisionVariables_FirstStage.Auxm_t[m, t]
                        <= integerVariables.Zm_t[m, t-1] 
                        for m in MP for t in T 
                        if t > 1),
                        'Constraint_1.4h') 
        
        model.addConstrs((decisionVariables_FirstStage.Auxm_t[m, t]
                        >= integerVariables.Zm_t[m, t-1] 
                        - parameters_FirstStage.zmax[m] 
                            * (1 - binaryVariables.R1m_t[m, t]) 
                        for m in MP for t in T 
                        if t > 1),
                        'Constraint_1.4i')
        
        model.addConstrs((decisionVariables_FirstStage.Auxm_t[m, t]
                        <= integerVariables.Zm_t[m, t] 
                        for m in MP for t in T),
                        'Constraint_1.4j' )
        
        model.addConstrs((decisionVariables_FirstStage.Auxm_t[m, t]
                        <= binaryVariables.R1m_t[m, t] 
                        * parameters_FirstStage.zmax[m] 
                        for m in MP for t in T),
                        'Constraint_1.4k') 
        
        #Constraint 5: Length-based campaign
        """ The level of production capacity during a production campaign of a length-based plant is set """
        model.addConstrs(((decisionVariables_FirstStage.Qm_t[m, t] 
                        / parameters_FirstStage.cmin[m]) 
                        <= integerVariables.Zm_t[m, t] 
                        for m in MP for t in T 
                        if parameters_FirstStage.cty[m] == 0),
                        'Constraint_1.5a')
        
        model.addConstrs(((decisionVariables_FirstStage.Qm_t[m, t] 
                        / parameters_FirstStage.cmax[m]) 
                        >= integerVariables.Zm_t[m, t] 
                        for m in MP for t in T 
                        if parameters_FirstStage.cty[m] == 0),
                        'Constraint_1.5b')
        
        """ In this type of campaigns, a variable Am, t accounts for accumulated production days at manufacturing plant m on day t. This accumula-
            tion (constraints (25) and (26)) continues until the current campaign ends. Parameter dmax
            m represents maximal value of Am, t . If a campaign        ends on day t, then the mandatory accumulation of production on day t + 1 (i.e. Am,t+1 ) is relaxed (constraint (26)). This allows to set the
            accumulator variable in a new campaign to zero in a posterior campaign. In these equations the Boolean variable R2m, t (previously de-
            fined), is used to model the start or end of a length-based campaign. Constraints (27) and (28) define upper and lower bounds for Am, t .
            The quotient dmax_m / cmin_m, represents the maximum number of campaigns that might take place for manufacturing plant m within the current
            planning horizon"
        """
        model.addConstrs((decisionVariables_FirstStage.Am_t[m, t]  
                        <= decisionVariables_FirstStage.Am_t[m, t-1] 
                        + integerVariables.Zm_t[m, t] 
                        for m in MP for t in T 
                        if (t > 1) and (parameters_FirstStage.cty[m] == 0)),
                        'Constraint_1.5c')

        model.addConstrs((decisionVariables_FirstStage.Am_t[m, t]  
                        >= decisionVariables_FirstStage.Am_t[m, t-1]
                        + integerVariables.Zm_t[m, t] 
                        - ((parameters_FirstStage.dmax[m]
                            / parameters_FirstStage.cmin[m] )
                            * binaryVariables.R2m_t[m, t]) 
                        for m in MP for t in T 
                        if (t > 1) and (parameters_FirstStage.cty[m] == 0)),
                        'Constraint_1.5d')
        
        model.addConstrs((decisionVariables_FirstStage.Am_t[m, t]  
                        >= integerVariables.Zm_t[m, t] 
                        for m in MP for t in T 
                        if parameters_FirstStage.cty[m] == 0),
                        'Constraint_1.5e')
        
        model.addConstrs((decisionVariables_FirstStage.Am_t[m, t]
                        <= (parameters_FirstStage.dmax[m]
                            / parameters_FirstStage.cmin[m]) 
                        for m in MP for t in T 
                        if (t > 1) and (parameters_FirstStage.cty[m] == 0)),
                        'Constraint_1.5f')
        
        """ Accumulated production at the beginning of the horizon. The following equations (constraints (29) and (30)) model the remaining quantity
        production for the special case of t = 1."""
        model.addConstrs((decisionVariables_FirstStage.Am_t[m, 1]  # T=1
                        <= integerVariables.Zm_t[m, 1] 
                        for m in MP
                        if parameters_FirstStage.cty[m] == 0),
                        'Constraint_1.5g')
        
        model.addConstrs((decisionVariables_FirstStage.Am_t[m, 1]  # T=1
                        <= (parameters_FirstStage.dmax[m]
                            / parameters_FirstStage.cmin[m]) 
                        for m in MP
                        if parameters_FirstStage.cty[m] == 0),
                        'Constraint_1.5h') 
        
        model.addConstrs((decisionVariables_FirstStage.Am_t[m, 1]  # T=1
                        >= integerVariables.Zm_t[m, 1] 
                        - ((parameters_FirstStage.dmax[m]
                            / parameters_FirstStage.cmin[m]) 
                            * binaryVariables.R2m_t[m, 1]) 
                        for m in MP 
                        if parameters_FirstStage.cty[m] == 0),
                        'Constraint_1.5i') 

        #Constraint 6
        """ The level of production capacity during a production campaign for a shift scheduled plant is set in constraints (32) and (33). It is set
        according to the number of shifts defined by the production campaign indicator (Zm, t ). In these equations scm represents the production
        capacity of manufacturing plant m on one work shift. The parameter ism in (0,1] is the maximum portion of the capacity of a shift which
        can be idle.
        """
        model.addConstrs(((decisionVariables_FirstStage.Qm_t[m, t] 
                        / parameters_FirstStage.sc[m])
                        <= integerVariables.Zm_t[m, t] 
                        for m in MP for t in T 
                        if parameters_FirstStage.cty == 1),
                        'Constraint_1.6a')
        
        model.addConstrs((decisionVariables_FirstStage.Qm_t[m, t] 
                        / (parameters_FirstStage.sc[m] 
                            * (1 - parameters_FirstStage.is_[m]))
                        >= integerVariables.Zm_t[m, t] 
                        for m in MP for t in T 
                        if parameters_FirstStage.cty == 1),
                        'Constraint_1.6b')
        
        # Constraint 1.7: Campaign Setups
        """In order to model these features, the binary variable Ym, t is introduced. This variable takes value 1 when a new production campaign
        starts at t, if and only if R2m, t > 0 and Zm,t−1 = 0, which is ensured by constraints (34) - (35) – (36). We emphasize the redundancy of
        constraint (36) which was included to improve the computational performance of the family aggregated model.
        If at any period t, a production campaign for a manufacturing plant start (Ym,t = 1), then on periods t− t1 : t1 ∈ 0..(αm− 1) setup
        tasks may be required and therefore production is not allowed in these periods . In this way if Ym,t = 1 keeps Zm,t−t1 = 0 (there is no
        production) until finish the setup task (constraint (37)). Now for the special case that at the beginning of the horizon there is a setup task
        in progress, this is reflected in the parameter ostm > 0, constraint (38) keeping campaign indicator variable to 0 until the task is finished.
        """
        model.addConstrs((integerVariables.Zm_t[m, t-1] 
                        <= parameters_FirstStage.zmax[m] 
                        * (1 - binaryVariables.Ym_t[m, t]) 
                        for m in MP for t in T 
                        if t > 0), "Constraint_1.7a")
        
        model.addConstrs((binaryVariables.R2m_t[m,t] 
                        >= binaryVariables.Ym_t[m,t] 
                        for m in MP for t in T), "Constraint_1.7b")
        
        model.addConstrs((binaryVariables.R2m_t[m,t] 
                        - integerVariables.Zm_t[m, t-1] 
                        <= binaryVariables.Ym_t[m,t] 
                        for m in MP for t in T 
                        if t > 0), "Constraint_1.7c")
        
        model.addConstrs((integerVariables.Zm_t[m, t - t1] 
                        <= parameters_FirstStage.zmax[m] 
                        * (1 - binaryVariables.Ym_t[m,t]) 
                        for m in MP for t in T for t1 in range(parameters_FirstStage.alpha[m] - 1) 
                        if (parameters_FirstStage.alpha[m] > 0)  and (t - t1 >= 0)), "Constraint_1.7d")
        
        model.addConstrs((integerVariables.Zm_t[m,t] 
                        <= 0 
                        for m in MP for t in T 
                        if t <= parameters_FirstStage.ost[m]), "Constraint_1.7e")

        #5.1.8. Factory inventory balances
        """ The following constraints model the filling of factory inventory with finished products and the shipments and exports that deplete this
        inventory."""

        model.addConstrs((decisionVariables_FirstStage.IFf_t[f,t] 
                        == parameters_FirstStage.i0_ft[f][t] 
                        + gp.quicksum(decisionVariables_FirstStage.FPf_t[f,t1] for t1 in T if t1 <= t) 
                        - gp.quicksum(decisionVariables_FirstStage.DVf_l_t[f,l,t1] for l in L for t1 in T if t1 <= t) 
                        - gp.quicksum(integerVariables.Ef_t[f,t1] * parameters_FirstStage.el[f] for t1 in T if t1 <= t) 
                        for f in F for t in T),
                        'Constraint_1.8')

        
        # Constraint 1.9: Inventory at DCs
        """A shipment departed from factory inventory at period t, arrives to a distribution center l at period (t + τl ), where τl is the lead time for
        l. Inventory at distribution centers is scenario dependent accordingly to future demand realization (dps, f, l, t). Possible inventory fluctuation
        due to understock and overstock quantities are represented by scenario variables SOs, f, l, t,OSs, f, l, t, respectively.
        """
        model.addConstrs((decisionVariables_SecondStage.IDs_f_l_t[s,f,l,t] 
                        ==  parameters_FirstStage.i_0[f][l] 
                        + gp.quicksum(decisionVariables_FirstStage.DVf_l_t[f,l,t1] for t1 in T if (t1+parameters_FirstStage.tau[l]) <= t)
                        - gp.quicksum(parameters_SecondStage.dp[s][f][l][t1] for t1 in T if t1 <= t) 
                        + gp.quicksum(decisionVariables_SecondStage.SO_sflt[s,f,l,t1] for t1 in T if t1 <= t) 
                        - gp.quicksum(decisionVariables_SecondStage.OSs_f_l_t[s,f,l,t1] for t1 in T if t1 <= t) 
                        for s in S for f in F for l in L for t in T),
                        'Constraint_1.9a')
        

        # INDEX OF TAU WAS WRONG !! i INSTEAD OF l

        '''In any DC, fresh and dry warehouse size limitations may arise; this is modeled by constraint'''

        model.addConstrs((gp.quicksum(decisionVariables_SecondStage.IDs_f_l_t[s,f,l,t] for f in F if parameters_FirstStage.fty[f] == i) 
                        <= parameters_FirstStage.imax[i][l] 
                        for s in S for l in L for i in FT for t in T),
                        'Constraint_1.9b')
        
        # RUNNING PARAMETER FOR T IS MISSING!!! 

        # Constraint 1.10: Shelf life constraints
        """Shelf life constraints at FW. Based on the concept discussed above in subSection 4.2, the following two constraints are introduced into
        the planning model to enforce the shelf-life indirectly. This constraint ensures that a product family will be transported to the distribution
        centers before the end of its warehouse shelf-life. 
        """
        model.addConstrs((decisionVariables_FirstStage.IFf_t[f,t] 
                        <= gp.quicksum(decisionVariables_FirstStage.DVf_l_t[f,l,t1] for t1 in range(t+1,t+parameters_FirstStage.omega_fw[f]) for l in L) 
                        for f in F for t in T 
                        if (parameters_FirstStage.fty[f] == 1) and (t + parameters_FirstStage.omega_fw[f] <= parameters_FirstStage.hl)),
                        'Constraint_1.10a')


        model.addConstrs((decisionVariables_FirstStage.IFf_t[f,t] 
                        <= gp.quicksum((decisionVariables_FirstStage.DVf_l_t[f,l,t1]
                                        / parameters_FirstStage.omega_fw[f])
                                        *(t + parameters_FirstStage.omega_fw[f] - parameters_FirstStage.hl) for t1 in range(t - parameters_FirstStage.omega_fw[f] + 1, t) for l in L) 
                        +  gp.quicksum(decisionVariables_FirstStage.DVf_l_t[f,l,t2] for t2 in range(t + 1, t + parameters_FirstStage.omega_fw[f]) for l in L if t2 <= parameters_FirstStage.hl) 
                        for f in F for t in T 
                        if (parameters_FirstStage.fty[f] == 1) and (t + parameters_FirstStage.omega_fw[f] > parameters_FirstStage.hl)),
                        'Constraint_1.10b')
        
        model.addConstrs((decisionVariables_SecondStage.IDs_f_l_t[s,f,l,t] 
                        <= gp.quicksum(parameters_SecondStage.dp[s][f][l][t1] for t1 in range(t+1,t+parameters_FirstStage.omega_dc[f] + 1)) 
                        for s in S for f in F for l in L for t in T 
                        if (parameters_FirstStage.fty[f] == 1) and (t + parameters_FirstStage.omega_dc[f] <= parameters_FirstStage.hl)),
                        'Constraint_1.10c')

        model.addConstrs((decisionVariables_SecondStage.IDs_f_l_t[s,f,l,t] 
                        <= gp.quicksum((parameters_SecondStage.dp[s][f][l][t1]
                                        / parameters_FirstStage.omega_dc[f])
                                        * (t + parameters_FirstStage.omega_dc[f] - parameters_FirstStage.hl) for t1 in range(t - parameters_FirstStage.omega_dc[f] + 1, t)) 
                        + gp.quicksum(parameters_SecondStage.dp[s][f][l][t2] for t2 in range(t + 1, t + parameters_FirstStage.omega_dc[f]) if t2 <= parameters_FirstStage.hl) 
                        for s in S for f in F for l in L for t in T 
                        if (parameters_FirstStage.fty[f] == 1) and (t + parameters_FirstStage.omega_dc[f] > parameters_FirstStage.hl)),
                        'Constraint_1.10d')

        # Constraint 1.11: Shipments consolidation
        """ Shipments (Vi, l, t ) from the factory inventory to DCs l are consolidated into fresh and dry shipments with variables DVf, l, t according to
        their refrigerated transportation requirements.
        """

        model.addConstrs((decisionVariables_FirstStage.Vi_l_t[i,l,t] 
                        == gp.quicksum(decisionVariables_FirstStage.DVf_l_t[f,l,t] for f in F if parameters_FirstStage.fty[f] == i)
                        for i in FT for l in L for t in T),
                        'Constraint_1.11a')

        # Constraint 1.12: Required Number Of Trucks
        """ The volume shipped from factory inventory to DC l needs to be loaded in trucks. The number of required trucks (TRi, l, t ) is calculated
            in the following constraints. A shipment to a distribution center may require n trucks, only one of these n trucks is allowed to have less
            than a truck load tlmax and the minimum amount of cargo it can transport is given by parameter tlmin 
        """
        model.addConstrs( (decisionVariables_FirstStage.Vi_l_t[i, l, t] 
                            <= integerVariables.TRi_l_t[i, l, t] 
                            * parameters_FirstStage.tl_max 
                        for i in FT for l in L for t in T),
                        'Constraint_1.12a')
        
        model.addConstrs(( decisionVariables_FirstStage.Vi_l_t[i, l, t] 
                            >= (integerVariables.TRi_l_t[i, l, t] - 1)  
                            * parameters_FirstStage.tl_max 
                            + parameters_FirstStage.tl_min 
                        for i in FT for l in L for t in T),
                        'Constraint_1.12b')
        
        """ Every shipment from a factory warehouse to a DC must be planned to arrive within the horizon. For that, Vi, l, t must be set to zero every
            time t + τl > hl     Vi,l,t = 0, ∀i ∈ F T , l ∈ L, t ∈ (hl - τl + 1 )..hl : τl > 0 
        """
        model.addConstrs((decisionVariables_FirstStage.Vi_l_t[i, l, t] 
                        == 0 
                        for i in FT for l in L for t in (range(parameters_FirstStage.hl - parameters_FirstStage.tau[l] + 1, parameters_FirstStage.hl))
                        if parameters_FirstStage.tau[l] > 0),
                        'Constraint_1.12c')

        # Constraint 1.13: Exports lots
        """ Bounds for the number of lots to be exported for each family f on the horizon
        """

        model.addConstrs( (parameters_FirstStage.el_min[f] 
                        <= gp.quicksum(integerVariables.Ef_t[f, t] for t in T) 
                        for f in F),
                        'Constraint_1.13a')
        
        model.addConstrs( (gp.quicksum(integerVariables.Ef_t[f, t] for t in T) 
                        <= parameters_FirstStage.el_max[f] 
                        for f in F),
                        'Constraint_1.13b')

        return model

    def Run_Model(self, T, F, S, FT, MP, CT, L, scenarios):
        # Create a new model
        model = gp.Model("FirstStage")

        # get the needed parameters
        parameters_FirstStage = Parameters_FirstStage(T,F,S,FT,MP,CT,L)

        # get the needed decision variables
        decisionVariables_FirstStage = DecisionVariables_FirstStage(model, T, F, S, FT, MP, CT, L)

        # get the needed integer variables
        binaryVariables = BinaryVariables(model, T, F, S, FT, MP, CT, L)

        # get the needed integer variables
        integerVariables = IntegerVariables(model, parameters_FirstStage, T, F, S, FT, MP, CT, L)

        # get the needed second stage parameters
        parameters_SecondStage = Parameters_SecondStage(T, F, S, FT, MP, CT, L, scenarios)

        # get the needed decision variables for the second stage
        decisionVariables_SecondStage = DecisionVariables_SecondStage(model, T, F, S, FT, MP, CT, L)

        # Add the objective function

        model = self.Objective_Function(parameters_FirstStage, decisionVariables_FirstStage, parameters_SecondStage,
                                        decisionVariables_SecondStage, binaryVariables, integerVariables, model, T, F, S, FT, MP, CT, L)

        # Add the constraints
        model = self.Constraints(parameters_FirstStage, decisionVariables_FirstStage, parameters_SecondStage,
                                 decisionVariables_SecondStage, binaryVariables, integerVariables, model, T, F, S, FT, MP, CT, L)

        # Optimize model
        model.optimize()

        # Print the results
        #for v in model.getVars():
        #    print('%s %g' % (v.varName, v.x))

        #print('Attr:', model.printAttr('X'))
        print('model.status:', model.status)
        if model.status == GRB.Status.OPTIMAL:
            print('Obj: %g' % model.objVal)
        elif model.status == GRB.Status.INFEASIBLE:
                # find infeasibilities
            model.computeIIS()
            model.write("results/infeasible.ilp")
        

        # Save the model
        # Add timestamp to file name
        timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"results/result_FirstStage_LP_{timestamp}.lp"
        model.write(file_name)

        file_name = f"results/result_FirstStage_MPS_{timestamp}.mps"
        model.write(file_name)

        file_name = f"results/result_FirstStage_PRM_{timestamp}.prm"
        model.write(file_name)



