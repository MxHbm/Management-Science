#### Load necessary packages 

#### Import python scrips
from variables import *  #Werte für Parameter
#from gurobipy import * #Gurobi
import gurobipy as gp
import datetime as dt
from parameters import *   # All parameters

class Model:
    def __init__(self):
        pass

    def Objective_Function(self, data:Parameters, decisionVariables_FirstStage: DecisionVariables_FirstStage, 
                            decisionVariables_SecondStage: DecisionVariables_SecondStage, 
                            binaryVariables:BinaryVariables,integerVariables:IntegerVariables, model):

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
        decisionVariables_FirstStage.TCOST = (
                gp.quicksum(integerVariables.TR[i, l, t]           # for debugging
                            * data.tc[l][i] for i in data.FT for l in data.L for t in data.T) 
                + gp.quicksum(binaryVariables.Y[m, t] 
                            * data.sco for m in data.MP for t in data.T) 
                + gp.quicksum(data.rho[s] 
                            * (decisionVariables_SecondStage.RS[s, t] 
                                * data.rsc 
                                + decisionVariables_SecondStage.RO[s, t] 
                                * data.roc) 
                            for s in data.S for t in data.T))


        ''' The expected net benefit is obtained from income minus total costs. The incomes include from left to right, the export sales income, sales
            income, and overstock incomes. Overstock incomes are produced from selling at a reduced price by the quantity produced in overstock for
            each of families.'''
    
        # BENEFIT
        decisionVariables_FirstStage.EXI = ( 
                    gp.quicksum( data.re[f] 
                                * data.ls_p[f] 
                                * integerVariables.E[f, t]
                                for f in data.F for t in data.T)
                    + gp.quicksum(  data.rho[s]
                                    * (gp.quicksum(data.r[f] 
                                        * (data.dp[s][f][l][t] 
                                            - decisionVariables_SecondStage.SO[s, f, l, t])
                                        for l in data.L for f in data.F for t in data.T)
                                        + gp.quicksum(decisionVariables_SecondStage.OS[s, f, l, t] 
                                                        * data.rr[f]
                                        for l in data.L for f in data.F for t in data.T)
                                        )
                                    for s in data.S )
        ) 
    
        # EXPECTED NET BENEFIT
        model.setObjective(decisionVariables_FirstStage.EXI - decisionVariables_FirstStage.TCOST, GRB.MAXIMIZE)

        return model


    def Constraints(self, data:Parameters, decisionVariables_FirstStage: DecisionVariables_FirstStage,
                    decisionVariables_SecondStage: DecisionVariables_SecondStage,
                    binaryVariables:BinaryVariables, integerVariables:IntegerVariables, model):
        
        #pass
        ''' constraints: 
        '''
        
        # Constraint 1: Raw milk supply consumption
        """ The following constraints model raw milk inventory flow within the industrial complex. In some scenarios the purchase of raw milk to
            a third-party supplier (RSs, t) or its disposal (ROs, t) due to overstock may arise. For every scenario, dris, t is raw milk daily input (parameter)
            and RM (independent of scenarios) is the variable modeling the raw milk consumption of all plants in the complex. """
        model.addConstrs((decisionVariables_SecondStage.RI[s, t]
                        == data.r0
                        + gp.quicksum(data.dri[s][t1] for t1 in data.T if t1 <= t) 
                        - gp.quicksum(decisionVariables_FirstStage.RM[t1] for t1 in data.T if t1 <= t) 
                        + gp.quicksum(decisionVariables_SecondStage.RS[s,t1] for t1 in data.T if t1 <= t)
                        - gp.quicksum(decisionVariables_SecondStage.RO[s,t1] for t1 in data.T if t1 <= t)
                        for s in data.S for t in data.T),
                        'Constraint_1.1a')

        model.addConstrs((decisionVariables_SecondStage.RI[s,t] 
                        <= data.r_max 
                        for s in data.S for t in data.T),
                        'Constraint_1.1b')

        model.addConstrs((decisionVariables_FirstStage.RM[t] 
                        == gp.quicksum(decisionVariables_FirstStage.Q[m,t]/data.fy[m] for m in data.MP)         # just for debugging
                        for t in data.T),
                        'Constraint_1.1c')
        
        # Constraint 2: General production constraints
        """ Family f production of all plants in the complex is equal to the manufacturing output of plants producing f. """
        model.addConstrs((decisionVariables_FirstStage.FP[f,t] 
                        == gp.quicksum(decisionVariables_FirstStage.MO[m,t] for m in data.MP if data.mappingFtoM[f] == f)   # [maybe solved] see issue #41
                        for f in data.F for t in data.T),
                        'Constraint_1.2a')

        model.addConstrs((decisionVariables_FirstStage.MO[m,t] 
                        == (1 - data.beta[m]) 
                        * decisionVariables_FirstStage.Q[m,t-data.sigma[m]] 
                        for m in data.MP for t in data.T if t > data.sigma[m]),
                        'Constraint_1.2b')
        
        model.addConstrs((decisionVariables_FirstStage.MO[m,t] 
                        == (1 - data.beta[m]) 
                        * data.wp[m][t] 
                        for m in data.MP for t in data.T if t <= data.sigma[m]),
                        'Constraint_1.2c')

        # Constraint 3: Work-in-progress (WIP) inventory constraints
        """ Manufacturing products with σ m > 0 generate WIP inventory which is depleted by the volume of finished products in period t represented by the variable MOm, t. Parameter iwip0
            m represents inventory from the previous planning horizon at manufacturing plant m. """
        model.addConstrs((decisionVariables_FirstStage.IWIP[m,t] 
                        == data.iwip0[m]
                        + gp.quicksum(decisionVariables_FirstStage.Q[m,t1] for t1 in data.T if t1 <= t)
                        - gp.quicksum(decisionVariables_FirstStage.MO[m,t1] for t1 in data.T if t1 <= t)
                        for m in data.MP for t in data.T 
                        if data.sigma[m] > 0),
                        'Constraint_1.3a')
        
        # Constraint 4
        model.addConstrs((integerVariables.Z[m, t]
                        == decisionVariables_FirstStage.Z1[m, t] 
                        + decisionVariables_FirstStage.Z2[m, t] 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4a')
        
        model.addConstrs((decisionVariables_FirstStage.Z1[m, t]
                        <= data.zmax[m] * binaryVariables.R1[m, t] 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4b')
        
        model.addConstrs((decisionVariables_FirstStage.Z2[m, t]
                        <= data.zmax[m] 
                        * binaryVariables.R2[m, t] 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4c')
        
        model.addConstrs((binaryVariables.R1[m, t]
                        + binaryVariables.R2[m, t] 
                        == 1 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4d')
        
        model.addConstrs((binaryVariables.R1[m, 0]  #data.T = 1 -> Here in python it has to be t = 0
                        == 1 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4e')
        
        model.addConstrs((decisionVariables_FirstStage.Z1[m, t]
                        <= integerVariables.Z[m, t-1] 
                        for m in data.MP for t in data.T 
                        if t > 0 ),
                        'Constraint_1.4f') # t - 1
        
        model.addConstrs((decisionVariables_FirstStage.Z1[m, t]
                        >= binaryVariables.R1[m, t] 
                        * integerVariables.Z[m, t-1] 
                        for m in data.MP for t in data.T 
                        if t > 0),
                        'Constraint_1.4g') 
        
        model.addConstrs((decisionVariables_FirstStage.Aux[m, t]
                        <= integerVariables.Z[m, t-1] 
                        for m in data.MP for t in data.T 
                        if t > 0),
                        'Constraint_1.4h') 
        
        model.addConstrs((decisionVariables_FirstStage.Aux[m, t]
                        >= integerVariables.Z[m, t-1] 
                        - data.zmax[m] 
                            * (1 - binaryVariables.R1[m, t]) 
                        for m in data.MP for t in data.T 
                        if t > 0),
                        'Constraint_1.4i')
        
        model.addConstrs((decisionVariables_FirstStage.Aux[m, t]
                        <= integerVariables.Z[m, t] 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4j' )
        
        model.addConstrs((decisionVariables_FirstStage.Aux[m, t]
                        <= binaryVariables.R1[m, t] 
                        * data.zmax[m] 
                        for m in data.MP for t in data.T),
                        'Constraint_1.4k') 
        
        #Constraint 5: Length-based campaign
        """ The level of production capacity during a production campaign of a length-based plant is set """
        model.addConstrs(((decisionVariables_FirstStage.Q[m, t] 
                        / data.cmin[m]) 
                        <= integerVariables.Z[m, t] 
                        for m in data.MP for t in data.T 
                        if data.cty[m] == 0),
                        'Constraint_1.5a')
        
        model.addConstrs(((decisionVariables_FirstStage.Q[m, t] 
                        / data.cmax[m]) 
                        >= integerVariables.Z[m, t] 
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
        model.addConstrs((decisionVariables_FirstStage.A[m, t]  
                        <= decisionVariables_FirstStage.A[m, t-1] 
                        + integerVariables.Z[m, t] 
                        for m in data.MP for t in data.T 
                        if (t > 0) and (data.cty[m] == 0)),
                        'Constraint_1.5c')

        model.addConstrs((decisionVariables_FirstStage.A[m, t]  
                        >= decisionVariables_FirstStage.A[m, t-1]
                        + integerVariables.Z[m, t] 
                        - ((data.dmax[m]
                            / data.cmin[m] )
                            * binaryVariables.R2[m, t]) 
                        for m in data.MP for t in data.T 
                        if (t > 0) and (data.cty[m] == 0)),
                        'Constraint_1.5d')
        
        model.addConstrs((decisionVariables_FirstStage.A[m, t]  
                        >= integerVariables.Z[m, t] 
                        for m in data.MP for t in data.T 
                        if data.cty[m] == 0),
                        'Constraint_1.5e')
        
        model.addConstrs((decisionVariables_FirstStage.A[m, t]
                        <= (data.dmax[m]
                            / data.cmin[m]) 
                        for m in data.MP for t in data.T 
                        if (t > 0) and (data.cty[m] == 0)),
                        'Constraint_1.5f')
        
        """ Accumulated production at the beginning of the horizon. The following equations (constraints (29) and (30)) model the remaining quantity
        production for the special case of t = 1."""
        model.addConstrs((decisionVariables_FirstStage.A[m, 0]  ##data.T = 1 -> Here in python it has to be t = 0
                        <= integerVariables.Z[m, 0] 
                        for m in data.MP
                        if data.cty[m] == 0),
                        'Constraint_1.5g')
        
        model.addConstrs((decisionVariables_FirstStage.A[m, 0]  #data.T = 1 -> Here in python it has to be t = 0
                        <= (data.dmax[m]
                            / data.cmin[m]) 
                        for m in data.MP
                        if data.cty[m] == 0),
                        'Constraint_1.5h') 
        
        model.addConstrs((decisionVariables_FirstStage.A[m, 0]  #data.T = 1 -> Here in python it has to be t = 0
                        >= integerVariables.Z[m, 0] 
                        - ((data.dmax[m]
                            / data.cmin[m]) 
                            * binaryVariables.R2[m, 0]) 
                        for m in data.MP 
                        if data.cty[m] == 0),
                        'Constraint_1.5i') 

        #Constraint 6
        """ The level of production capacity during a production campaign for a shift scheduled plant is set in constraints (32) and (33). It is set
        according to the number of shifts defined by the production campaign indicator (Zm, t ). In these equations scm represents the production
        capacity of manufacturing plant m on one work shift. The parameter ism in (0,1] is the maximum portion of the capacity of a shift which
        can be idle.
        """
        model.addConstrs(((decisionVariables_FirstStage.Q[m, t] 
                        / data.sc[m])
                        <= integerVariables.Z[m, t] 
                        for m in data.MP for t in data.T 
                        if data.cty == 1),
                        'Constraint_1.6a')
        
        model.addConstrs((decisionVariables_FirstStage.Q[m, t] 
                        / (data.sc[m] 
                            * (1 - data.is_[m]))
                        >= integerVariables.Z[m, t] 
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
        model.addConstrs((integerVariables.Z[m, t-1] 
                        <= data.zmax[m] 
                        * (1 - binaryVariables.Y[m, t]) 
                        for m in data.MP for t in data.T 
                        if t > 0), "Constraint_1.7a")
        
        model.addConstrs((binaryVariables.R2[m,t] 
                        >= binaryVariables.Y[m,t] 
                        for m in data.MP for t in data.T), "Constraint_1.7b")
        
        model.addConstrs((binaryVariables.R2[m,t] 
                        - integerVariables.Z[m, t-1] 
                        <= binaryVariables.Y[m,t] 
                        for m in data.MP for t in data.T 
                        if t > 0), "Constraint_1.7c")
        
        model.addConstrs((integerVariables.Z[m, t - t1] 
                        <= data.zmax[m] 
                        * (1 - binaryVariables.Y[m,t]) 
                        for m in data.MP for t in data.T for t1 in range(data.alpha[m] - 1) 
                        if (data.alpha[m] > 0)  and (t - t1 >= 0)), "Constraint_1.7d")
        
        model.addConstrs((integerVariables.Z[m,t] 
                        <= 0 
                        for m in data.MP for t in data.T 
                        if t <= data.ost[m]), "Constraint_1.7e")

        #5.1.8. Factory inventory balances
        """ The following constraints model the filling of factory inventory with finished products and the shipments and exports that deplete this
        inventory."""

        model.addConstrs((decisionVariables_FirstStage.IF[f,t] 
                        == data.i_0_ft[f][t] 
                        + gp.quicksum(decisionVariables_FirstStage.FP[f,t1] for t1 in data.T if t1 <= t) 
                        - gp.quicksum(decisionVariables_FirstStage.DV[f,l,t1] for l in data.L for t1 in data.T if t1 <= t) 
                        - gp.quicksum(integerVariables.E[f,t1] * data.el[f] for t1 in data.T if t1 <= t) 
                        for f in data.F for t in data.T),
                        'Constraint_1.8')

        
        # Constraint 1.9: Inventory at DCs
        """A shipment departed from factory inventory at period t, arrives to a distribution center l at period (t + τl ), where τl is the lead time for
        l. Inventory at distribution centers is scenario dependent accordingly to future demand realization (dps, f, l, t). Possible inventory fluctuation
        due to understock and overstock quantities are represented by scenario variables SOs, f, l, t,OSs, f, l, t, respectively.
        """
        model.addConstrs((decisionVariables_SecondStage.ID[s,f,l,t] 
                        ==  data.i_0[f][l] 
                        + gp.quicksum(decisionVariables_FirstStage.DV[f,l,t1] for t1 in data.T if (t1+data.tau[l]) <= t)
                        - gp.quicksum(data.dp[s][f][l][t1] for t1 in data.T if t1 <= t) 
                        + gp.quicksum(decisionVariables_SecondStage.SO[s,f,l,t1] for t1 in data.T if t1 <= t) 
                        - gp.quicksum(decisionVariables_SecondStage.OS[s,f,l,t1] for t1 in data.T if t1 <= t)   # just for debugging
                        for s in data.S for f in data.F for l in data.L for t in data.T),
                        'Constraint_1.9a')
        

        # INDEX OF TAU WAS WRONG !! i INSTEAD OF l

        '''In any DC, fresh and dry warehouse size limitations may arise; this is modeled by constraint'''

        model.addConstrs((gp.quicksum(decisionVariables_SecondStage.ID[s,f,l,t] for f in data.F if data.fty[f] == i) 
                        <= data.imax[l][i] 
                        for s in data.S for l in data.L for i in data.FT for t in data.T),
                        'Constraint_1.9b')
        
        # RUNNING PARAMETER FOR data.T WAS MISSING!!! 

        # Constraint 1.10: Shelf life constraints
        """Shelf life constraints at FW. Based on the concept discussed above in subSection 4.2, the following two constraints are introduced into
        the planning model to enforce the shelf-life indirectly. This constraint ensures that a product family will be transported to the distribution
        centers before the end of its warehouse shelf-life. 
        """
        model.addConstrs((decisionVariables_FirstStage.IF[f,t] 
                        <= gp.quicksum(decisionVariables_FirstStage.DV[f,l,t1] for t1 in range(t+1,t+data.omega_fw[f] + 1) for l in data.L) 
                        for f in data.F for t in data.T 
                        if (data.fty[f] == 1) and (t + data.omega_fw[f] <= data.hl)),
                        'Constraint_1.10a')


        model.addConstrs((decisionVariables_FirstStage.IF[f,t] 
                        <= gp.quicksum((decisionVariables_FirstStage.DV[f,l,t1]
                                        / data.omega_fw[f])
                                        *(t + data.omega_fw[f] - data.hl) for t1 in range(t - data.omega_fw[f] + 1, t) for l in data.L) 
                        +  gp.quicksum(decisionVariables_FirstStage.DV[f,l,t2] for t2 in range(t + 1, t + data.omega_fw[f] + 1) for l in data.L if t2 <= data.hl) 
                        for f in data.F for t in data.T 
                        if (data.fty[f] == 1) and (t + data.omega_fw[f] > data.hl)),
                        'Constraint_1.10b')
        
        model.addConstrs((decisionVariables_SecondStage.ID[s,f,l,t] 
                        <= gp.quicksum(data.dp[s][f][l][t1] for t1 in range(t+1,t+data.omega_dc[f] + 1)) 
                        for s in data.S for f in data.F for l in data.L for t in data.T 
                        if (data.fty[f] == 1) and (t + data.omega_dc[f] <= data.hl)),
                        'Constraint_1.10c')

        model.addConstrs((decisionVariables_SecondStage.ID[s,f,l,t] 
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

        model.addConstrs((decisionVariables_FirstStage.V[i,l,t] 
                        == gp.quicksum(decisionVariables_FirstStage.DV[f,l,t] for f in data.F if data.fty[f] == i)
                        for i in data.FT for l in data.L for t in data.T),
                        'Constraint_1.11a')

        # Constraint 1.12: Required Number Of Trucks
        """ The volume shipped from factory inventory to DC l needs to be loaded in trucks. The number of required trucks (TRi, l, t ) is calculated
            in the following constraints. A shipment to a distribution center may require n trucks, only one of these n trucks is allowed to have less
            than a truck load tlmax and the minimum amount of cargo it can transport is given by parameter tlmin 
        """
        model.addConstrs( (decisionVariables_FirstStage.V[i, l, t] 
                            <= integerVariables.TR[i, l, t] 
                            * data.tl_max 
                        for i in data.FT for l in data.L for t in data.T),
                        'Constraint_1.12a')
        
        model.addConstrs(( decisionVariables_FirstStage.V[i, l, t] 
                            >= (integerVariables.TR[i, l, t] - 1)  
                            * data.tl_max 
                            + data.tl_min 
                        for i in data.FT for l in data.L for t in data.T),
                        'Constraint_1.12b')
        
        """ Every shipment from a factory warehouse to a DC must be planned to arrive within the horizon. For that, Vi, l, t must be set to zero every
            time t + τl > hl     Vi,l,t = 0, ∀i ∈ data.F data.T , l ∈ data.L, t ∈ (hl - τl + 1 )..hl : τl > 0 
        """
        model.addConstrs((decisionVariables_FirstStage.V[i, l, t] 
                        == 0 
                        for i in data.FT for l in data.L for t in (range(data.hl - data.tau[l] + 1, data.hl))
                        if data.tau[l] > 0),
                        'Constraint_1.12c')

        # Constraint 1.13: Exports lots
        """ Bounds for the number of lots to be exported for each family f on the horizon
        """

        model.addConstrs( (data.el_min[f] 
                        <= gp.quicksum(integerVariables.E[f, t] for t in data.T) 
                        for f in data.F),
                        'Constraint_1.13a')
        
        model.addConstrs( (gp.quicksum(integerVariables.E[f, t] for t in data.T) 
                        <= data.el_max[f] 
                        for f in data.F),
                        'Constraint_1.13b')

        return model

    def Run_Model(self, data, logger):
        # Create a new model
        model = gp.Model("FirstStage")

        # get the needed decision variables
        decisionVariables_FirstStage = DecisionVariables_FirstStage(model, data)

        # get the needed integer variables
        binaryVariables = BinaryVariables(model, data)

        # get the needed integer variables
        integerVariables = IntegerVariables(model, data)

        # get the needed decision variables for the second stage
        decisionVariables_SecondStage = DecisionVariables_SecondStage(model, data)

        # Add the objective function

        model = self.Objective_Function(data, decisionVariables_FirstStage,
                                        decisionVariables_SecondStage, binaryVariables, integerVariables, model)

        # Add the constraints
        model = self.Constraints(data, decisionVariables_FirstStage,
                                 decisionVariables_SecondStage, binaryVariables, integerVariables, model)

        # Optimize model
        model.setParam('MIPGap', 1)
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
        #             decisionVariables_SecondStage.SO[8,3,0,0].LB,
        #             decisionVariables_SecondStage.SO[8,3,0,0].UB,
        #             decisionVariables_SecondStage.SO[8,3,0,0].Obj,
        #             decisionVariables_SecondStage.SO[8,3,0,0].VType,
        #             decisionVariables_SecondStage.SO[8,3,0,0].VarName)

        
        # for k in decisionVariables_SecondStage.RS:
        #     logger.info('RS: %s', decisionVariables_SecondStage.RS[k].Obj)
        
        # for k in integerVariables.TR:
        #     logger.info('TR: %s', integerVariables.TR[k].Obj)

        # for k in decisionVariables_SecondStage.RO:
        #     logger.info('RO: %s', decisionVariables_SecondStage.RO[k].Obj)


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
        

        return model, logger



