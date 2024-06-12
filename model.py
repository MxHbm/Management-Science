#### Load necessary packages 

#### Import python scrips
from variables import *  #Werte für Parameter
#from gurobipy import * #Gurobi
import gurobipy as gp
import datetime as dt
import time
from parameters import *   # All parameters

import matplotlib.pyplot as plt

class Model:
    def __init__(self):
        pass

    def Objective_Function(self, data:Parameters, vars:DecisionVariables, model: gp.Model):

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
        #TCOST = (
        vars.first_stage.TCOST = (
                gp.quicksum(vars.integer.TR[i, l, t]           # for debugging
                            * data.tc[l][i] for i in data.FT for l in data.L for t in data.T) 
                + gp.quicksum(vars.binary.Y[m, t] 
                            * data.sco for m in data.MP for t in data.T) 
                + gp.quicksum(data.rho[s] 
                            * (vars.second_stage.RS[s, t] 
                                * data.rsc 
                                + vars.second_stage.RO[s, t] 
                                * data.roc) 
                            for s in data.S for t in data.T))


        ''' The expected net benefit is obtained from income minus total costs. The incomes include from left to right, the export sales income, sales
            income, and overstock incomes. Overstock incomes are produced from selling at a reduced price by the quantity produced in overstock for
            each of families.'''
    
        # BENEFIT
        vars.first_stage.EXI = ( 
                    gp.quicksum( data.re[f] 
                                * data.ls[f] 
                                * vars.integer.E[f, t]
                                for f in data.F for t in data.T)
                    + gp.quicksum(  data.rho[s]
                                    * (gp.quicksum(data.r[f] 
                                        * (data.dp[s][f][l][t] 
                                            - vars.second_stage.SO[s, f, l, t])
                                        for l in data.L for f in data.F for t in data.T)
                                        + gp.quicksum(vars.second_stage.OS[s, f, l, t] 
                                                        * data.rr[f]
                                        for l in data.L for f in data.F for t in data.T)
                                        )
                                    for s in data.S )
        ) 
    
        # EXPECTED NET BENEFIT
        model.setObjective(vars.first_stage.EXI - vars.first_stage.TCOST, GRB.MAXIMIZE)

        return model


    def Constraints(self, data:Parameters, vars:DecisionVariables, model: gp.Model):
        
        #pass
        ''' constraints: 
        '''
        
        # Constraint 1: Raw milk supply consumption
        """ The following constraints model raw milk inventory flow within the industrial complex. In some scenarios the purchase of raw milk to
            a third-party supplier (RSs, t) or its disposal (ROs, t) due to overstock may arise. For every scenario, dris, t is raw milk daily input (parameter)
            and RM (independent of scenarios) is the variable modeling the raw milk consumption of all plants in the complex. """
        model.addConstrs((vars.second_stage.RI[s, t]
                        == data.r0
                        + gp.quicksum(data.dri[s][t1] for t1 in data.T if t1 <= t) 
                        - gp.quicksum(vars.first_stage.RM[t1] for t1 in data.T if t1 <= t) 
                        + gp.quicksum(vars.second_stage.RS[s,t1] for t1 in data.T if t1 <= t)
                        - gp.quicksum(vars.second_stage.RO[s,t1] for t1 in data.T if t1 <= t)
                        for s in data.S for t in data.T),
                        'Constraint_1.1a')

        model.addConstrs((vars.second_stage.RI[s,t] 
                        <= data.r_max 
                        for s in data.S for t in data.T),
                        'Constraint_1.1b')

        model.addConstrs((vars.first_stage.RM[t] 
                        == gp.quicksum(vars.first_stage.Q[m,t]/data.fy[m] for m in data.MP)         # just for debugging
                        for t in data.T),
                        'Constraint_1.1c')
        
        # Constraint 2: General production constraints
        """ Family f production of all plants in the complex is equal to the manufacturing output of plants producing f. """
        model.addConstrs((vars.first_stage.FP[f,t] 
                        == gp.quicksum(vars.first_stage.MO[m,t] for m in data.MP if data.mappingFtoM[f] == f)   # [maybe solved] see issue #41
                        for f in data.F for t in data.T),
                        'Constraint_1.2a')

        model.addConstrs((vars.first_stage.MO[m,t] 
                        == (1 - data.beta[m]) 
                        *vars.first_stage.Q[m,t-data.sigma[m]] 
                        for m in data.MP for t in data.T if t > data.sigma[m]),
                        'Constraint_1.2b')
        
        model.addConstrs((vars.first_stage.MO[m,t] 
                        == (1 - data.beta[m]) 
                        * data.wp[m][t] 
                        for m in data.MP for t in data.T if t <= data.sigma[m]),
                        'Constraint_1.2c')

        # Constraint 3: Work-in-progress (WIP) inventory constraints
        """ Manufacturing products with σ m > 0 generate WIP inventory which is depleted by the volume of finished products in period t represented by the variable MOm, t. Parameter iwip0
            m represents inventory from the previous planning horizon at manufacturing plant m. """
        model.addConstrs((vars.first_stage.IWIP[m,t] 
                        == data.iwip0[m]
                        + gp.quicksum(vars.first_stage.Q[m,t1] for t1 in data.T if t1 <= t)
                        - gp.quicksum(vars.first_stage.MO[m,t1] for t1 in data.T if t1 <= t)
                        for m in data.MP for t in data.T 
                        if data.sigma[m] > 0),
                        'Constraint_1.3a')
        
        # Constraint 4
        model.addConstrs((vars.integer.Z[m, t]
                        ==vars.first_stage.Z1[m, t] 
                        +vars.first_stage.Z2[m, t] 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4a')
        
        model.addConstrs((vars.first_stage.Z1[m, t]
                        <= data.zmax[m] * vars.binary.R1[m, t] 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4b')
        
        model.addConstrs((vars.first_stage.Z2[m, t]
                        <= data.zmax[m] 
                        * vars.binary.R2[m, t] 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4c')
        
        model.addConstrs((vars.binary.R1[m, t]
                        + vars.binary.R2[m, t] 
                        == 1 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4d')
        
        model.addConstrs((vars.binary.R1[m, 0]  #data.T = 1 -> Here in python it has to be t = 0
                        == 1 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4e')
        
        model.addConstrs((vars.first_stage.Z1[m, t]
                        <= vars.integer.Z[m, t-1] 
                        for m in data.MP for t in data.T 
                        if t > 0 ),
                        'Constraint_1.4f') # t - 1
        
        model.addConstrs((vars.first_stage.Z1[m, t]
                        >= vars.binary.R1[m, t] 
                        * vars.integer.Z[m, t-1] 
                        for m in data.MP for t in data.T 
                        if t > 0),
                        'Constraint_1.4g') 
        
        model.addConstrs((vars.first_stage.Aux[m, t]
                        <= vars.integer.Z[m, t-1] 
                        for m in data.MP for t in data.T 
                        if t > 0),
                        'Constraint_1.4h') 
        
        model.addConstrs((vars.first_stage.Aux[m, t]
                        >= vars.integer.Z[m, t-1] 
                        - data.zmax[m] 
                            * (1 - vars.binary.R1[m, t]) 
                        for m in data.MP for t in data.T 
                        if t > 0),
                        'Constraint_1.4i')
        
        model.addConstrs((vars.first_stage.Aux[m, t]
                        <= vars.integer.Z[m, t] 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4j' )
        
        model.addConstrs((vars.first_stage.Aux[m, t]
                        <= vars.binary.R1[m, t] 
                        * data.zmax[m] 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4k') 
        
        #Constraint 5: Length-based campaign
        """ The level of production capacity during a production campaign of a length-based plant is set """
        model.addConstrs(((vars.first_stage.Q[m, t] 
                        / data.cmin[m]) 
                        <= vars.integer.Z[m, t] 
                        for m in data.MP for t in data.T 
                        if data.cty[m] == 0),
                        'Constraint_1.5a')
        
        model.addConstrs(((vars.first_stage.Q[m, t] 
                        / data.cmax[m]) 
                        >= vars.integer.Z[m, t] 
                        for m in data.MP for t in data.T 
                        if data.cty[m] == 0),
                        'Constraint_1.5b')
        
        """ In this type of campaigns, a variable Am, t accounts for accumulated production days at manufacturing plant m on day t. This accumula-
            tion (constraints (25) and (26)) continues until the current campaign ends. Parameter dmax
            m represents maximal value of Am, t . If a campaign        ends on day t, then the mandatory accumulation of production on day t + 1 (i.e. Am,t+1 ) is relaxed (constraint (26)). This allows to set the
            accumulator variable in a new campaign to zero in a posterior campaign. In these equations the Boolean variable R2m, t (previously de-
            fined), is used to model the start or end of a length-based campaign. Constraints (27) and (28) define upper and lower bounds for Am, t .
            The quotient dmax_m / cmin_m, represents the maximum number of campaigns that might take place for manufacturing plant m within the current
            planning horizon"
        """
        model.addConstrs((vars.first_stage.A[m, t]  
                        <=vars.first_stage.A[m, t-1] 
                        + vars.integer.Z[m, t] 
                        for m in data.MP for t in data.T 
                        if (t > 0) and (data.cty[m] == 0)),
                        'Constraint_1.5c')

        model.addConstrs((vars.first_stage.A[m, t]  
                        >=vars.first_stage.A[m, t-1]
                        + vars.integer.Z[m, t] 
                        - ((data.dmax[m]
                            / data.cmin[m] )
                            * vars.binary.R2[m, t]) 
                        for m in data.MP for t in data.T 
                        if (t > 0) and (data.cty[m] == 0)),
                        'Constraint_1.5d')
        
        model.addConstrs((vars.first_stage.A[m, t]  
                        >= vars.integer.Z[m, t] 
                        for m in data.MP for t in data.T 
                        if data.cty[m] == 0),
                        'Constraint_1.5e')
        
        model.addConstrs((vars.first_stage.A[m, t]
                        <= (data.dmax[m]
                            / data.cmin[m]) 
                        for m in data.MP for t in data.T 
                        if (t > 0) and (data.cty[m] == 0)),
                        'Constraint_1.5f')
        
        """ Accumulated production at the beginning of the horizon. The following equations (constraints (29) and (30)) model the remaining quantity
        production for the special case of t = 1."""
        model.addConstrs((vars.first_stage.A[m, 0]  ##data.T = 1 -> Here in python it has to be t = 0
                        <= vars.integer.Z[m, 0] 
                        for m in data.MP
                        if data.cty[m] == 0),
                        'Constraint_1.5g')
        
        model.addConstrs((vars.first_stage.A[m, 0]  #data.T = 1 -> Here in python it has to be t = 0
                        <= (data.dmax[m]
                            / data.cmin[m]) 
                        for m in data.MP
                        if data.cty[m] == 0),
                        'Constraint_1.5h') 
        
        model.addConstrs((vars.first_stage.A[m, 0]  #data.T = 1 -> Here in python it has to be t = 0
                        >= vars.integer.Z[m, 0] 
                        - ((data.dmax[m]
                            / data.cmin[m]) 
                            * vars.binary.R2[m, 0]) 
                        for m in data.MP 
                        if data.cty[m] == 0),
                        'Constraint_1.5i') 

        #Constraint 6
        """ The level of production capacity during a production campaign for a shift scheduled plant is set in constraints (32) and (33). It is set
        according to the number of shifts defined by the production campaign indicator (Zm, t ). In these equations scm represents the production
        capacity of manufacturing plant m on one work shift. The parameter ism in (0,1] is the maximum portion of the capacity of a shift which
        can be idle.
        """
        model.addConstrs(((vars.first_stage.Q[m, t] 
                        / data.sc[m])
                        <= vars.integer.Z[m, t] 
                        for m in data.MP for t in data.T 
                        if data.cty == 1),
                        'Constraint_1.6a')
        
        model.addConstrs((vars.first_stage.Q[m, t] 
                        / (data.sc[m] 
                            * (1 - data.is_[m]))
                        >= vars.integer.Z[m, t] 
                        for m in data.MP for t in data.T 
                        if data.cty == 1),
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
        model.addConstrs((vars.integer.Z[m, t-1] 
                        <= data.zmax[m] 
                        * (1 - vars.binary.Y[m, t]) 
                        for m in data.MP for t in data.T 
                        if t > 0), "Constraint_1.7a")
        
        model.addConstrs((vars.binary.R2[m,t] 
                        >= vars.binary.Y[m,t] 
                        for m in data.MP for t in data.T), "Constraint_1.7b")
        
        model.addConstrs((vars.binary.R2[m,t] 
                        - vars.integer.Z[m, t-1] 
                        <= vars.binary.Y[m,t] 
                        for m in data.MP for t in data.T 
                        if t > 0), "Constraint_1.7c")
        
        model.addConstrs((vars.integer.Z[m, t - t1] 
                        <= data.zmax[m] 
                        * (1 - vars.binary.Y[m,t]) 
                        for m in data.MP for t in data.T for t1 in range(data.alpha[m] - 1) 
                        if (data.alpha[m] > 0)  and (t - t1 >= 0)), "Constraint_1.7d")
        
        model.addConstrs((vars.integer.Z[m,t] 
                        <= 0 
                        for m in data.MP for t in data.T 
                        if t <= data.ost[m]), "Constraint_1.7e")

        #5.1.8. Factory inventory balances
        """ The following constraints model the filling of factory inventory with finished products and the shipments and exports that deplete this
        inventory."""

        model.addConstrs((vars.first_stage.IF[f,t] 
                        == data.i_0_f[f]
                        + gp.quicksum(vars.first_stage.FP[f,t1] for t1 in data.T if t1 <= t) 
                        - gp.quicksum(vars.first_stage.DV[f,l,t1] for l in data.L for t1 in data.T if t1 <= t) 
                        - gp.quicksum(vars.integer.E[f,t1] * data.el[f] for t1 in data.T if t1 <= t) 
                        for f in data.F for t in data.T),
                        'Constraint_1.8')

        
        # Constraint 1.9: Inventory at DCs
        """A shipment departed from factory inventory at period t, arrives to a distribution center l at period (t + τl ), where τl is the lead time for
        l. Inventory at distribution centers is scenario dependent accordingly to future demand realization (dps, f, l, t). Possible inventory fluctuation
        due to understock and overstock quantities are represented by scenario variables SOs, f, l, t,OSs, f, l, t, respectively.
        """
        model.addConstrs((vars.second_stage.ID[s,f,l,t] 
                        ==  data.i_0[f][l] 
                        + gp.quicksum(vars.first_stage.DV[f,l,t1] for t1 in data.T if (t1+data.tau[l]) <= t)
                        - gp.quicksum(data.dp[s][f][l][t1] for t1 in data.T if t1 <= t) 
                        + gp.quicksum(vars.second_stage.SO[s,f,l,t1] for t1 in data.T if t1 <= t) 
                        - gp.quicksum(vars.second_stage.OS[s,f,l,t1] for t1 in data.T if t1 <= t)   # just for debugging
                        for s in data.S for f in data.F for l in data.L for t in data.T),
                        'Constraint_1.9a')
        

        # INDEX OF TAU WAS WRONG !! i INSTEAD OF l

        '''In any DC, fresh and dry warehouse size limitations may arise; this is modeled by constraint'''

        model.addConstrs((gp.quicksum(vars.second_stage.ID[s,f,l,t] for f in data.F if data.fty[f] == i) 
                        <= data.imax[l][i] 
                        for s in data.S for l in data.L for i in data.FT for t in data.T),
                        'Constraint_1.9b')
        
        # RUNNING PARAMETER FOR data.T WAS MISSING!!! 

        # Constraint 1.10: Shelf life constraints
        """Shelf life constraints at FW. Based on the concept discussed above in subSection 4.2, the following two constraints are introduced into
        the planning model to enforce the shelf-life indirectly. This constraint ensures that a product family will be transported to the distribution
        centers before the end of its warehouse shelf-life. 
        """
        model.addConstrs((vars.first_stage.IF[f,t] 
                        <= gp.quicksum(vars.first_stage.DV[f,l,t1] for t1 in range(t+1,t+data.omega_fw[f] + 1) for l in data.L) 
                        for f in data.F for t in data.T 
                        if (data.fty[f] == 1) and (t + data.omega_fw[f] <= data.hl)),
                        'Constraint_1.10a')


        model.addConstrs((vars.first_stage.IF[f,t] 
                        <= gp.quicksum((vars.first_stage.DV[f,l,t1]
                                        / data.omega_fw[f])
                                        *(t + data.omega_fw[f] - data.hl) for t1 in range(t - data.omega_fw[f] + 1, t) for l in data.L) 
                        +  gp.quicksum(vars.first_stage.DV[f,l,t2] for t2 in range(t + 1, t + data.omega_fw[f] + 1) for l in data.L if t2 <= data.hl) 
                        for f in data.F for t in data.T 
                        if (data.fty[f] == 1) and (t + data.omega_fw[f] > data.hl)),
                        'Constraint_1.10b')
        
        model.addConstrs((vars.second_stage.ID[s,f,l,t] 
                        <= gp.quicksum(data.dp[s][f][l][t1] for t1 in range(t+1,t+data.omega_dc[f] + 1)) 
                        for s in data.S for f in data.F for l in data.L for t in data.T 
                        if (data.fty[f] == 1) and (t + data.omega_dc[f] <= data.hl)),
                        'Constraint_1.10c')

        model.addConstrs((vars.second_stage.ID[s,f,l,t] 
                        <= gp.quicksum((data.dp[s][f][l][t1]
                                        / data.omega_dc[f])
                                        * (t + data.omega_dc[f] - data.hl) for t1 in range(t - data.omega_dc[f] + 1, t)) 
                        + gp.quicksum(data.dp[s][f][l][t2] for t2 in range(t + 1, t + data.omega_dc[f]+1) if t2 <= data.hl) 
                        for s in data.S for f in data.F for l in data.L for t in data.T 
                        if (data.fty[f] == 1) and (t + data.omega_dc[f] > data.hl)),
                        'Constraint_1.10d')

        # Constraint 1.11: Shipments consolidation
        """ Shipments (Vi, l, t ) from the factory inventory to DCs l are consolidated into fresh and dry shipments with variables DVf, l, t according to
        their refrigerated transportation requirements.
        """

        model.addConstrs((vars.first_stage.V[i,l,t] 
                        == gp.quicksum(vars.first_stage.DV[f,l,t] for f in data.F if data.fty[f] == i)
                        for i in data.FT for l in data.L for t in data.T),
                        'Constraint_1.11a')

        # Constraint 1.12: Required Number Of Trucks
        """ The volume shipped from factory inventory to DC l needs to be loaded in trucks. The number of required trucks (TRi, l, t ) is calculated
            in the following constraints. A shipment to a distribution center may require n trucks, only one of these n trucks is allowed to have less
            than a truck load tlmax and the minimum amount of cargo it can transport is given by parameter tlmin 
        """
        model.addConstrs( (vars.first_stage.V[i, l, t] 
                            <= vars.integer.TR[i, l, t] 
                            * data.tl_max 
                        for i in data.FT for l in data.L for t in data.T),
                        'Constraint_1.12a')
        
        model.addConstrs((vars.first_stage.V[i, l, t] 
                            >= (vars.integer.TR[i, l, t] - 1)  
                            * data.tl_max 
                            + data.tl_min 
                        for i in data.FT for l in data.L for t in data.T),
                        'Constraint_1.12b')
        
        """ Every shipment from a factory warehouse to a DC must be planned to arrive within the horizon. For that, Vi, l, t must be set to zero every
            time t + τl > hl     Vi,l,t = 0, ∀i ∈ data.F data.T , l ∈ data.L, t ∈ (hl - τl + 1 )..hl : τl > 0 
        """
        model.addConstrs((vars.first_stage.V[i, l, t] 
                        == 0 
                        for i in data.FT for l in data.L for t in (range(data.hl - data.tau[l] + 1, data.hl))
                        if data.tau[l] > 0),
                        'Constraint_1.12c')

        # Constraint 1.13: Exports lots
        """ Bounds for the number of lots to be exported for each family f on the horizon
        """

        model.addConstrs( (data.el_min[f]
                        <= gp.quicksum(vars.integer.E[f, t] for t in data.T) 
                        for f in data.F),
                        'Constraint_1.13a')
        
        model.addConstrs( (gp.quicksum(vars.integer.E[f, t] for t in data.T) 
                        <= data.el_max[f] 
                        for f in data.F),
                        'Constraint_1.13b')

        return model

    def Run_Model(self, data:Parameters, logger):
        # Create a new model
        model = gp.Model("first_stage")

        # get the needed decision variables
        vars = DecisionVariables(model, data)

        # Add the objective function
        model = self.Objective_Function(data, vars, model)

        # Add the constraints
        model = self.Constraints(data, vars, model)

        # Optimize model
        model.setParam('MIPGap', 1)
        print('============================ Optimize Model ============================')
        model.optimize()

        # für jede Variable einzeln die Werte mit .X abfragen
        # unbeschränkte Variablen erkennenn
        # Upper Bounds ändenr
        # welche variablen haben einen positiven Zielkoeffizienten
        # Marge beim Verkauf von Milch muss Penalty sein., um Arbitrage zu vermeiden 

        #model.printAttr('X')

        #logger.info(model.printAttr('X'))

        # logger.info('rho: %s', data.rho)

        # logger.info("SO[8,3,0,0]: LB = %s, UB = %s, Obj = %s, VType = %s, VarName = %s",
        #             vars.second_stage.SO[8,3,0,0].LB,
        #             vars.second_stage.SO[8,3,0,0].UB,
        #             vars.second_stage.SO[8,3,0,0].Obj,
        #             vars.second_stage.SO[8,3,0,0].VType,
        #             vars.second_stage.SO[8,3,0,0].VarName)

        
        # for k in vars.second_stage.RS:
        #     logger.info('RS: %s', vars.second_stage.RS[k].Obj)
        
        # for k in vars.integer.TR:
        #     logger.info('TR: %s', vars.integer.TR[k].Obj)

        # for k in vars.second_stage.RO:
        #     logger.info('RO: %s', vars.second_stage.RO[k].Obj)


        logger.info(f'model.status: {model.status}')
        logger.info('rsc: %g', data.rsc)


        if model.status == 5:
            logger.warning("Model is unbounded")
        elif model.status == 2:
            logger.info("Optimal solution found")
            #for v in model.getVars():
            # for v in model.printAttr('X'):
            #     logger.info(f"{v.varName}: {v.x}")


            logger.info('Obj: %g' % model.objVal)

            # Save the model
            if 1 == 0:
                # Add timestamp to file name
                timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%data.S")
                file_name = f"results/result_FirstStage_LP_{timestamp}.lp"
                model.write(file_name)

                file_name = f"results/result_FirstStage_MPS_{timestamp}.mps"
                model.write(file_name)

                file_name = f"results/result_FirstStage_PRM_{timestamp}.prm"
                model.write(file_name)

        elif model.status == 4:
            logger.warning("Model is infeasible")

            try:
                model.computeIIS()
                model.write("results/infeasible.ilp")

            except gp.GurobiError as e:
                logger.error('Error Compute IIS: %s', e)
        else:
            logger.error("Optimization ended with status %s", model.status)
        
        self.plot_constraints_and_vars(logger, model, 'family_aggregated_model')
        return model, logger
    
    def Detailed_Constraints(self, data:Parameters, vars:DecisionVariables, model: gp.Model, FP: list[list[float]], E: list[list[int]]):
        
        # WAS SOLLEN DIESE CONSTRAINTS MACHEN??
        # WELCHE VARIABLEN BRAUCHEN WIR DAFÜR?
        
        # Constraint 53: Translating familiys to products
        """ In the following constraints, for every product p, flyp accounts for product p family. Manufacturing of products from any family f is
            constrained to the production level previously set in the Family Aggregated Model"""
        
        # NEED TO BE REVISED, MAYBE CHANGE THE SET PRODUCT TO 15 PRODUCTS BELONGING TO DIFFERERNT PRODUCT FAMILIES
        model.addConstrs((FP[f][t] 
                          == gp.quicksum(vars.first_stage.PD[p,t] for p in data.P if f == p)
                        for f in data.F for t in data.T ),
                        'Constraint_53')
        

        # Constraint 54: export level of products
        '''Export levels for familyf products (Ef, t) defined in the Family Aggregated model define the export levels for every product in the Detailed
           Planning model.
        '''
        model.addConstrs((data.el[f] 
                          * E[f][t] 
                          == gp.quicksum(vars.first_stage.ED[p,t] 
                                        * data.ls[p] for p in data.P if f == p)
                        for f in data.FT for t in data.T ),
                        'Constraint_54')
        
        # Constraint 55: Inventory Balance 
        '''
        Inventory balances in distribution centers. These restrictions are homologous to eq. (40) of the family aggregated model.
        '''

        model.addConstrs(
            (vars.second_stage.IDD[s, p, l, t]
                == data.id0[p][l]
                + gp.quicksum(vars.first_stage.PS[p,l,t1] for t1 in data.T if (t1 + data.tau[l]) <= t)
                - gp.quicksum(data.dpd[s][p][l][t1] for t1 in data.T if t1 <= t)
                + gp.quicksum(vars.second_stage.SOD[s,p,l,t1] for t1 in data.T if t1 <= t)
                - gp.quicksum(vars.second_stage.OSD[s,p,l,t1] for t1 in data.T if t1 <= t)
                for s in data.S for l in data.L for t in data.T for p in data.P),
                'Constraint_55')
                

        """ 
        Finished products inventory at the factory is determined by the fluctuations caused by product manufacturing, shipments, and exports.
        """

        model.addConstrs(
            (vars.first_stage.IFD[p,t] == 
                        data.i_0_f[p]
                        + gp.quicksum(vars.first_stage.PD[p,t1] for t1 in data.T if t1 <= t)
                        - gp.quicksum(vars.first_stage.PS[p,l,t1] for l in data.L for t1 in data.T if t1 <= t)
                        - gp.quicksum(vars.first_stage.ED[p,t1] * data.ls[p] for t1 in data.T if t1 <= t)
                        for p in data.P for t in data.T),
                        'Constraint_56')
        
        # Constraint 57: Shelf Life Balances
        ''' 
            Shelf-life considerations are included in the Detailed Planning model as well.
        '''
       
        model.addConstrs((vars.first_stage.IFD[p,t] 
                        <= gp.quicksum(vars.first_stage.PS[p,l,t1] for t1 in range(t+1,t+data.omega_fw[f] + 1) for l in data.L) 
                        for f in data.F for t in data.T for p in data.P
                        if (p == f) and (data.fty[f] == 1) and (t + data.omega_fw[f] <= data.hl)),
                        'Constraint_57')


        model.addConstrs((vars.first_stage.IFD[p,t] 
                        <= gp.quicksum((vars.first_stage.PS[p,l,t1]
                                        / data.omega_fw[f])
                                        *(t + data.omega_fw[f] - data.hl) for t1 in range(t - data.omega_fw[f] + 1, t) for l in data.L) 
                        +  gp.quicksum(vars.first_stage.DV[f,l,t2] for t2 in range(t + 1, t + data.omega_fw[f] + 1) for l in data.L if t2 <= data.hl) 
                        for f in data.F for t in data.T for p in data.P
                        if (p == f) and (data.fty[f] == 1) and (t + data.omega_fw[f] > data.hl)),
                        'Constraint_58')
        
        #Constraint 59
        """Distribution Centers shelf-life:"""
        
        model.addConstrs((vars.second_stage.IDD[s,p,l,t] 
                        <= gp.quicksum(data.dpd[s][p][l][t1] for t1 in range(t+1,t+data.omega_dc[f] + 1)) 
                        for s in data.S for f in data.F for l in data.L for t in data.T for p in data.P
                        if (f == p) and (data.fty[f] == 1) and (t + data.omega_dc[f] <= data.hl)),
                        'Constraint_59')

        model.addConstrs((vars.second_stage.IDD[s,p,l,t] 
                        <= gp.quicksum((data.dpd[s][p][l][t1]
                                        / data.omega_dc[f])
                                        * (t + data.omega_dc[f] - data.hl) for t1 in range(t - data.omega_dc[f] + 1, t)) 
                        + gp.quicksum(data.dpd[s][p][l][t2] for t2 in range(t + 1, t + data.omega_dc[f]+1) if t2 <= data.hl) 
                        for s in data.S for f in data.F for l in data.L for t in data.T for p in data.P
                        if (p == f) and (data.fty[f] == 1) and (t + data.omega_dc[f] > data.hl)),
                        'Constraint_60')

        # Constraint 61... : Shipment to DCs
        """ 
            Family type (Fresh or Dry) i shipments to distribution center l on day t from factory to Distribution Centers are consolidated into fresh
            and dry shipments according to their refrigerated transportation requirements.
        """

        model.addConstrs((vars.first_stage.VD[i,l,t] 
                        == gp.quicksum(vars.first_stage.PS[p,l,t] for p in data.P for f in data.F if (data.fty[f] == i) and (f == p))
                        for i in data.FT for l in data.L for t in data.T),
                        'Constraint_61')

        model.addConstrs((vars.first_stage.VD[i, l, t] 
                            <= vars.integer.TRD[i, l, t] 
                            * data.tl_max 
                        for i in data.FT for l in data.L for t in data.T),
                        'Constraint_62')
        
        model.addConstrs((vars.first_stage.VD[i, l, t] 
                            >= (vars.integer.TRD[i, l, t] - 1)  
                            * data.tl_max 
                            + data.tl_min 
                        for i in data.FT for l in data.L for t in data.T),
                        'Constraint_63')

        return model
    
    def Detailed_Objective_Function(self, data:Parameters, vars:DecisionVariables, model: gp.Model):

        ''' The detailed planning model maximizes the expected net benefit (DENB), and is obtained as follows.
        '''

        # Costs
        vars.second_stage.COST = (
                    gp.quicksum(vars.integer.TR[i, l, t] * data.tc[l][i] 
                                for i in data.FT for l in data.L for t in data.T
                                )
                            )


        # Return
        vars.second_stage.RETURN = ( 
                    gp.quicksum( data.re[f] 
                                * data.ls[f] 
                                * vars.integer.E[f, t]
                                for f in data.F for t in data.T)
                    + gp.quicksum(data.rho[s]
                                    * (gp.quicksum(data.r[f] 
                                        * (data.dp[s][f][l][t] 
                                            - vars.second_stage.SO[s, f, l, t])
                                        for l in data.L for f in data.F for t in data.T)
                                        + gp.quicksum(vars.second_stage.OS[s, f, l, t] 
                                                        * data.rr[f]
                                        for l in data.L for f in data.F for t in data.T)
                                        )
                                    for s in data.S )
        ) 

        # EXPECTED NET BENEFIT
        model.setObjective(vars.second_stage.RETURN - vars.second_stage.COST, GRB.MAXIMIZE)

        return model
    
    def get_fixed_values(self, gp_model : gp.Model, data:Parameters):
        ''' Retrieves the values from the previously solved gurobi model for variable E and FP'''

        # Get the fixed values from the model
        param_FP = []
        param_FP_UB = []
        param_FP_LB = []
        param_E = []
        param_E_UB = []
        param_E_LB = []
        for f in data.F:
            sub_params_FP = []
            sub_params_FP_UB = []
            sub_params_FP_LB = []
            sub_params_E = []
            sub_params_E_UB = []
            sub_params_E_LB = []
            for t in data.T:
                var_name_FP = "FPf_t[" + str(f) + "," + str(t) + "]"
                var_name_E = "Ef_t[" + str(f) + "," + str(t) + "]"
                sub_params_FP.append(gp_model.getVarByName(var_name_FP).X)
                sub_params_FP_UB.append(gp_model.getVarByName(var_name_FP).UB)
                sub_params_FP_LB.append(gp_model.getVarByName(var_name_FP).LB)
                sub_params_E.append(int(gp_model.getVarByName(var_name_E).X))
                sub_params_E_UB.append(gp_model.getVarByName(var_name_E).UB)
                sub_params_E_LB.append(gp_model.getVarByName(var_name_E).LB)
            
            param_FP.append(sub_params_FP)
            param_FP_UB.append(sub_params_FP_UB)
            param_FP_LB.append(sub_params_FP_LB)
            param_E.append(sub_params_E)
            param_E_UB.append(sub_params_E_UB)
            param_E_LB.append(sub_params_E_LB)

        if 1 == 1:
            print("param_E")
            for f in  data.F:
                for t in data.T:
                    print(f, t, '\t', param_E[f][t], "\tbounds:", param_E_LB[f][t], '...', param_E_UB[f][t])
                
                print("\n")
        
        if 1 == 0:
            print("param_FP")
            for f in  data.F:
                for t in data.T:
                    print(f, t, '\t', param_FP[f][t], "\tbounds:", param_FP_LB[f][t], '...', param_FP_UB[f][t])
                
                print("\n")
        if 1 == 0:

            print('data.P')
            print(data.P)

            print('data.F')
            print(data.F)

        return param_FP, param_E

    def Run_Detailed_Model(self, data:Parameters, model_first_stage: gp.Model, logger):
        # Create a new model
        model = gp.Model("second_stage")

        # get the needed decision variables
        vars = DecisionVariables(model, data)


        # Get the needed fixed variable values from model 1
        param_FP, param_E = self.get_fixed_values(model_first_stage, data)

        # Add the objective function
        model = self.Detailed_Objective_Function(data, vars, model)

        # Add the constraints
        model = self.Detailed_Constraints(data, vars, model, param_FP, param_E)

        # Optimize model
        model.setParam('MIPGap', 1)
        print('============================ Optimize Detailed Model ============================')

        # for debugging: set variable values
        for f in data.F:
            for t in data.T:
                #vars.first_stage.FP[f, t].setAttr('Obj', 5000)
                pass

        model.optimize()

        logger.info(f'=========== Detailed Model =================')
        logger.info(f'model.status: {model.status}')

        # Print the values of all variables
        for v in model.getVars():
            if v.Obj != 0:
                logger.info(f"{v.VarName} = {v.Obj}")
                pass

        # for p in data.P:
        #     for l in data.L:
        #         for t in data.T:
        #             for t1 in data.T :
        #                 if t1 + data.tau[l] <= t:
        #                     print(f'PS[{p},{l},{t1}]: {vars.first_stage.PS[p,l,t1]}' )
        #                     if vars.first_stage.PS[p,l,t1].X != 0:
        #                         try:
        #                             logger.info(f'PS[{p},{l},{t1}]: {vars.first_stage.PS[p,l,t1].X}' )
        #                         except:
        #                             logger.error(f'Error: PS[{p},{l},{t1}]')

        if model.status == 5:
            logger.warning("Model is unbounded")
        elif model.status == 2:
            logger.info("Optimal solution found")
            #for v in model.getVars():
            # for v in model.printAttr('X'):
            #     logger.info(f"{v.varName}: {v.x}")


            logger.info('Obj: %g' % model.objVal)

            # Save the model
            if 1 == 1:
                # Add timestamp to file name
                timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%data.S")
                file_name = f"results/result_FirstStage_LP_{timestamp}.lp"
                model.write(file_name)

                file_name = f"results/result_FirstStage_MPS_{timestamp}.mps"
                model.write(file_name)

                file_name = f"results/result_FirstStage_PRM_{timestamp}.prm"
                model.write(file_name)

        elif model.status == 4:
            logger.warning("Model is infeasible or unbounded.")

            try:
                print('============================ Compute IIS ============================')
                # model.setParam('DualReductions', 0)
                # model.reset()
                # model.optimize()
                # logger.info(f'model.status: {model.status}')
                model.computeIIS()
                model.write("results/infeasible-detailled.ilp")


            except gp.GurobiError as e:
                logger.error('Error Compute IIS: %s', e)


            # for v in model.getVars():
            #     if v.Obj != 0:
            #         logger.info(f"{v.varName}: {v.Obj}")

            #logger.info()
        else:
            logger.error("Optimization ended with status %s", model.status)

        # plot constraints and variables (bar chart, takes a lot of time)
        self.plot_constraints_and_vars(logger, model, 'detailed_model')

        logger.info('Detailed Model finished')

        return model, logger

    def plot_constraints_and_vars(self, logger, model, model_type='family_aggregated_model'):
        plot_time_start = time.process_time_ns()
        self.display_constraints(logger, model, model_type)
        self.display_vars(logger, model, model_type)
        plot_time_end = time.process_time_ns()
        logger.info(f'All plots saved in {plot_time_end - plot_time_start} seconds')
    
    def display_vars(self, logger, model, model_type):

        v_names = []
        v_names_split = []
        obj_values = []

        for v in model.getVars():
            #if ('FPf_t' in v.varName) or ('PDp_t' in v.varName) or ('EDp_t' in v.varName) or ('Ef_t' in v.varName):
            v_name = v.varName
            v_names.append(v_name)
            v_name_split = v_name.split('[')[0]  # Remove brackets from v name
            v_names_split.append(v_name_split)
            obj_values.append(v.Obj)

            #logger.info(f"{v.varName}: {v.Obj}")
            v_name = v.varName.split('[')[0]
        
        
        for i, var in enumerate(set(v_names_split)):
            # Start time
            start_time = time.process_time_ns()
                
            names = []
            values = []
            for name, val in zip(v_names, obj_values):
                if var in name:
                    names.append(name)
                    values.append(val)

            
            # figure size
            plt.figure(figsize=(20, 10))

            # Plotting the variable values
            plt.bar(names, values)
            plt.xlabel('Variable')
            plt.ylabel('Value')
            plt.title(f'Variable Values {var}')
            plt.xticks(rotation=90)
            plt.tight_layout()
            # plt.show()
            file_name = f"results/{var}-{model_type}.png"
            plt.savefig(file_name)
            plt.clf()
            plt.close()

            # End time
            end_time = time.process_time_ns()

            # Calculate elapsed time
            elapsed_time = (end_time - start_time) / (10**9)  # convert to seconds (1 ns = 10^-9 s)

            print(f"saved plot to {file_name} (plot {i+1}/{len(set(v_names_split))}) [{round(elapsed_time, 2)} seconds]")


    def display_constraints(self, logger, model, model_type):

        constraint_names = []
        constraint_names_split = []
        rhs_values = []

        for c in model.getConstrs():
            constraint_name = c.constrName
            constraint_names.append(constraint_name)
            constraint_name_split = constraint_name.split('[')[0]  # Remove brackets from constraint name
            constraint_names_split.append(constraint_name_split)
            rhs_values.append(c.RHS)

        print(set(constraint_names_split))

        for i, constraint in enumerate(set(constraint_names_split)):
            # Start time
            start_time = time.process_time_ns()

            # figure size
            plt.figure(figsize=(20, 10))

            names = []
            rhs_v = []
            for name, rhs in zip(constraint_names, rhs_values):
                if constraint in name:
                    names.append(name)
                    rhs_v.append(rhs)
                
            plt.bar(names, rhs_v)

            plt.xlabel('Constraint Name')
            plt.ylabel('RHS Value')
            plt.title(f'Constraint RHS Value: {constraint}')
            plt.xticks(rotation=90)
            plt.tight_layout()
            #plt.show()
            file_name = f"results/{constraint}-{model_type}.png"
            plt.savefig(file_name)
            plt.clf()
            plt.close()

            # End time
            end_time = time.process_time_ns()

            # Calculate elapsed time
            elapsed_time = (end_time - start_time) / (10**9)  # convert to seconds (1 ns = 10^-9 s)

            print(f"saved plot to {file_name} (plot {i+1}/{len(set(constraint_names_split))}) [{round(elapsed_time, 2)} seconds]")



