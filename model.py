#### Load necessary packages 

#### Import python scrips
from variables import *  #Werte für Parameter
#from gurobipy import * #Gurobi
import gurobipy as gp
from gurobipy import GRB, quicksum, Model, abs_ 
import datetime as dt
import time as time
from parameters import *   # All parameters

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Model:
    def __init__(self):
        pass

    def Objective_Function(self, data:Parameters, vars:DecisionVariablesModel1, model: gp.Model):

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
                + gp.quicksum(vars.binary.Y[m, t,k] 
                            * data.sco for m in data.MP for t in data.T for k in range(data.dmax[m]) if data.cty[m] == 0) 
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
                                * data.el[f] 
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
                                    for s in data.S)
        ) 
    
        # EXPECTED NET BENEFIT
        model.setObjective(vars.first_stage.EXI - vars.first_stage.TCOST, GRB.MAXIMIZE)

        return model


    def Constraints(self, data:Parameters, vars:DecisionVariablesModel1, model: gp.Model):
        
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
                        'Constraint_1.1a-5')

        model.addConstrs((vars.second_stage.RI[s,t] 
                        <= data.r_max 
                        for s in data.S for t in data.T),
                        'Constraint_1.1b-6')

        model.addConstrs((vars.first_stage.RM[t] 
                        == gp.quicksum(vars.first_stage.Q[m,t]/data.fy[m] for m in data.MP)         
                        for t in data.T),
                        'Constraint_1.1c-7')
        
      # Constraint 2: General production constraints
        """ Family f production of all plants in the complex is equal to the manufacturing output of plants producing f. """
        model.addConstrs((vars.first_stage.FP[f,t] 
                        == vars.first_stage.MO[f,t]   # Product family is produced by plant m
                        for f in data.F for t in data.T),
                        'Constraint_1.2a-8')
        
        
        '''
            model.addConstrs((vars.first_stage.FP[f,t] 
                        == gp.quicksum(vars.first_stage.MO[m,t] for m in data.MP if m == f)   # Product family is produced by plant m
                        for f in data.F for t in data.T),
                        'Constraint_1.2a')
        '''
    
        '''
            model.addConstrs((vars.first_stage.FP[f,t] 
                        == gp.quicksum(vars.first_stage.MO[m,t] for m in data.MP if m == f)   # Product family is produced by plant m
                        for f in data.F for t in data.T),
                        'Constraint_1.2a')
        '''

        model.addConstrs((vars.first_stage.MO[m,t] 
                        == (1 - data.beta[m]) 
                        * vars.first_stage.Q[m,t - data.sigma[m]] 
                        for m in data.MP for t in data.T if t >= data.sigma[m]),
                        'Constraint_1.2b-9')
        
        model.addConstrs((vars.first_stage.MO[m,t] 
                        == (1 - data.beta[m]) 
                        * data.wp[m][t] 
                        for m in data.MP for t in data.T if t < data.sigma[m]),
                        'Constraint_1.2c-10')
        

        # Constraint 3: Work-in-progress (WIP) inventory constraints
        """ Manufacturing products with σ m > 0 generate WIP inventory which is depleted by the volume of finished products in period t represented by the variable MOm, t. Parameter iwip0
            m represents inventory from the previous planning horizon at manufacturing plant m. """
        
        ### SHOULD ONLY TAKE VALUES AT THE BEGININNG OF THE PLANNING HORIZON !!!
        '''
        model.addConstrs((vars.first_stage.IWIP[m,t] 
                        == data.iwip0[m]
                        + gp.quicksum(vars.first_stage.Q[m,t1] for t1 in data.T if t1 <= t)
                        - gp.quicksum(vars.first_stage.MO[m,t1] for t1 in data.T if t1 <= t)
                        for m in data.MP for t in data.T 
                        if data.sigma[m] > 0),
                        'Constraint_1.3a-11')
    '''
          # Constraint 4

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
                        if data.cty[m] == 1),
                        'Constraint_1.6a-32')
        
        ## DAMIT FUNKTIONIERT ES NICHT !!

        model.addConstrs(((vars.first_stage.Q[m, t] / data.sc[m]) * (1/(1 - data.is_[m]))
                >= vars.integer.Z[m, t] 
                for m in data.MP for t in data.T 
                if data.cty[m] == 1),
                'Constraint_1.6b-33')
        
        # Constraint 4                 
        '''
        model.addConstrs((vars.binary.R1[m, t]
                        + vars.binary.R2[m, t] 
                        == 1 
                        for m in data.MP for t in data.T if data.cty[m] == 0),
                        'Constraint_1.4d-15')
        
        model.addConstrs((vars.binary.R1[m, 0] 
                        == 1 
                        for m in data.MP if data.cty[m]==0),
                        'Constraint_1.4e-16')
        '''
         #Constraint 5: Length-based campaign
        """ The level of production capacity during a production campaign of a length-based plant is set """


        ### Changed symbols >= and <= !!!
        model.addConstrs(((vars.first_stage.Q[m, t] 
                        / data.cmin[m]) 
                        >= vars.integer.Z[m, t] 
                        for m in data.MP for t in data.T
                        if data.cty[m] == 0),
                        'Constraint_1.5a-23')
        
        model.addConstrs(((vars.first_stage.Q[m, t] 
                        / data.cmax[m]) 
                        <= vars.integer.Z[m, t] 
                        for m in data.MP for t in data.T
                        if data.cty[m] == 0),
                        'Constraint_1.5b-24')
        

          
        
        # Constraint 1.7: Campaign Setups
        """In order to model these features, the binary variable Ym, t is introduced. This variable takes value 1 when a new production campaign
        starts at t, if and only if R2m, t > 0 and Zm,t−1 = 0, which is ensured by constraints (34) - (35) – (36). We emphasize the redundancy of
        constraint (36) which was included to improve the computational performance of the family aggregated model.
        If at any period t, a production campaign for a manufacturing plant start (Ym,t = 1), then on periods t− t1 : t1 ∈ 0..(αm− 1) setup
        tasks may be required and therefore production is not allowed in these periods . In this way if Ym,t = 1 keeps Zm,t−t1 = 0 (there is no
        production) until finish the setup task (constraint (37)). Now for the special case that at the beginning of the horizon there is a setup task
        in progress, this is reflected in the parameter ostm > 0, constraint (38) keeping campaign indicator variable to 0 until the task is finished.
        """
        

        # Zusammenfassen als R2 >= abs(Zm-t - Zm-t-1) !!!
        '''
        model.addConstrs((vars.binary.R2[m, t] >=  vars.integer.Z[m, t-1] - vars.integer.Z[m, t]
                        for m in data.MP for t in data.T 
                        if (t > 0) and (data.cty[m] == 0)), "Constraint_1.7a-34")
        
        model.addConstrs((vars.binary.R2[m, t] >=  vars.integer.Z[m, t] - vars.integer.Z[m, t-1]
                        for m in data.MP for t in data.T 
                        if (t > 0) and (data.cty[m] == 0)), "Constraint_1.7a-34")
        '''
        #Ensure that R1 is 1 ewhen Zt-1 and Zt are equal
        '''
        model.addConstrs((vars.binary.R1[m, t] >=  1 - vars.integer.Z[m, t] - vars.integer.Z[m, t-1]
                        for m in data.MP for t in data.T 
                        if (t > 0) and (data.cty[m] == 0)), "Constraint_1.7a-34")
        
        model.addConstrs((vars.binary.R1[m, t] >=  (-1)*((1 - vars.integer.Z[m, t-1]) - vars.integer.Z[m, t])
                        for m in data.MP for t in data.T 
                        if (t > 0) and (data.cty[m] == 0)), "Constraint_1.7a-34")
        '''
        
        
        ####### NEW BECKER FORMULATION ########
        '''I want to find a lot of tuples (k,t') in a set Omega_t, which are defined as follows:
        if at time t the tuple k,t' could be active at time t, being active is defined as follows,
        that t' is the starting point and k is the duration. 
        '''
        
        # Z has to be 1 if one of the campaign is 1 in the past or now! 
        model.addConstrs((vars.integer.Z[m,t] 
                         <= gp.quicksum(vars.binary.Y[m, t_, k] for t_,k in data.big_phi[t]) 
                         for m in data.MP for t in data.T
                         if (data.cty[m] == 0)), "set_constraint_1")

        model.addConstrs((vars.integer.Z[m,t] 
                         <= 1 - gp.quicksum(vars.binary.Y[m, t_, k] for t_,k in data.big_theta[t]) 
                         for m in data.MP for t in data.T
                         if (data.cty[m] == 0)), "set_constraint_2")
        
        model.addConstrs((vars.binary.Y[m, t, k]
                         <= 1 - gp.quicksum(vars.binary.Y[m, t_, k_] for t_, k_ in data.big_omega[t][k]) 
                         for m in data.MP for t in data.T for k in range(data.dmax[m])
                         if (data.cty[m] == 0)), "set_constraint_2")
                        
      
        #5.1.8. Factory inventory balances
        """ The following constraints model the filling of factory inventory with finished products and the shipments and exports that deplete this
        inventory."""

        model.addConstrs((vars.first_stage.IF[f,t] 
                        == data.i_0_f[f]
                        + gp.quicksum(vars.first_stage.FP[f,t1] for t1 in data.T if t1 <= t) 
                        - gp.quicksum(vars.first_stage.DV[f,l,t1] for l in data.L for t1 in data.T if t1 <= t) 
                        - gp.quicksum(vars.integer.E[f,t1] * data.el[f] for t1 in data.T if t1 <= t) 
                        for f in data.F for t in data.T),
                        'Constraint_1.8-39')

        
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
                        - gp.quicksum(vars.second_stage.OS[s,f,l,t1] for t1 in data.T if t1 <= t) 
                        for s in data.S for f in data.F for l in data.L for t in data.T),
                        'Constraint_1.9a-40')
        

        '''In any DC, fresh and dry warehouse size limitations may arise; this is modeled by constraint'''

        model.addConstrs((gp.quicksum(vars.second_stage.ID[s,f,l,t] for f in data.F if data.fty[f] == i) 
                        <= data.imax[l][i] 
                        for s in data.S for l in data.L for i in data.FT for t in data.T),
                        'Constraint_1.9b-41')
        
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
                        'Constraint_1.10a-42')


        model.addConstrs((vars.first_stage.IF[f,t] 
                        <= gp.quicksum((vars.first_stage.DV[f,l,t1]
                                        / data.omega_fw[f])
                                        *(t + data.omega_fw[f] - data.hl) for t1 in range(t - data.omega_fw[f] + 1, t) for l in data.L) 
                        +  gp.quicksum(vars.first_stage.DV[f,l,t2] for t2 in range(t + 1, t + data.omega_fw[f] + 1) for l in data.L if t2 <= data.hl) 
                        for f in data.F for t in data.T 
                        if (data.fty[f] == 1) and (t + data.omega_fw[f] > data.hl)),
                        'Constraint_1.10b-43')
        
        model.addConstrs((vars.second_stage.ID[s,f,l,t] 
                        <= gp.quicksum(data.dp[s][f][l][t1] for t1 in range(t+1,t+data.omega_dc[f] + 1)) 
                        for s in data.S for f in data.F for l in data.L for t in data.T 
                        if (data.fty[f] == 1) and (t + data.omega_dc[f] <= data.hl)),
                        'Constraint_1.10c-44')

        model.addConstrs((vars.second_stage.ID[s,f,l,t] 
                        <= gp.quicksum((data.dp[s][f][l][t1]
                                        / data.omega_dc[f])
                                        * (t + data.omega_dc[f] - data.hl) for t1 in range(t - data.omega_dc[f] + 1, t)) 
                        + gp.quicksum(data.dp[s][f][l][t2] for t2 in range(t + 1, t + data.omega_dc[f]+1) if t2 <= data.hl) 
                        for s in data.S for f in data.F for l in data.L for t in data.T 
                        if (data.fty[f] == 1) and (t + data.omega_dc[f] > data.hl)),
                        'Constraint_1.10d-45')

        # Constraint 1.11: Shipments consolidation
        """ Shipments (Vi, l, t ) from the factory inventory to DCs l are consolidated into fresh and dry shipments with variables DVf, l, t according to
        their refrigerated transportation requirements.
        """

        model.addConstrs((vars.first_stage.V[i,l,t] 
                        == gp.quicksum(vars.first_stage.DV[f,l,t] for f in data.F if data.fty[f] == i)
                        for i in data.FT for l in data.L for t in data.T),
                        'Constraint_1.11a-46')

        # Constraint 1.12: Required Number Of Trucks
        """ The volume shipped from factory inventory to DC l needs to be loaded in trucks. The number of required trucks (TRi, l, t ) is calculated
            in the following constraints. A shipment to a distribution center may require n trucks, only one of these n trucks is allowed to have less
            than a truck load tlmax and the minimum amount of cargo it can transport is given by parameter tlmin 
        """
        model.addConstrs( (vars.first_stage.V[i, l, t] 
                            <= vars.integer.TR[i, l, t] 
                            * data.tl_max 
                        for i in data.FT for l in data.L for t in data.T),
                        'Constraint_1.12a-47')
        
        model.addConstrs((vars.first_stage.V[i, l, t] 
                            >= (vars.integer.TR[i, l, t] - 1)  
                            * data.tl_max 
                            + data.tl_min 
                        for i in data.FT for l in data.L for t in data.T),
                        'Constraint_1.12b-48')
        
        """ Every shipment from a factory warehouse to a DC must be planned to arrive within the horizon. For that, Vi, l, t must be set to zero every
            time t + τl > hl     Vi,l,t = 0, ∀i ∈ data.F data.T , l ∈ data.L, t ∈ (hl - τl + 1 )..hl : τl > 0 
        """
        model.addConstrs((vars.first_stage.V[i, l, t] 
                        == 0 
                        for i in data.FT for l in data.L for t in (range(data.hl - data.tau[l] + 1, data.hl))
                        if data.tau[l] > 0),
                        'Constraint_1.12c-49')

        # Constraint 1.13: Exports lots
        """ Bounds for the number of lots to be exported for each family f on the horizon
        """

        model.addConstrs( (data.el_min[f]
                        <= gp.quicksum(vars.integer.E[f, t] for t in data.T) 
                        for f in data.F),
                        'Constraint_1.13-50a')
        
        model.addConstrs( (gp.quicksum(vars.integer.E[f, t] for t in data.T) 
                        <= data.el_max[f] 
                        for f in data.F),
                        'Constraint_1.13-50b')
        

        ## NEw Constraint Maximum INventtory

        #model.addConstrs(vars.first_stage.IF[f,t] <= 5000 for f in data.F for t in data.T)

        return model
        
    def Calculate_emvp(self, data:S_star,  logger):
        print('============================ Calculate EMVP ============================')
        logger.info('============================ Calculate EMVP ============================')

        # Step 1: Calculate s*
        # this is done in class S_star
        # S_star calculates the mean value of the second stage parameters


        #data.s_star = s_star.s_star
        #logger.info(f's_star: {data.s_star}')

        #scenarios, probabilities = data.S, data.rho

        # Step 2: Solve the planning model using s*
        mvp_solution, logger = self.Run_Model(data, logger, 'MVP')
        mvp_solution_obj = mvp_solution.ObjVal

        # Step 3: Calculate optimal second stage reactions for each scenario
        emvp_solution, logger = self.Run_Detailed_Model(data, mvp_solution, logger, 'EMVP')
        emvp_solution_obj = emvp_solution.ObjVal

        # Extract objective values from Gurobi models
        #optimal_objective_values = [emvp_solution.ObjVal]

        # Step 4: Calculate EMVP
        #emvp = sum(obj_val * prob for obj_val, prob in zip(optimal_objective_values, probabilities))

        logger.info(f'mvp: {mvp_solution_obj}')
        logger.info(f'emvp: {emvp_solution_obj}')

        return emvp_solution_obj, emvp_solution, mvp_solution, logger
    

    
    def Run_Model(self, data:Parameters, logger, model_type='FAM'):

        logger.info('============================ Run Model ============================')
        # Create a new model
        model = gp.Model("first_stage")

        # get the needed decision variables
        #vars = DecisionVariables(model, data)
        vars = DecisionVariablesModel1(model, data)

        # Add the objective function
        model = self.Objective_Function(data, vars, model)

        # Add the constraints
        model = self.Constraints(data, vars, model)

        # Optimize model
        #Sets MipGap to 5% and TimeLimit to 60 seconds
        model.setParam('MIPGap', 0.05)
        model.setParam('TimeLimit', 60)

        # Adaptions to get more preciose results and less floats
        # model.setParam('NumericalFocus', 2)
        # model.setParam('IntFeasTol', 1e-9)
        # model.setParam('FeasibilityTol', 1e-9)
        # model.setParam('OptimalityTol', 1e-9)

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
        print(f'model.status: {model.status}')
        print(f'model.getObjective().getValue(): {model.getObjective().getValue()}')



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
        
        #self.plot_constraints_and_vars(logger, model, 'family_aggregated_model')
        self.create_table_of_ZRA(data, model, model_type)
        
        return model, logger
    
    def Detailed_Constraints(self, data:Parameters, vars:DecisionVariablesModel2, model: gp.Model, FP: list[list[float]], E: list[list[int]]):
        
        # WAS SOLLEN DIESE CONSTRAINTS MACHEN??
        # WELCHE VARIABLEN BRAUCHEN WIR DAFÜR?
        
        # Constraint 53: Translating familiys to products
        """ In the following constraints, for every product p, flyp accounts for product p family. Manufacturing of products from any family f is
            constrained to the production level previously set in the Family Aggregated Model"""
        
        model.addConstrs((FP[f][t] 
                          == gp.quicksum(vars.first_stage.PD[p,t] for p in data.P if data.fly[p] == f)
                        for f in data.F for t in data.T ),
                        'Constraint_53')
        

        # Constraint 54: export level of products
        '''Export levels for familyf products (Ef, t) defined in the Family Aggregated model define the export levels for every product in the Detailed
           Planning model.
        '''

        model.addConstrs((data.el[f] 
                          * E[f][t] 
                          == gp.quicksum(vars.first_stage.ED[p,t] * data.ls[p] for p in data.P if data.fly[p]== f) 
                        for f in data.F for t in data.T),
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
                        data.id0_FW[p]
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
                    <= gp.quicksum(vars.first_stage.PS[p,l,t1] for t1 in range(t+1,t+data.omega_fw[data.fly[p]] + 1) for l in data.L) 
                    for t in data.T for p in data.P
                    if (data.fty[data.fly[p]] == 1) and (t + data.omega_fw[data.fly[p]] <= data.hl)),
                    'Constraint_57')

        model.addConstrs((vars.first_stage.IFD[p,t] 
                    <= gp.quicksum((vars.first_stage.PS[p,l,t1]
                                    / data.omega_fw[data.fly[p]])
                                    *(t + data.omega_fw[data.fly[p]] - data.hl) for t1 in range(t - data.omega_fw[data.fly[p]] + 1, t) for l in data.L) 
                    +  gp.quicksum(vars.first_stage.PS[p,l,t2] for t2 in range(t + 1, t + data.omega_fw[data.fly[p]] + 1) for l in data.L if t2 <= data.hl) 
                    for t in data.T for p in data.P
                    if (data.fty[data.fly[p]] == 1) and (t + data.omega_fw[data.fly[p]] > data.hl)),
                    'Constraint_58')
        
        #Constraint 59
        """Distribution Centers shelf-life:"""
        
        # original constraint
        model.addConstrs((vars.second_stage.IDD[s,p,l,t] 
                         <= gp.quicksum(data.dpd[s][p][l][t1] for t1 in range(t+1,t+data.omega_dc[data.fly[p]] + 1)) 
                         for s in data.S for l in data.L for t in data.T for p in data.P
                         if (data.fty[data.fly[p]] == 1) and (t + data.omega_dc[data.fly[p]] <= data.hl)),
                         'Constraint_59')

        model.addConstrs((vars.second_stage.IDD[s,p,l,t] 
                    <= gp.quicksum((data.dpd[s][p][l][t1]
                                    / data.omega_dc[data.fly[p]])
                                    * (t + data.omega_dc[data.fly[p]] - data.hl) for t1 in range(t - data.omega_dc[data.fly[p]] + 1, t)) 
                    + gp.quicksum(data.dpd[s][p][l][t2] for t2 in range(t + 1, t + data.omega_dc[data.fly[p]]+1) if t2 <= data.hl) 
                    for s in data.S for l in data.L for t in data.T for p in data.P
                    if (data.fty[data.fly[p]] == 1) and (t + data.omega_dc[data.fly[p]] > data.hl)),
                    'Constraint_60')

        # Constraint 61... : Shipment to DCs
        """ 
            Family type (Fresh or Dry) i shipments to distribution center l on day t from factory to Distribution Centers are consolidated into fresh
            and dry shipments according to their refrigerated transportation requirements.
        """

        # original constraint
        model.addConstrs((vars.first_stage.VD[i,l,t] 
                        == gp.quicksum(vars.first_stage.PS[p,l,t] for p in data.P if (data.fty[data.fty_p[p]] == i))
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
        
        # new constraint - similar to constraint 49 - DO WE NEED THIS ??
        # model.addConstrs((vars.first_stage.VD[i, l, t] 
        #                 == 0 
        #                 for i in data.FT for l in data.L for t in (range(data.hl - data.tau[l] + 1, data.hl))
        #                 if data.tau[l] > 0),
        #                 'Constraint_64_new')

        '''In any DC, fresh and dry warehouse size limitations may arise; this is modeled by constraint'''

        model.addConstrs((gp.quicksum(vars.second_stage.IDD[s,p,l,t] for p in data.P if data.fty_p[p] == i) 
                        <= data.imax[l][i] 
                        for s in data.S for l in data.L for i in data.FT for t in data.T),
                        'Constraint_1.9b')

        return model
    
    def Detailed_Objective_Function(self, data:Parameters, vars:DecisionVariablesModel2, model: gp.Model):

        ''' The detailed planning model maximizes the expected net benefit (DENB), and is obtained as follows.
        '''

        # Costs
        vars.second_stage.COST = (
                    gp.quicksum(vars.integer.TRD[i, l, t] * data.tc[l][i] 
                                for i in data.FT for l in data.L for t in data.T
                                )
                            )


        # Return
        vars.second_stage.RETURN = ( 
                    gp.quicksum( data.re_p[p] 
                                * data.ls[p] 
                                * vars.first_stage.ED[p, t]
                                for p in data.P for t in data.T)
                    + gp.quicksum(data.rho[s]
                                    * (gp.quicksum(data.r_p[p] 
                                        * (data.dpd[s][p][l][t] 
                                            - vars.second_stage.SOD[s, p, l, t])
                                        for l in data.L for p in data.P for t in data.T)
                                        + gp.quicksum(vars.second_stage.OSD[s, p, l, t] 
                                                        * data.rr_p[p]
                                        for l in data.L for p in data.P for t in data.T)
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
        param_E = []

        for f in data.F:
            sub_params_FP = []
            sub_params_E = []
            for t in data.T:

                var_name_FP = "FPf_t[" + str(f) + "," + str(t) + "]"
                var_name_E = "Ef_t[" + str(f) + "," + str(t) + "]"
                sub_params_FP.append(gp_model.getVarByName(var_name_FP).X)
                sub_params_E.append(int(gp_model.getVarByName(var_name_E).X))
            
            param_FP.append(sub_params_FP)
            param_E.append(sub_params_E)

        
        #Debugging: Print the values of the fixed variables
        '''
        if 1 == 1:
            print("param_E")
            for f in  data.F:
                for t in data.T:
                    print(f, t, '\t', param_E[f][t])
                
                print("\n")

            print("param_FP")
            for f in  data.F:
                for t in data.T:
                    print(f, t, '\t', param_FP[f][t])
                
                print("\n")
        '''
        return param_FP, param_E

    def Run_Detailed_Model(self, data:Parameters, model_first_stage: gp.Model, logger, model_type='DPM'):


        # Get the needed fixed variable values from model 1
        param_FP, param_E = self.get_fixed_values(model_first_stage, data)

        #model_first_stage.reset()

        # Create a new model
        model = gp.Model("second_stage")

        # get the needed decision variables
        vars = DecisionVariablesModel2(model, data)

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
        print(f'model.status: {model.status}')

        # Print the values of all variables
        for v in model.getVars():
            if v.Obj != 0:
                #logger.info(f"{v.VarName} = {v.Obj}")
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

        #plot constraints and variables (bar chart, takes a lot of time)
        #self.plot_constraints_and_vars(logger, model, 'detailed_model')

        logger.info('Detailed Model finished')
        self.create_table_of_ZRA(data, model, model_type)

        return model, logger

    def plot_constraints_and_vars(self, logger, model, model_type='family_aggregated_model'):
        plot_time_start = time.process_time_ns()
        # self.display_constraints(logger, model, model_type)
        # self.display_vars(logger, model, model_type)

        combined_plots = [['R1', 'R2'], 
                          ['Z1', 'Z2'],
                          ['Zm', 'Y']]
        self.display_combined_plots(logger, model, model_type, combined_plots)
        plot_time_end = time.process_time_ns()
        logger.info(f'All plots saved in {(plot_time_end - plot_time_start) / (10**9)} seconds')

    def display_combined_plots(self, logger, model, model_type, combined_plots):
            
            for i, plot in enumerate(combined_plots):
                # Start time
                start_time = time.process_time_ns()
    
                # figure size
                plt.figure(figsize=(20, 10))
    
                # Plotting the variable values
                for p in plot:
                    names = []
                    values = []
                    for v in model.getVars():
                        if p in v.varName:
                            names.append(v.varName.split('[')[1])
                            values.append(v.X)
    
                    plt.bar(names, values)
    
                plt.xlabel('Variable')
                plt.ylabel('Value')
                plt.title(f'Combined Plots: {plot} ({model_type})')
                plt.xticks(rotation=90)
                plt.legend(plot)
                plt.tight_layout()
                # plt.show()
                file_name = f"results/{plot}-{model_type}.png"
                plt.savefig(file_name)
                plt.clf()
                plt.close()
    
                # End time
                end_time = time.process_time_ns()
    
                # Calculate elapsed time
                elapsed_time = (end_time - start_time) / (10**9)
    
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
            obj_values.append(v.X)

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
            plt.title(f'Variable Values {var} ({model_type})')
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
            plt.title(f'Constraint RHS Value: {constraint} ({model_type})')
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

    def create_table_of_ZRA(self, data:Parameters, model: gp.Model, model_type='FAM'):
        # time for fileName
        timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")
        timestamp += f'_{model_type}'

        if model_type in ['FAM', 'MVP']:
            # Create a table of the ZRA values
            table = []

            for m in data.MP:
                for t in data.T:
                    row = {}
                    row['m'] = m
                    row['t'] = t
                    row['Zm'] = model.getVarByName(f'Zm_t[{m},{t}]').X
                    # row['Z1m_t'] = model.getVarByName(f'Z1m_t[{m},{t}]').X
                    # row['Z2m_t'] = model.getVarByName(f'Z2m_t[{m},{t}]').X
                    row['Zm_t-1'] = model.getVarByName(f'Zm_t[{m},{t-1}]').X if t > 0 else np.nan
                    row['Am'] = model.getVarByName(f'Am_t[{m},{t}]').X
                    row['Am_t-1'] = model.getVarByName(f'Am_t[{m},{t-1}]').X if t > 0 else np.nan
                    # row['R1m'] = model.getVarByName(f'R1m_t[{m},{t}]').X
                    # row['R2m'] = model.getVarByName(f'R2m_t[{m},{t}]').X
                    # row['Ym_t'] = model.getVarByName(f'Ym_t[{m},{t},{data.dmax}]').X
                    # row['Auxm_t'] = model.getVarByName(f'Auxm_t[{m},{t}]').X
                    row['Qm_t'] = model.getVarByName(f'Qm_t[{m},{t}]').X
                    row['MOm_t'] = model.getVarByName(f'MOm_t[{m},{t}]').X
                    row['MOm_t>sigma'] = (1-data.beta[m]) * model.getVarByName(f'Qm_t[{m},{t-data.sigma[m]}]').X if t > data.sigma[m] else np.nan  
                    row['MOm_t<=sigma'] = (1-data.beta[m]) * data.wp[m][t] if t <= data.sigma[m] else np.nan  
                    row['iwip0m'] = data.iwip0[m]
                    row['IWIPm_t'] = model.getVarByName(f'IWIPm_t[{m},{t}]').X
                    row['FPf_t'] = model.getVarByName(f'FPf_t[{m},{t}]').X
                    row['i0f_fw'] = data.i_0_f[m]
                    row['IFm_t'] = model.getVarByName(f'IFf_t[{m},{t}]').X 

                    row['Zmax=Q/cmin'] = model.getVarByName(f'Qm_t[{m},{t}]').X / data.cmin[m]
                    row['Zmin=Q/cmax'] = model.getVarByName(f'Qm_t[{m},{t}]').X / data.cmax[m]

                    row['Qm_t/sc_m'] = model.getVarByName(f'Qm_t[{m},{t}]').X / data.sc[m] if data.sc[m] > 0 else np.nan
                    row['Qm_t/sc_m(1-ism)'] = model.getVarByName(f'Qm_t[{m},{t}]').X / (data.sc[m] * (1 - data.is_[m])) if data.sc[m] > 0 else np.nan
                    row['Qm_t/fym'] = model.getVarByName(f'Qm_t[{m},{t}]').X / data.fy[m] if data.fy[m] > 0 else np.nan
                    row['RM_t'] = model.getVarByName(f'RMt[{t}]').X 
                    row['dmax/cmin'] = data.dmax[m]/data.cmin[m]
                    # row['R2*dmax/cmin'] = model.getVarByName(f'R2m_t[{m},{t}]').X * data.dmax[m]/data.cmin[m]
                    row['zmax'] = data.zmax[m]
                    # row['zmax*(1-R1)'] = data.zmax[m] * (1 - model.getVarByName(f'R1m_t[{m},{t}]').X)
                    row['cmax'] = data.cmax[m]
                    row['cmin'] = data.cmin[m]

                    table.append(row)

            # table to df
            table = pd.DataFrame(table)
            table.to_csv(f'results/table_mt_{timestamp}.csv', index=False)

            table2 = []

            for f in data.F:
                for t in data.T:
                    row = {}
                    row['f'] = f
                    row['t'] = t

                    row['IFf_t'] = model.getVarByName(f'IFf_t[{f},{t}]').X
                    row['i_0f'] = data.i_0_f[f]
                    row['FPf_t'] = model.getVarByName(f'FPf_t[{f},{t}]').X

                    for l in data.L:
                        row[f'DVf_{l}_t'] = model.getVarByName(f'DVf_l_t[{f},{l},{t}]').X

                    row['Ef_t'] = model.getVarByName(f'Ef_t[{f},{t}]').X * data.el[f]

                    table2.append(row)

            table2 = pd.DataFrame(table2)
            table2.to_csv(f'results/table_flt_{timestamp}.csv', index=False)

            table2 = []

            for i in data.FT:
                for t in data.T:
                    row = {}
                    row['i'] = i
                    row['t'] = t


                    for l in data.L:
                        row[f'Vi_{l}_t'] = model.getVarByName(f'Vi_l_t[{i},{l},{t}]').X
                        row[f'TRi_{l}_t'] = model.getVarByName(f'TRi_l_t[{i},{l},{t}]').X


                    table2.append(row)

            table2 = pd.DataFrame(table2)
            table2.to_csv(f'results/table_ilt_{timestamp}.csv', index=False)


            # data for plotting 
            table = []
                
            for s in data.S:

                for t in data.T:
                    for f in data.F:
                        for l in data.L:
                            row = {}

                            row['f'] = f
                            row['l'] = l
                            row['s'] = s
                            row['t'] = t
                            
                            row['RM_t'] = model.getVarByName(f'RMt[{t}]').X
                            row[f'SAs_f_l_t'] = model.getVarByName(f'SAs_f_l_t[{s},{f},{l},{t}]').X
                            row[f'SOs_f_l_t'] = model.getVarByName(f'SOs_f_l_t[{s},{f},{l},{t}]').X
                            row[f'OSs_f_l_t'] = model.getVarByName(f'OSs_f_l_t[{s},{f},{l},{t}]').X
                    
                            row[f'RSs_t'] = model.getVarByName(f'RSs_t[{s},{t}]').X
                            row[f'ROs_t'] = model.getVarByName(f'ROs_t[{s},{t}]').X
                            row[f'RIs_t'] = model.getVarByName(f'RIs_t[{s},{t}]').X
                            table.append(row)

            # table to df
            table = pd.DataFrame(table)
            table.drop_duplicates(inplace=True)
            table.to_csv(f'results/plot_table_ts_{timestamp}.csv', index=False)


            # data for validation Objective Function
            table = []
                

            for t in data.T:
                for s in data.S:
                    row = {}

                    row['s'] = s
                    row['t'] = t
                
            
                    row[f'RSs_t'] = model.getVarByName(f'RSs_t[{s},{t}]').X
                    row[f'RSs_t*roc'] = model.getVarByName(f'RSs_t[{s},{t}]').X * data.roc
                    row[f'ROs_t'] = model.getVarByName(f'ROs_t[{s},{t}]').X
                    row[f'ROs_t*rsc'] = model.getVarByName(f'ROs_t[{s},{t}]').X * data.rsc

                    table.append(row)

                for f in data.F:
                    row = {}
                    row['f'] = f
                    row['t'] = t

                    row['Ef_t'] = model.getVarByName(f'Ef_t[{f},{t}]').X 
                    row['Ef_t*el'] = model.getVarByName(f'Ef_t[{f},{t}]').X * data.el[f]
                    row['Ef_t*el*ls'] = model.getVarByName(f'Ef_t[{f},{t}]').X * data.el[f] * data.ls[f]

                    row['FPf_t'] = model.getVarByName(f'FPf_t[{f},{t}]').X

                    table.append(row)


            # table to df
            table = pd.DataFrame(table)
            # 

            table.drop_duplicates(inplace=True)
            table.to_csv(f'results/validation_table_{timestamp}.csv', index=False)

        if model_type in ['DPM', 'EMVP']:
            pass

        #return table


